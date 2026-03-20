"""One-time import from an existing wezterm.lua config file."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from wezterm_tui.schema import get_defaults

_LUA_KEY_TO_JSON: dict[str, tuple[str, str]] = {
    "window_padding": ("window", "padding"),
    "window_decorations": ("window", "decorations"),
    "window_background_opacity": ("window", "background_opacity"),
    "initial_cols": ("window", "initial_cols"),
    "initial_rows": ("window", "initial_rows"),
    "color_scheme": ("colors", "color_scheme"),
    "enable_tab_bar": ("tabs", "enable_tab_bar"),
    "use_fancy_tab_bar": ("tabs", "use_fancy_tab_bar"),
    "tab_bar_at_bottom": ("tabs", "tab_bar_at_bottom"),
    "hide_tab_bar_if_only_one_tab": ("tabs", "hide_tab_bar_if_only_one_tab"),
    "show_new_tab_button_in_tab_bar": ("tabs", "show_new_tab_button_in_tab_bar"),
    "show_close_tab_button_in_tabs": ("tabs", "show_close_tab_button_in_tabs"),
    "show_tab_index_in_tab_bar": ("tabs", "show_tab_index_in_tab_bar"),
    "tab_max_width": ("tabs", "tab_max_width"),
    "default_cursor_style": ("cursor", "default_cursor_style"),
    "cursor_blink_rate": ("cursor", "cursor_blink_rate"),
    "cursor_blink_ease_in": ("cursor", "cursor_blink_ease_in"),
    "cursor_blink_ease_out": ("cursor", "cursor_blink_ease_out"),
    "cursor_thickness": ("cursor", "cursor_thickness"),
    "scrollback_lines": ("scrollback", "scrollback_lines"),
    "enable_scroll_bar": ("scrollback", "enable_scroll_bar"),
    "scroll_to_bottom_on_input": ("scrollback", "scroll_to_bottom_on_input"),
    "min_scroll_bar_height": ("scrollback", "min_scroll_bar_height"),
    "front_end": ("performance", "front_end"),
    "max_fps": ("performance", "max_fps"),
    "animation_fps": ("performance", "animation_fps"),
    "webgpu_power_preference": ("performance", "webgpu_power_preference"),
    "pane_focus_follows_mouse": ("mouse", "pane_focus_follows_mouse"),
    "hide_mouse_cursor_when_typing": ("mouse", "hide_mouse_cursor_when_typing"),
    "swallow_mouse_click_on_pane_focus": ("mouse", "swallow_mouse_click_on_pane_focus"),
    "swallow_mouse_click_on_window_focus": ("mouse", "swallow_mouse_click_on_window_focus"),
    "mouse_wheel_scrolls_tabs": ("mouse", "mouse_wheel_scrolls_tabs"),
    "audible_bell": ("misc", "audible_bell"),
    "check_for_updates": ("misc", "check_for_updates"),
    "automatically_reload_config": ("misc", "automatically_reload_config"),
    "term": ("misc", "term"),
    "exit_behavior": ("misc", "exit_behavior"),
    "canonicalize_pasted_newlines": ("misc", "canonicalize_pasted_newlines"),
    "enable_wayland": ("misc", "enable_wayland"),
    "enable_kitty_keyboard": ("misc", "enable_kitty_keyboard"),
}

_RE_FONT = re.compile(
    r'config\.font\s*=\s*wezterm\.font\(\s*"([^"]+)"\s*,\s*\{\s*weight\s*=\s*"([^"]+)"\s*\}\s*\)'
)
_RE_STRING = re.compile(r'config\.(\w+)\s*=\s*"([^"]*)"')
_RE_NUMBER = re.compile(r'config\.(\w+)\s*=\s*([0-9]+(?:\.[0-9]+)?)')
_RE_BOOL = re.compile(r'config\.(\w+)\s*=\s*(true|false)')
_RE_PADDING = re.compile(
    r'config\.window_padding\s*=\s*\{\s*'
    r'left\s*=\s*(\d+)\s*,\s*right\s*=\s*(\d+)\s*,\s*'
    r'top\s*=\s*(\d+)\s*,\s*bottom\s*=\s*(\d+)\s*,?\s*\}',
    re.DOTALL,
)

_RE_QUOTED_STRING = re.compile(r'"([^"]*)"')

_STRING_LIST_KEYS: dict[str, tuple[str, str]] = {
    "quick_select_patterns": ("misc", "quick_select_patterns"),
    "harfbuzz_features": ("font", "harfbuzz_features"),
}

_RE_STRING_LIST_START = re.compile(r'config\.(\w+)\s*=\s*\{')

_RE_KEY_BLOCK_START = re.compile(r'config\.keys\s*=\s*\{')
_RE_KEY_NOARG = re.compile(
    r'\{\s*key\s*=\s*"([^"]+)"\s*,\s*mods\s*=\s*"([^"]+)"\s*,\s*action\s*=\s*wezterm\.action\.(\w+)\s*\}'
)
_RE_KEY_STR_ARG = re.compile(
    r'\{\s*key\s*=\s*"([^"]+)"\s*,\s*mods\s*=\s*"([^"]+)"\s*,\s*'
    r'action\s*=\s*wezterm\.action\.(\w+)\(\s*"([^"]+)"\s*\)\s*\}'
)
_RE_KEY_TABLE_ARG = re.compile(
    r'\{\s*key\s*=\s*"([^"]+)"\s*,\s*mods\s*=\s*"([^"]+)"\s*,\s*'
    r'action\s*=\s*wezterm\.action\.(\w+)\(\s*\{([^}]*)\}\s*\)\s*\}'
)
_RE_TABLE_KV = re.compile(r'(\w+)\s*=\s*"?([^",\s]+)"?')


def _extract_outer_block(content: str, start: int) -> str | None:
    """Given the index of the opening '{' in content, return the text inside the outermost braces."""
    depth = 0
    i = start
    while i < len(content):
        ch = content[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return content[start + 1:i]
        i += 1
    return None


def _parse_table_args(s: str) -> dict[str, Any]:
    result = {}
    for m in _RE_TABLE_KV.finditer(s):
        k, v = m.group(1), m.group(2)
        if v == "true":
            result[k] = True
        elif v == "false":
            result[k] = False
        else:
            try:
                result[k] = int(v)
            except ValueError:
                try:
                    result[k] = float(v)
                except ValueError:
                    result[k] = v
    return result


def import_from_wezterm_lua(content: str) -> dict[str, Any]:
    settings = get_defaults()
    settings["_version"] = 1

    m = _RE_FONT.search(content)
    if m:
        settings["font"]["family"] = m.group(1)
        settings["font"]["weight"] = m.group(2)

    font_number_keys = {"font_size": "size", "line_height": "line_height"}

    m = _RE_PADDING.search(content)
    if m:
        settings["window"]["padding"] = {
            "left": int(m.group(1)), "right": int(m.group(2)),
            "top": int(m.group(3)), "bottom": int(m.group(4)),
        }

    for m in _RE_BOOL.finditer(content):
        key, val = m.group(1), m.group(2) == "true"
        if key in _LUA_KEY_TO_JSON:
            cat, json_key = _LUA_KEY_TO_JSON[key]
            settings[cat][json_key] = val

    for m in _RE_STRING.finditer(content):
        key, val = m.group(1), m.group(2)
        if key in _LUA_KEY_TO_JSON:
            cat, json_key = _LUA_KEY_TO_JSON[key]
            settings[cat][json_key] = val

    for m in _RE_NUMBER.finditer(content):
        key, val_str = m.group(1), m.group(2)
        val: int | float = float(val_str) if "." in val_str else int(val_str)
        if key in font_number_keys:
            settings["font"][font_number_keys[key]] = val
        elif key in _LUA_KEY_TO_JSON:
            cat, json_key = _LUA_KEY_TO_JSON[key]
            settings[cat][json_key] = val

    for m in _RE_STRING_LIST_START.finditer(content):
        key = m.group(1)
        if key in _STRING_LIST_KEYS:
            body = _extract_outer_block(content, m.end() - 1)
            if body is not None:
                cat, json_key = _STRING_LIST_KEYS[key]
                values = _RE_QUOTED_STRING.findall(body)
                settings[cat][json_key] = values

    kb_start = _RE_KEY_BLOCK_START.search(content)
    if kb_start:
        block = _extract_outer_block(content, kb_start.end() - 1)
        if block is not None:
            keybindings = []
            # Collect all matches with their positions to preserve original order
            all_matches: list[tuple[int, dict[str, Any]]] = []
            for m in _RE_KEY_TABLE_ARG.finditer(block):
                all_matches.append((m.start(), {"key": m.group(1), "mods": m.group(2),
                                    "action": m.group(3), "args": _parse_table_args(m.group(4))}))
            for m in _RE_KEY_STR_ARG.finditer(block):
                all_matches.append((m.start(), {"key": m.group(1), "mods": m.group(2),
                                    "action": m.group(3), "args": m.group(4)}))
            for m in _RE_KEY_NOARG.finditer(block):
                all_matches.append((m.start(), {"key": m.group(1), "mods": m.group(2),
                                    "action": m.group(3)}))
            # Sort by position and deduplicate (keep first occurrence per key+mods)
            all_matches.sort(key=lambda x: x[0])
            seen: set[tuple[str, str]] = set()
            for _, kb in all_matches:
                pair = (kb["key"], kb["mods"])
                if pair not in seen:
                    seen.add(pair)
                    keybindings.append(kb)
            settings["keybindings"] = keybindings

    return settings


def import_from_file(path: Path | None = None) -> dict[str, Any]:
    if path is None:
        path = Path.home() / ".config" / "wezterm" / "wezterm.lua"
    content = path.read_text()
    return import_from_wezterm_lua(content)
