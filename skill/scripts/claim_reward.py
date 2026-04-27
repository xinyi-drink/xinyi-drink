#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from build_response import render_claim_result
from skill_config import load_config
from skill_http import SkillHttpError, build_url, fetch_json, make_debug_logger, post_json
from user_state import mark_activity_joined, mark_activity_not_joined, save_mobile


debug_log = make_debug_logger("claim_reward")


def main() -> int:
    parser = argparse.ArgumentParser(description="按手机号参与新一好喝活动并领取奖励")
    parser.add_argument("--mobile", required=True, help="用户手机号")
    parser.add_argument("--debug", action="store_true", help="输出调试信息到 stderr")
    args = parser.parse_args()

    config = load_config()
    base_url = config["apiBaseUrl"].rstrip("/")
    url = build_url(base_url, "/skill/xinyi/claim")
    debug_log(args.debug, f"posting claim request to {url}")
    save_mobile(args.mobile)

    try:
        parsed = post_json(url, config["timeoutSeconds"], {"mobile": args.mobile})
    except SkillHttpError as exc:
        sys.stdout.write(f"领取活动失败：{exc}")
        return 1

    if isinstance(parsed.get("data"), dict):
        parsed["data"].setdefault("requestedMobile", args.mobile)

    context_data = None
    if parsed.get("code") == 200:
        claim_data = parsed.get("data", {})
        if claim_data.get("user"):
            debug_log(args.debug, "user matched; saving mobile")
            if claim_data.get("kind") in {"granted", "already_claimed"}:
                mark_activity_joined(args.mobile)
            else:
                mark_activity_not_joined(args.mobile)
            context_url = build_url(
                base_url,
                "/skill/xinyi/context",
                {"mobile": args.mobile},
            )
            try:
                debug_log(args.debug, f"fetching context from {context_url}")
                context_response = fetch_json(
                    context_url,
                    config["timeoutSeconds"],
                )
                context_data = context_response.get("data", {})
                debug_log(
                    args.debug,
                    "context includes weather data" if context_data.get("weather") is not None else "context missing weather; using generic recommendation copy",
                )
            except SkillHttpError:
                debug_log(args.debug, "context enrichment failed; keep primary success message only")
                context_data = None
        else:
            mark_activity_not_joined(args.mobile)
            debug_log(args.debug, "user not found; marking activity as not joined")
    sys.stdout.write(render_claim_result(parsed.get("data", {}), context_data))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
