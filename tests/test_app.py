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


async def test_color_preview_updates_on_highlight(monkeypatch):
    from textual.widgets import ListView

    from wezterm_tui.screens import colors as colors_module

    monkeypatch.setattr(
        colors_module, "load_scheme_names", lambda: ["Dracula", "Gruvbox Dark"]
    )
    monkeypatch.setattr(
        colors_module,
        "load_scheme_palettes",
        lambda: {
            "Dracula": {
                "background": "#282a36",
                "foreground": "#f8f8f2",
                "selection_bg": "#44475a",
                "selection_fg": "#f8f8f2",
                "cursor_bg": "#f8f8f2",
                "ansi": ["#000000"] * 8,
                "brights": ["#ffffff"] * 8,
            },
            "Gruvbox Dark": {
                "background": "#282828",
                "foreground": "#ebdbb2",
                "selection_bg": "#504945",
                "selection_fg": "#ebdbb2",
                "cursor_bg": "#fabd2f",
                "ansi": ["#111111"] * 8,
                "brights": ["#eeeeee"] * 8,
            },
        },
    )

    app = WezTermSettingsApp()
    app.settings["colors"]["color_scheme"] = "Dracula"

    async with app.run_test() as pilot:
        await app._switch_screen("colors")
        await pilot.pause()

        screen = app.current_screen
        assert screen.preview_scheme == "Dracula"
        assert screen.current_scheme == "Dracula"

        list_view = screen.query_one("#scheme-list", ListView)
        list_view.focus()
        list_view.index = 1
        await pilot.pause()

        assert screen.preview_scheme == "Gruvbox Dark"
        assert screen.current_scheme == "Dracula"

        await pilot.press("enter")
        await pilot.pause()

        assert screen.current_scheme == "Gruvbox Dark"
        assert app.settings["colors"]["color_scheme"] == "Gruvbox Dark"


async def test_color_search_is_debounced(monkeypatch):
    from textual.widgets import Input

    from wezterm_tui.screens import colors as colors_module

    monkeypatch.setattr(
        colors_module,
        "load_scheme_names",
        lambda: ["Dracula", "Gruvbox Dark", "Night Owl"],
    )
    monkeypatch.setattr(colors_module, "load_scheme_palettes", lambda: {})

    app = WezTermSettingsApp()

    async with app.run_test() as pilot:
        await app._switch_screen("colors")
        await pilot.pause()

        screen = app.current_screen
        screen.SEARCH_DEBOUNCE_SECONDS = 0.02
        calls = []

        async def capture(schemes):
            calls.append(list(schemes))

        monkeypatch.setattr(screen, "_populate_list", capture)
        search = screen.query_one("#scheme-search", Input)

        await screen.on_input_changed(Input.Changed(search, "g"))
        await screen.on_input_changed(Input.Changed(search, "gr"))
        await screen.on_input_changed(Input.Changed(search, "gru"))
        await pilot.pause(0.01)

        assert calls == []

        await pilot.pause(0.03)

        assert calls == [["Gruvbox Dark"]]


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
        {
            "key": "t",
            "mods": "CTRL",
            "action": "SpawnTab",
            "args": {"domain_name": "local"},
        },
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
