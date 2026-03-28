import json
import pytest
from wezterm_tui.profiles import list_profiles, save_profile, load_profile, delete_profile


def test_list_profiles_empty(tmp_path):
    assert list_profiles(tmp_path) == []


def test_save_and_load_profile(tmp_path):
    settings = {"font": {"size": 14}, "colors": {"color_scheme": "Dracula"}}
    save_profile("coding", settings, tmp_path)
    loaded = load_profile("coding", tmp_path)
    assert loaded == settings


def test_list_profiles(tmp_path):
    save_profile("coding", {"a": 1}, tmp_path)
    save_profile("presentation", {"b": 2}, tmp_path)
    profiles = list_profiles(tmp_path)
    assert sorted(profiles) == ["coding", "presentation"]


def test_delete_profile(tmp_path):
    save_profile("temp", {"a": 1}, tmp_path)
    assert "temp" in list_profiles(tmp_path)
    delete_profile("temp", tmp_path)
    assert "temp" not in list_profiles(tmp_path)


def test_delete_nonexistent_profile(tmp_path):
    delete_profile("nope", tmp_path)  # should not raise


def test_load_nonexistent_profile(tmp_path):
    assert load_profile("nope", tmp_path) is None


def test_profile_isolation(tmp_path):
    settings = {"font": {"size": 14}}
    save_profile("a", settings, tmp_path)
    settings["font"]["size"] = 999
    loaded = load_profile("a", tmp_path)
    assert loaded["font"]["size"] == 14
