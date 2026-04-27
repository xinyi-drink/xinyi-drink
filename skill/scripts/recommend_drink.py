#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import urllib.request

from build_response import render_recommendation_context
from skill_config import load_config
from user_state import (
    clear_mobile,
    load_activity_joined,
    load_mobile,
    mark_activity_joined,
    mark_activity_not_joined,
    save_mobile,
)


def debug_log(enabled: bool, message: str) -> None:
    if enabled:
        print(f"DEBUG recommend_drink: {message}", file=sys.stderr)


def fetch_json(url: str, timeout: int) -> dict:
    request = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(url: str, timeout: int, payload: dict) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="获取聚合推荐上下文，并整理成可直接提供给大模型的文本/表格"
    )
    parser.add_argument("--mobile", help="可选手机号，用于个性化推荐")
    parser.add_argument(
        "--clear-mobile",
        action="store_true",
        help="清空已保存的手机号，下次不再自动带出",
    )
    parser.add_argument("--query", help="用户问题或饮品名称")
    parser.add_argument("--scene", help="场景，如提神、下午茶、轻负担")
    parser.add_argument("--preference", help="偏好，如咖啡、茶、低卡")
    parser.add_argument("--debug", action="store_true", help="输出调试信息到 stderr")
    args = parser.parse_args()

    if args.clear_mobile:
        clear_mobile()
        debug_log(args.debug, "cleared saved mobile")

    resolved_mobile = args.mobile or load_mobile()
    if args.mobile:
        debug_log(args.debug, "resolved mobile from cli argument")
    elif resolved_mobile:
        debug_log(args.debug, "resolved mobile from local state")
    else:
        debug_log(args.debug, "no mobile resolved")

    if args.mobile:
        save_mobile(args.mobile)
        debug_log(args.debug, "saved mobile from cli argument before claim lookup")

    config = load_config()
    base_url = config["apiBaseUrl"].rstrip("/")
    timeout = config["timeoutSeconds"]

    mobile_for_context = resolved_mobile
    if resolved_mobile:
        claim_url = f"{base_url}/skill/xinyi/claim"
        debug_log(args.debug, f"posting claim request to {claim_url}")
        try:
            claim_response = post_json(
                claim_url,
                timeout,
                {"mobile": resolved_mobile},
            )
        except Exception as exc:
            debug_log(
                args.debug,
                f"claim lookup failed; continue with context lookup and cached activity state: {exc}",
            )
        else:
            claim_data = claim_response.get("data", {})
            if claim_data.get("user"):
                debug_log(args.debug, "claim matched user")
                if claim_data.get("kind") in {"granted", "already_claimed"}:
                    mark_activity_joined(resolved_mobile)
                else:
                    mark_activity_not_joined(resolved_mobile)
            else:
                mark_activity_not_joined(resolved_mobile)
                debug_log(
                    args.debug,
                    "claim did not match user; keep saved mobile and continue with context lookup",
                )

    query_suffix = ""
    if mobile_for_context:
        query_suffix = f"?mobile={mobile_for_context}"

    context_url = f"{base_url}/skill/xinyi/context{query_suffix}"
    debug_log(args.debug, f"fetching context from {context_url}")
    context_response = fetch_json(context_url, timeout)
    context_data = context_response.get("data", {})

    weather_data = context_data.get("weather")
    debug_log(
        args.debug,
        "context includes weather data" if weather_data is not None else "context missing weather; using generic recommendation copy",
    )

    rendered_context = render_recommendation_context(
        context={
            "mobile": mobile_for_context,
            "mobileFromStore": bool(mobile_for_context and not args.mobile),
            "preference": args.preference,
            "query": args.query,
            "scene": args.scene,
            "activityJoined": load_activity_joined(mobile_for_context),
        },
        goods=context_data.get("goods", []),
        stores=context_data.get("stores", []),
        weather=weather_data,
        orders=context_data.get("orders"),
    )

    sys.stdout.write(rendered_context)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
