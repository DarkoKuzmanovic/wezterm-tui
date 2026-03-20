"""JSON settings read/write with backup and default-merging."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from wezterm_tui.schema import SCHEMA, OptionType, get_defaults, validate_value as _validate

CONFIG_FILENAME = "settings.json"
CURRENT_VERSION = 1


def get_config_dir() -> Path:
    path = Path.home() / ".config" / "wezterm"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _sanitize_settings(settings: dict) -> dict:
    """Validate loaded settings against schema, replacing invalid values with defaults."""
    defaults = get_defaults()
    for opt in SCHEMA:
        if opt.type == OptionType.KEYBINDINGS:
            if not isinstance(settings.get("keybindings"), list):
                settings["keybindings"] = defaults.get("keybindings", [])
            continue
        cat = settings.get(opt.category, {})
        if opt.key in cat:
            if not _validate(opt, cat[opt.key]):
                cat[opt.key] = defaults.get(opt.category, {}).get(opt.key, opt.default)
    return settings


def load_settings(path: Path | None = None) -> dict[str, Any]:
    if path is None:
        path = get_config_dir() / CONFIG_FILENAME
    defaults = get_defaults()
    defaults["_version"] = CURRENT_VERSION
    if not path.exists():
        return defaults
    with open(path) as f:
        saved = json.load(f)
    merged = _deep_merge(defaults, saved)
    return _sanitize_settings(merged)


def save_settings(path: Path | None = None, settings: dict[str, Any] | None = None) -> None:
    if path is None:
        path = get_config_dir() / CONFIG_FILENAME
    if settings is None:
        return
    settings["_version"] = CURRENT_VERSION
    if path.exists():
        backup = path.with_suffix(".json.bak")
        shutil.copy2(path, backup)
    tmp = path.with_suffix(".json.tmp")
    with open(tmp, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")
    tmp.rename(path)
