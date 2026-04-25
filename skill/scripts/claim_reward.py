#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

from build_response import render_claim_result
from user_state import save_mobile


def debug_log(enabled: bool, message: str) -> None:
    if enabled:
        print(f"DEBUG claim_reward: {message}", file=sys.stderr)


def load_config() -> dict:
    config_path = Path(__file__).resolve().parents[1] / "config" / "defaults.json"
    return json.loads(config_path.read_text())


def fetch_json(url: str, timeout: int) -> dict:
    request = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="按手机号参与新一好喝活动并领取奖励")
    parser.add_argument("--mobile", required=True, help="用户手机号")
    parser.add_argument("--debug", action="store_true", help="输出调试信息到 stderr")
    args = parser.parse_args()

    config = load_config()
    url = f"{config['apiBaseUrl'].rstrip('/')}/skill/xinyi/claim"
    debug_log(args.debug, f"posting claim request to {url}")
    payload = json.dumps({"mobile": args.mobile}).encode("utf-8")

    request = urllib.request.Request(
      url,
      data=payload,
      headers={"Content-Type": "application/json"},
      method="POST",
    )

    with urllib.request.urlopen(request, timeout=config["timeoutSeconds"]) as response:
        payload = response.read().decode("utf-8")
        parsed = json.loads(payload)
        context_data = None
        if parsed.get("code") == 200:
            claim_data = parsed.get("data", {})
            if claim_data.get("user"):
                debug_log(args.debug, "user matched; saving mobile")
                save_mobile(args.mobile)
                base_url = config["apiBaseUrl"].rstrip("/")
                try:
                    debug_log(args.debug, f"fetching context from {base_url}/skill/xinyi/context?mobile={args.mobile}")
                    context_response = fetch_json(
                        f"{base_url}/skill/xinyi/context?mobile={args.mobile}",
                        config["timeoutSeconds"],
                    )
                    context_data = context_response.get("data", {})
                    debug_log(
                        args.debug,
                        "context includes weather data" if context_data.get("weather") is not None else "context missing weather; using generic recommendation copy",
                    )
                except Exception:
                    debug_log(args.debug, "context enrichment failed; keep primary success message only")
                    context_data = None
            else:
                debug_log(args.debug, "user not found; skip saving mobile")
        sys.stdout.write(render_claim_result(parsed.get("data", {}), context_data))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
