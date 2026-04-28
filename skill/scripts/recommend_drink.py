#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from build_response import render_recommendation_context, render_recommendation_unavailable
from skill_config import load_config
from skill_http import SkillHttpError, build_url, fetch_json, make_debug_logger
from user_state import (
    clear_mobile,
    load_activity_joined,
    load_mobile,
)


debug_log = make_debug_logger("recommend_drink")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="获取聚合推荐上下文，并整理成可直接提供给大模型的文本/表格"
    )
    parser.add_argument("--mobile", help="可选手机号，用于个性化推荐")
    parser.add_argument(
        "--use-saved-mobile",
        action="store_true",
        help="内部参数：仅在订单摘要或口味偏好等明确个性化场景复用本地手机号",
    )
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

    resolved_mobile = args.mobile
    if not resolved_mobile and args.use_saved_mobile:
        resolved_mobile = load_mobile()

    if args.mobile:
        debug_log(args.debug, "resolved mobile from cli argument")
    elif args.use_saved_mobile and resolved_mobile:
        debug_log(args.debug, "resolved mobile from local state")
    elif args.use_saved_mobile:
        debug_log(args.debug, "saved mobile requested but not found")
    else:
        debug_log(args.debug, "no mobile resolved; saved mobile not used")

    config = load_config()
    base_url = config["apiBaseUrl"].rstrip("/")
    timeout = config["timeoutSeconds"]

    context_url = build_url(
        base_url,
        "/skill/xinyi/context",
        {"mobile": resolved_mobile},
    )
    debug_log(args.debug, f"fetching context from {context_url}")
    try:
        context_response = fetch_json(context_url, timeout)
    except SkillHttpError as exc:
        sys.stdout.write(render_recommendation_unavailable(exc))
        return 0
    context_data = context_response.get("data", {})

    weather_data = context_data.get("weather")
    debug_log(
        args.debug,
        "context includes weather data" if weather_data is not None else "context missing weather; using generic recommendation copy",
    )

    rendered_context = render_recommendation_context(
        context={
            "mobile": resolved_mobile,
            "mobileFromStore": bool(resolved_mobile and args.use_saved_mobile and not args.mobile),
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
