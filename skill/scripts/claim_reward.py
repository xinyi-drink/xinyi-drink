#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from activity_claim import (
    claim_response_succeeded,
    is_joined_claim_kind,
    normalize_claim_data,
)
from build_response import render_claim_result
from skill_config import load_config
from skill_http import SkillHttpError, build_url, fetch_json, make_debug_logger, post_json
from user_state import (
    load_activity_joined,
    load_mobile,
    mark_activity_joined,
    mark_activity_not_joined,
)


debug_log = make_debug_logger("claim_reward")


def mask_mobile(mobile: str) -> str:
    if len(mobile) <= 7:
        return mobile
    return f"{mobile[:3]}****{mobile[-4:]}"


def render_session_claim_locked(saved_mobile: str) -> str:
    return (
        f"当前会话已使用手机号 {mask_mobile(saved_mobile)} 领取过 Skill用户大礼包，"
        "不能更换手机号重复领取。"
    )


def render_claim_app_error(response: dict) -> str | None:
    if claim_response_succeeded(response):
        return None

    message = str(response.get("message") or "").strip()
    if not message:
        return None

    return f"领取活动失败：{message}"


def main() -> int:
    parser = argparse.ArgumentParser(description="按手机号参与新一好喝活动并领取奖励")
    parser.add_argument("--mobile", required=True, help="用户手机号")
    parser.add_argument("--debug", action="store_true", help="输出调试信息到 stderr")
    args = parser.parse_args()

    saved_mobile = load_mobile()
    if (
        saved_mobile
        and saved_mobile != args.mobile
        and load_activity_joined(saved_mobile) is True
    ):
        debug_log(args.debug, "saved mobile already claimed; rejecting mobile switch")
        sys.stdout.write(render_session_claim_locked(saved_mobile))
        return 0

    config = load_config()
    base_url = config["apiBaseUrl"].rstrip("/")
    url = build_url(base_url, "/skill/xinyi/claim")
    debug_log(args.debug, f"posting claim request to {url}")
    previous_activity_joined = load_activity_joined(args.mobile)

    try:
        parsed = post_json(url, config["timeoutSeconds"], {"mobile": args.mobile})
    except SkillHttpError as exc:
        sys.stdout.write(f"领取活动失败：{exc}")
        return 1

    claim_error = render_claim_app_error(parsed)
    if claim_error:
        sys.stdout.write(claim_error)
        return 0

    claim_data = normalize_claim_data(parsed, args.mobile, previous_activity_joined)
    context_data = None
    if claim_response_succeeded(parsed) and claim_data:
        if claim_data.get("user"):
            debug_log(args.debug, "user matched; syncing activity state")
            if is_joined_claim_kind(claim_data.get("kind")):
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
                if context_data.get("weather") is not None:
                    debug_log(args.debug, "context includes weather data")
                else:
                    debug_log(
                        args.debug,
                        "context missing weather; using generic recommendation copy",
                    )
            except SkillHttpError:
                debug_log(args.debug, "context enrichment failed; keep primary success message only")
                context_data = None
        else:
            mark_activity_not_joined(args.mobile)
            debug_log(args.debug, "user not found; marking activity as not joined")
    render_data = claim_data if claim_response_succeeded(parsed) else {}
    sys.stdout.write(render_claim_result(render_data, context_data))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
