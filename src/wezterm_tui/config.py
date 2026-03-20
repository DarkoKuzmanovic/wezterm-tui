"""JSON settings read/write with backup and default-merging."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from wezterm_tui.schema import get_defaults

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


def load_settings(path: Path | None = None) -> dict[str, Any]:
    if path is None:
        path = get_config_dir() / CONFIG_FILENAME
    defaults = get_defaults()
    defaults["_version"] = CURRENT_VERSION
    if not path.exists():
        return defaults
    with open(path) as f:
        saved = json.load(f)
    return _deep_merge(defaults, saved)


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
