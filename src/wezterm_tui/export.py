"""Export settings as Lua, JSON, or base64."""

from __future__ import annotations

import base64
import json

from wezterm_tui.lua_gen import generate_lua


def export_lua(settings: dict) -> str:
    return generate_lua(settings)


def export_json(settings: dict) -> str:
    return json.dumps(settings, indent=2)


def export_base64(settings: dict) -> str:
    raw = json.dumps(settings, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode()


def import_base64(blob: str) -> dict | None:
    try:
        raw = base64.urlsafe_b64decode(blob.encode())
        return json.loads(raw)
    except (ValueError, json.JSONDecodeError):
        return None
