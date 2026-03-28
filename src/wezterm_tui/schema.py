"""WezTerm option schema definitions."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class OptionType(Enum):
    STRING = "string"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    ENUM = "enum"
    STRING_LIST = "string_list"
    PADDING = "padding"
    KEYBINDINGS = "keybindings"


@dataclass
class Option:
    key: str
    category: str
    label: str
    type: OptionType
    default: Any
    description: str = ""
    enum_values: list[str] = field(default_factory=list)
    min_value: float | None = None
    max_value: float | None = None
    lua_key: str | None = None  # Lua config key; defaults to same as `key`


SCHEMA: list[Option] = [
    # Font
    Option("family", "font", "Font Family", OptionType.STRING, "JetBrains Mono", description="Font family name"),
    Option("weight", "font", "Font Weight", OptionType.ENUM, "Regular",
           enum_values=["Thin", "ExtraLight", "Light", "Regular", "Medium", "DemiBold", "Bold", "ExtraBold", "Black"]),
    Option("size", "font", "Font Size", OptionType.FLOAT, 12.0, min_value=4.0, max_value=72.0),
    Option("line_height", "font", "Line Height", OptionType.FLOAT, 1.0, min_value=0.5, max_value=3.0),
    Option("harfbuzz_features", "font", "HarfBuzz Features", OptionType.STRING_LIST, [],
           description="OpenType features e.g. calt, liga, zero"),

    # Colors
    Option("color_scheme", "colors", "Color Scheme", OptionType.STRING, "Default (Dark)",
           description="WezTerm built-in color scheme name"),

    # Window
    Option("padding", "window", "Window Padding", OptionType.PADDING, {"left": 0, "right": 0, "top": 0, "bottom": 0},
           lua_key="window_padding"),
    Option("decorations", "window", "Window Decorations", OptionType.ENUM, "TITLE | RESIZE",
           enum_values=["NONE", "TITLE", "RESIZE", "TITLE | RESIZE", "INTEGRATED_BUTTONS|RESIZE"],
           lua_key="window_decorations"),
    Option("background_opacity", "window", "Background Opacity", OptionType.FLOAT, 1.0, min_value=0.0, max_value=1.0,
           lua_key="window_background_opacity"),
    Option("initial_cols", "window", "Initial Columns", OptionType.INT, 80, min_value=20, max_value=500),
    Option("initial_rows", "window", "Initial Rows", OptionType.INT, 24, min_value=5, max_value=200),
    Option("adjust_window_size_when_changing_font_size", "window",
           "Adjust Window on Font Change", OptionType.BOOL, True),

    # Tabs
    Option("enable_tab_bar", "tabs", "Enable Tab Bar", OptionType.BOOL, True),
    Option("use_fancy_tab_bar", "tabs", "Fancy Tab Bar", OptionType.BOOL, True),
    Option("tab_bar_at_bottom", "tabs", "Tab Bar at Bottom", OptionType.BOOL, False),
    Option("hide_tab_bar_if_only_one_tab", "tabs", "Hide If Only One Tab", OptionType.BOOL, False),
    Option("show_new_tab_button_in_tab_bar", "tabs", "Show New Tab Button", OptionType.BOOL, True),
    Option("show_close_tab_button_in_tabs", "tabs", "Show Close Button", OptionType.BOOL, True),
    Option("show_tab_index_in_tab_bar", "tabs", "Show Tab Index", OptionType.BOOL, False),
    Option("tab_max_width", "tabs", "Max Tab Width", OptionType.INT, 16, min_value=1, max_value=100),

    # Cursor
    Option("default_cursor_style", "cursor", "Cursor Style", OptionType.ENUM, "SteadyBlock",
           enum_values=["SteadyBlock", "BlinkingBlock", "SteadyUnderline", "BlinkingUnderline", "SteadyBar", "BlinkingBar"]),
    Option("cursor_blink_rate", "cursor", "Blink Rate (ms)", OptionType.INT, 800, min_value=0, max_value=5000),
    Option("cursor_blink_ease_in", "cursor", "Blink Ease In", OptionType.ENUM, "Constant",
           enum_values=["Constant", "Linear", "EaseIn", "EaseInOut", "EaseOut"]),
    Option("cursor_blink_ease_out", "cursor", "Blink Ease Out", OptionType.ENUM, "Constant",
           enum_values=["Constant", "Linear", "EaseIn", "EaseInOut", "EaseOut"]),
    Option("cursor_thickness", "cursor", "Cursor Thickness", OptionType.INT, 1, min_value=1, max_value=10),
    Option("cell_width", "cursor", "Cell Width", OptionType.FLOAT, 1.0,
           min_value=0.5, max_value=2.0),

    # Scrollback
    Option("scrollback_lines", "scrollback", "Scrollback Lines", OptionType.INT, 3500, min_value=0, max_value=1000000),
    Option("enable_scroll_bar", "scrollback", "Show Scroll Bar", OptionType.BOOL, False),
    Option("scroll_to_bottom_on_input", "scrollback", "Scroll to Bottom on Input", OptionType.BOOL, True),
    Option("min_scroll_bar_height", "scrollback", "Min Scrollbar Height", OptionType.INT, 10, min_value=1, max_value=100),

    # Performance
    Option("front_end", "performance", "Rendering Backend", OptionType.ENUM, "OpenGL",
           enum_values=["OpenGL", "Software", "WebGpu"]),
    Option("max_fps", "performance", "Max FPS", OptionType.INT, 60, min_value=1, max_value=255),
    Option("animation_fps", "performance", "Animation FPS", OptionType.INT, 10, min_value=1, max_value=255),
    Option("webgpu_power_preference", "performance", "WebGPU Power Preference", OptionType.ENUM, "LowPower",
           enum_values=["LowPower", "HighPerformance"]),

    # Keybindings
    Option("keybindings", "keybindings", "Key Bindings", OptionType.KEYBINDINGS, []),

    # Mouse
    Option("pane_focus_follows_mouse", "mouse", "Focus Follows Mouse", OptionType.BOOL, False),
    Option("hide_mouse_cursor_when_typing", "mouse", "Hide Cursor When Typing", OptionType.BOOL, True),
    Option("swallow_mouse_click_on_pane_focus", "mouse", "Swallow Click on Pane Focus", OptionType.BOOL, False),
    Option("swallow_mouse_click_on_window_focus", "mouse", "Swallow Click on Window Focus", OptionType.BOOL, False),
    Option("mouse_wheel_scrolls_tabs", "mouse", "Mouse Wheel Scrolls Tabs", OptionType.BOOL, False),

    # Misc
    Option("audible_bell", "misc", "Audible Bell", OptionType.ENUM, "SystemBeep",
           enum_values=["SystemBeep", "Disabled"]),
    Option("check_for_updates", "misc", "Check for Updates", OptionType.BOOL, True),
    Option("automatically_reload_config", "misc", "Auto-Reload Config", OptionType.BOOL, True),
    Option("term", "misc", "TERM Variable", OptionType.STRING, "xterm-256color"),
    Option("exit_behavior", "misc", "Exit Behavior", OptionType.ENUM, "Close",
           enum_values=["Close", "Hold", "CloseOnCleanExit"]),
    Option("canonicalize_pasted_newlines", "misc", "Paste Newline Mode", OptionType.ENUM, "None",
           enum_values=["None", "LineFeed", "CarriageReturn", "CarriageReturnAndLineFeed"]),
    Option("enable_wayland", "misc", "Enable Wayland", OptionType.BOOL, True),
    Option("enable_kitty_keyboard", "misc", "Kitty Keyboard Protocol", OptionType.BOOL, False),
    Option("quick_select_patterns", "misc", "Quick Select Patterns", OptionType.STRING_LIST, [],
           description="Regex patterns for Ctrl+Shift+Space quick select"),
    Option("use_ime", "misc", "Use IME", OptionType.BOOL, True),
    Option("ime_preedit_rendering", "misc", "IME Preedit Rendering", OptionType.ENUM,
           "Builtin", enum_values=["Builtin", "Custom"]),
    Option("command_palette_font_size", "misc", "Command Palette Font Size",
           OptionType.FLOAT, 14.0, min_value=4.0, max_value=72.0),
    Option("window_close_confirmation", "misc", "Close Confirmation", OptionType.ENUM,
           "AlwaysPrompt", enum_values=["AlwaysPrompt", "NeverPrompt"]),
]

CATEGORIES = [
    ("font", "Font"), ("colors", "Colors"), ("window", "Window"), ("tabs", "Tab Bar"),
    ("cursor", "Cursor"), ("scrollback", "Scrollback"), ("performance", "Performance"),
    ("keybindings", "Keybindings"), ("mouse", "Mouse"), ("misc", "Misc"),
]


def get_defaults() -> dict:
    result: dict[str, Any] = {}
    for opt in SCHEMA:
        if opt.type == OptionType.KEYBINDINGS:
            result["keybindings"] = copy.deepcopy(opt.default)
            continue
        result.setdefault(opt.category, {})[opt.key] = copy.deepcopy(opt.default)
    return result


def get_category_options(category: str) -> list[Option]:
    return [o for o in SCHEMA if o.category == category]


def get_direct_lua_map() -> dict[str, list[tuple[str, str]]]:
    """Build category -> [(json_key, lua_key)] for direct-mapped options.

    Excludes font (special wezterm.font() call) and keybindings (special table).
    """
    result: dict[str, list[tuple[str, str]]] = {}
    for opt in SCHEMA:
        if opt.category == "font" or opt.type == OptionType.KEYBINDINGS:
            continue
        result.setdefault(opt.category, []).append((opt.key, opt.lua_key or opt.key))
    return result


def get_lua_key_to_json() -> dict[str, tuple[str, str]]:
    """Build lua_key -> (category, json_key) reverse mapping for the importer.

    Excludes font family/weight/size/line_height (parsed specially) and keybindings.
    """
    result: dict[str, tuple[str, str]] = {}
    _font_special = {"family", "weight", "size", "line_height"}
    for opt in SCHEMA:
        if opt.type == OptionType.KEYBINDINGS:
            continue
        if opt.category == "font" and opt.key in _font_special:
            continue
        lua_key = opt.lua_key or opt.key
        result[lua_key] = (opt.category, opt.key)
    return result


def validate_value(option: Option, value: Any) -> bool:
    match option.type:
        case OptionType.STRING:
            return isinstance(value, str)
        case OptionType.INT:
            if not isinstance(value, int) or isinstance(value, bool):
                return False
            if option.min_value is not None and value < option.min_value:
                return False
            if option.max_value is not None and value > option.max_value:
                return False
            return True
        case OptionType.FLOAT:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                return False
            if option.min_value is not None and value < option.min_value:
                return False
            if option.max_value is not None and value > option.max_value:
                return False
            return True
        case OptionType.BOOL:
            return isinstance(value, bool)
        case OptionType.ENUM:
            return value in option.enum_values
        case OptionType.STRING_LIST:
            return isinstance(value, list) and all(isinstance(s, str) for s in value)
        case OptionType.PADDING:
            return (isinstance(value, dict)
                    and set(value.keys()) == {"left", "right", "top", "bottom"}
                    and all(isinstance(v, int) and v >= 0 for v in value.values()))
        case OptionType.KEYBINDINGS:
            return isinstance(value, list)
    return False
