import json

import pytest
from wezterm_tui.app import WezTermSettingsApp
from wezterm_tui.config import load_settings, save_settings
from wezterm_tui.lua_gen import generate_lua
from wezterm_tui.screens import SCREEN_MAP


async def test_app_starts():
    app = WezTermSettingsApp()
    async with app.run_test() as pilot:
        assert app.title == "WezTerm Settings"
        assert app.active_category == "font"


async def test_sidebar_navigation():
    app = WezTermSettingsApp()
    async with app.run_test() as pilot:
        sidebar = app.query_one("#sidebar")
        items = sidebar.query("ListItem")
        assert len(items) == 10


@pytest.mark.parametrize("category", list(SCREEN_MAP.keys()))
async def test_screen_renders(category):
    """Verify each settings screen mounts without errors."""
    app = WezTermSettingsApp()
    async with app.run_test() as pilot:
        await app._switch_screen(category)
        await pilot.pause()
        # Verify the screen mounted
        content = app.query_one("#content-area")
        assert content.children


def test_full_roundtrip(tmp_path):
    """Save settings -> generate Lua -> verify content."""
    json_path = tmp_path / "settings.json"
    lua_path = tmp_path / "settings.lua"

    settings = load_settings(json_path)
    settings["font"]["family"] = "Fira Code"
    settings["font"]["size"] = 14.0
    settings["colors"]["color_scheme"] = "Dracula"
    settings["window"]["background_opacity"] = 0.9
    settings["keybindings"] = [
        {"key": "t", "mods": "CTRL", "action": "SpawnTab", "args": {"domain_name": "local"}},
    ]

    save_settings(json_path, settings)

    lua = generate_lua(settings)
    lua_path.write_text(lua)

    assert 'wezterm.font("Fira Code"' in lua
    assert "M.font_size = 14.0" in lua
    assert '"Dracula"' in lua
    assert "M.window_background_opacity = 0.9" in lua
    assert "return M" in lua

    # Verify JSON was saved correctly
    reimported = json.loads(json_path.read_text())
    assert reimported["font"]["family"] == "Fira Code"
    assert reimported["font"]["size"] == 14.0
    assert reimported["colors"]["color_scheme"] == "Dracula"
