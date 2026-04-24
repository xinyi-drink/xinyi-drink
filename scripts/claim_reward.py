#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

from build_response import render_claim_result
from user_state import save_mobile


def load_config() -> dict:
    config_path = Path(__file__).resolve().parents[1] / "config" / "defaults.json"
    return json.loads(config_path.read_text())


def fetch_json(url: str, timeout: int) -> dict:
    request = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_weather(base_url: str, timeout: int) -> dict | None:
    weather_response = fetch_json(f"{base_url}/skill/xinyi/weather", timeout)
    weather_data = weather_response.get("data")
    return weather_data if isinstance(weather_data, dict) else None


def main() -> int:
    parser = argparse.ArgumentParser(description="按手机号参与新一好喝活动并领取奖励")
    parser.add_argument("--mobile", required=True, help="用户手机号")
    args = parser.parse_args()

    config = load_config()
    url = f"{config['apiBaseUrl'].rstrip('/')}/skill/xinyi/claim"
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
            save_mobile(args.mobile)
            claim_data = parsed.get("data", {})
            if claim_data.get("user"):
                base_url = config["apiBaseUrl"].rstrip("/")
                context_response = fetch_json(
                    f"{base_url}/skill/xinyi/context?mobile={args.mobile}",
                    config["timeoutSeconds"],
                )
                context_data = context_response.get("data", {})
                weather_data = fetch_weather(base_url, config["timeoutSeconds"])
                if weather_data is not None:
                    context_data["weather"] = weather_data
        sys.stdout.write(render_claim_result(parsed.get("data", {}), context_data))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
