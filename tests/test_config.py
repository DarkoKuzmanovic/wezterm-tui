import json
from pathlib import Path
from wezterm_tui.config import load_settings, save_settings, get_config_dir


def test_load_settings_returns_defaults_when_no_file(tmp_path):
    settings = load_settings(tmp_path / "settings.json")
    assert settings["font"]["family"] == "JetBrains Mono"
    assert settings["_version"] == 1


def test_save_and_load_roundtrip(tmp_path):
    path = tmp_path / "settings.json"
    settings = load_settings(path)
    settings["font"]["size"] = 14.0
    save_settings(path, settings)
    reloaded = load_settings(path)
    assert reloaded["font"]["size"] == 14.0


def test_save_creates_backup(tmp_path):
    path = tmp_path / "settings.json"
    save_settings(path, {"_version": 1, "font": {"size": 12.0}})
    save_settings(path, {"_version": 1, "font": {"size": 14.0}})
    backup = path.with_suffix(".json.bak")
    assert backup.exists()
    data = json.loads(backup.read_text())
    assert data["font"]["size"] == 12.0


def test_load_merges_missing_keys_from_defaults(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"_version": 1, "font": {"family": "Fira Code"}}))
    settings = load_settings(path)
    assert settings["font"]["family"] == "Fira Code"
    assert "size" in settings["font"]
    assert "cursor" in settings
