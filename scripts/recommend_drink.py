#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

from build_response import render_recommendation_context
from user_state import clear_mobile, load_mobile, save_mobile


def load_config() -> dict:
    config_path = Path(__file__).resolve().parents[1] / "config" / "defaults.json"
    return json.loads(config_path.read_text())


def fetch_json(url: str, timeout: int) -> dict:
    request = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_weather(base_url: str, timeout: int) -> dict | None:
    try:
        weather_response = fetch_json(f"{base_url}/skill/xinyi/weather", timeout)
    except Exception:
        return None

    weather_data = weather_response.get("data")
    return weather_data if isinstance(weather_data, dict) else None


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
    args = parser.parse_args()

    if args.clear_mobile:
        clear_mobile()

    resolved_mobile = args.mobile or load_mobile()
    if args.mobile:
        save_mobile(args.mobile)

    config = load_config()
    base_url = config["apiBaseUrl"].rstrip("/")

    query_suffix = ""
    if resolved_mobile:
        query_suffix = f"?mobile={resolved_mobile}"

    context_response = fetch_json(
        f"{base_url}/skill/xinyi/context{query_suffix}",
        config["timeoutSeconds"],
    )
    context_data = context_response.get("data", {})
    weather_data = fetch_weather(base_url, config["timeoutSeconds"])

    rendered_context = render_recommendation_context(
        context={
            "mobile": resolved_mobile,
            "mobileFromStore": bool(resolved_mobile and not args.mobile),
            "preference": args.preference,
            "query": args.query,
            "scene": args.scene,
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
