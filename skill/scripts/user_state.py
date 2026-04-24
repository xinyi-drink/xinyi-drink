#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import os


def resolve_state_file() -> Path:
    configured = os.getenv("XINYI_DRINK_STATE_FILE")
    if configured:
        return Path(configured).expanduser()

    return Path.home() / ".xinyi-drink" / "state.json"


def load_state() -> dict:
    state_file = resolve_state_file()
    if not state_file.exists():
        return {}

    try:
        return json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_mobile(mobile: str) -> None:
    state_file = resolve_state_file()
    state_file.parent.mkdir(parents=True, exist_ok=True)
    payload = load_state()
    payload["mobile"] = mobile
    payload["updatedAt"] = datetime.now(timezone.utc).isoformat()
    state_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def clear_mobile() -> None:
    state_file = resolve_state_file()
    payload = load_state()
    payload.pop("mobile", None)
    payload["updatedAt"] = datetime.now(timezone.utc).isoformat()
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_mobile() -> str | None:
    value = load_state().get("mobile")
    return value if isinstance(value, str) and value.strip() else None
