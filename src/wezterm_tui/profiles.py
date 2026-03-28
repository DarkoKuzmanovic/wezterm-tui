"""Named settings profiles -- save, load, list, delete."""

from __future__ import annotations

import json
from pathlib import Path

from wezterm_tui.config import get_config_dir


def _profiles_dir(base: Path | None = None) -> Path:
    d = (base or get_config_dir()) / "profiles"
    d.mkdir(parents=True, exist_ok=True)
    return d


def list_profiles(base: Path | None = None) -> list[str]:
    d = _profiles_dir(base)
    return sorted(p.stem for p in d.glob("*.json"))


def save_profile(name: str, settings: dict, base: Path | None = None) -> None:
    path = _profiles_dir(base) / f"{name}.json"
    with open(path, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")


def load_profile(name: str, base: Path | None = None) -> dict | None:
    path = _profiles_dir(base) / f"{name}.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def delete_profile(name: str, base: Path | None = None) -> None:
    path = _profiles_dir(base) / f"{name}.json"
    if path.exists():
        path.unlink()
