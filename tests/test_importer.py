# tests/test_importer.py
from wezterm_tui.importer import import_from_wezterm_lua


SAMPLE_CONFIG = '''
local wezterm = require("wezterm")
local config = wezterm.config_builder()

config.font = wezterm.font("JetBrains Mono", { weight = "Medium" })
config.font_size = 11.0
config.line_height = 1.1
config.color_scheme = "Catppuccin Mocha"
config.window_padding = { left = 8, right = 8, top = 8, bottom = 8 }
config.window_decorations = "TITLE | RESIZE"
config.window_background_opacity = 0.95
config.initial_cols = 140
config.initial_rows = 40
config.enable_tab_bar = true
config.use_fancy_tab_bar = false
config.tab_bar_at_bottom = true
config.hide_tab_bar_if_only_one_tab = true
config.default_cursor_style = "BlinkingBar"
config.cursor_blink_rate = 500
config.scrollback_lines = 10000
config.enable_scroll_bar = false
config.front_end = "WebGpu"
config.max_fps = 120
config.audible_bell = "Disabled"
config.check_for_updates = false

config.quick_select_patterns = {
    "[0-9a-f]{7,40}",
    "/[\\\\w./-]+",
}

config.keys = {
    { key = "d", mods = "CTRL|SHIFT", action = wezterm.action.SplitHorizontal({ domain = "CurrentPaneDomain" }) },
    { key = "=", mods = "CTRL", action = wezterm.action.IncreaseFontSize },
    { key = "h", mods = "CTRL|SHIFT", action = wezterm.action.ActivatePaneDirection("Left") },
}

return config
'''


def test_import_font():
    settings = import_from_wezterm_lua(SAMPLE_CONFIG)
    assert settings["font"]["family"] == "JetBrains Mono"
    assert settings["font"]["weight"] == "Medium"
    assert settings["font"]["size"] == 11.0


def test_import_scalars():
    settings = import_from_wezterm_lua(SAMPLE_CONFIG)
    assert settings["colors"]["color_scheme"] == "Catppuccin Mocha"
    assert settings["window"]["background_opacity"] == 0.95
    assert settings["performance"]["front_end"] == "WebGpu"
    assert settings["misc"]["audible_bell"] == "Disabled"


def test_import_booleans():
    settings = import_from_wezterm_lua(SAMPLE_CONFIG)
    assert settings["tabs"]["enable_tab_bar"] is True
    assert settings["tabs"]["use_fancy_tab_bar"] is False
    assert settings["misc"]["check_for_updates"] is False


def test_import_padding():
    settings = import_from_wezterm_lua(SAMPLE_CONFIG)
    assert settings["window"]["padding"] == {"left": 8, "right": 8, "top": 8, "bottom": 8}


def test_import_keybindings():
    settings = import_from_wezterm_lua(SAMPLE_CONFIG)
    keys = settings["keybindings"]
    assert len(keys) == 3
    assert keys[0]["action"] == "SplitHorizontal"
    assert keys[0]["args"] == {"domain": "CurrentPaneDomain"}
    assert keys[1]["action"] == "IncreaseFontSize"
    assert keys[1].get("args") is None
    assert keys[2]["action"] == "ActivatePaneDirection"
    assert keys[2]["args"] == "Left"


def test_import_quick_select_patterns():
    settings = import_from_wezterm_lua(SAMPLE_CONFIG)
    patterns = settings["misc"]["quick_select_patterns"]
    assert len(patterns) == 2
    assert "[0-9a-f]{7,40}" in patterns
