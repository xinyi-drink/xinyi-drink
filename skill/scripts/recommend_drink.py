#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from activity_claim import (
    claim_data_from_response,
    claim_response_succeeded,
    is_joined_claim_kind,
)
from build_response import render_recommendation_context
from skill_config import load_config
from skill_http import SkillHttpError, build_url, fetch_json, make_debug_logger, post_json
from user_state import (
    clear_mobile,
    load_activity_joined,
    load_mobile,
    mark_activity_joined,
    mark_activity_not_joined,
)


debug_log = make_debug_logger("recommend_drink")


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

    config = load_config()
    base_url = config["apiBaseUrl"].rstrip("/")
    timeout = config["timeoutSeconds"]

    if resolved_mobile:
        claim_url = build_url(base_url, "/skill/xinyi/claim")
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
            claim_data = claim_data_from_response(claim_response)
            if claim_response_succeeded(claim_response) and claim_data.get("user"):
                debug_log(args.debug, "claim matched user")
                if is_joined_claim_kind(claim_data.get("kind")):
                    mark_activity_joined(resolved_mobile)
                else:
                    mark_activity_not_joined(resolved_mobile)
            elif claim_response_succeeded(claim_response) and claim_data:
                mark_activity_not_joined(resolved_mobile)
                debug_log(
                    args.debug,
                    "claim did not match user; continue with context lookup",
                )

    context_url = build_url(
        base_url,
        "/skill/xinyi/context",
        {"mobile": resolved_mobile},
    )
    debug_log(args.debug, f"fetching context from {context_url}")
    try:
        context_response = fetch_json(context_url, timeout)
    except SkillHttpError as exc:
        sys.stdout.write(f"获取推荐上下文失败：{exc}")
        return 1
    context_data = context_response.get("data", {})

    weather_data = context_data.get("weather")
    debug_log(
        args.debug,
        "context includes weather data" if weather_data is not None else "context missing weather; using generic recommendation copy",
    )

    rendered_context = render_recommendation_context(
        context={
            "mobile": resolved_mobile,
            "mobileFromStore": bool(resolved_mobile and not args.mobile),
            "preference": args.preference,
            "query": args.query,
            "scene": args.scene,
            "activityJoined": load_activity_joined(resolved_mobile),
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
