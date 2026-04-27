#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import urllib.request

from build_response import render_stores_section
from skill_config import load_config


def debug_log(enabled: bool, message: str) -> None:
    if enabled:
        print(f"DEBUG fetch_stores: {message}", file=sys.stderr)


def main() -> int:
    debug_enabled = "--debug" in sys.argv[1:]
    config = load_config()
    url = f"{config['apiBaseUrl'].rstrip('/')}/skill/xinyi/stores"
    debug_log(debug_enabled, f"fetching stores from {url}")

    with urllib.request.urlopen(url, timeout=config["timeoutSeconds"]) as response:
        payload = json.loads(response.read().decode("utf-8"))
        sys.stdout.write(render_stores_section(payload.get("data", {}).get("stores", [])))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
