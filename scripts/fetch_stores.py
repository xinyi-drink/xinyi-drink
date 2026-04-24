#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

from build_response import render_stores_section


def load_config() -> dict:
    config_path = Path(__file__).resolve().parents[1] / "config" / "defaults.json"
    return json.loads(config_path.read_text())


def main() -> int:
    config = load_config()
    url = f"{config['apiBaseUrl'].rstrip('/')}/skill/xinyi/stores"

    with urllib.request.urlopen(url, timeout=config["timeoutSeconds"]) as response:
        payload = json.loads(response.read().decode("utf-8"))
        sys.stdout.write(render_stores_section(payload.get("data", {}).get("stores", [])))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
