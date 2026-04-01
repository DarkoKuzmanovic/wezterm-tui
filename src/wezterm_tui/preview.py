"""Live preview panel for WezTerm settings."""

from __future__ import annotations

from rich.text import Text
from rich.style import Style
from rich.color import Color

_DEFAULT_FG = "#d4d4d4"
_DEFAULT_BG = "#1e1e1e"
_DEFAULT_ANSI = [
    "#000000", "#cd3131", "#0dbc79", "#e5e510",
    "#2472c8", "#bc3fbc", "#11a8cd", "#e5e5e5",
]
_DEFAULT_BRIGHTS = [
    "#666666", "#f14c4c", "#23d18b", "#f5f543",
    "#3b8eea", "#d670d6", "#29b8db", "#e5e5e5",
]


def resolve_palette(scheme_name: str, palettes: dict) -> dict:
    """Look up a color scheme palette, falling back to defaults."""
    scheme = palettes.get(scheme_name)
    if scheme is None:
        return {
            "fg": _DEFAULT_FG,
            "bg": _DEFAULT_BG,
            "ansi": list(_DEFAULT_ANSI),
            "brights": list(_DEFAULT_BRIGHTS),
            "unknown": True,
        }
    return {
        "fg": scheme.get("foreground", _DEFAULT_FG),
        "bg": scheme.get("background", _DEFAULT_BG),
        "ansi": scheme.get("ansi", list(_DEFAULT_ANSI)),
        "brights": scheme.get("brights", list(_DEFAULT_BRIGHTS)),
        "unknown": False,
    }


def blend_opacity(hex_color: str, opacity: float) -> str:
    """Blend a hex color toward black by opacity (1.0 = unchanged, 0.0 = black)."""
    opacity = max(0.0, min(1.0, opacity))
    hex_color = hex_color.lstrip("#")
    r = int(int(hex_color[0:2], 16) * opacity)
    g = int(int(hex_color[2:4], 16) * opacity)
    b = int(int(hex_color[4:6], 16) * opacity)
    return f"#{r:02x}{g:02x}{b:02x}"


_CURSOR_CHARS = {
    "SteadyBlock": "\u2588",
    "BlinkingBlock": "\u2588",
    "SteadyBar": "|",
    "BlinkingBar": "|",
    "SteadyUnderline": "\u2581",
    "BlinkingUnderline": "\u2581",
}


def _get_setting(settings: dict, category: str, key: str, default):
    """Safely get a nested setting value."""
    return settings.get(category, {}).get(key, default)


def build_preview_text(settings: dict, palettes: dict) -> Text:
    """Build a Rich Text object simulating a terminal session.

    Pure function: settings dict + palettes dict in, Rich Text out.
    """
    # Resolve colors
    scheme_name = _get_setting(settings, "colors", "color_scheme", "Default (Dark)")
    palette = resolve_palette(scheme_name, palettes)
    fg = palette["fg"]
    bg = palette["bg"]
    ansi = palette["ansi"]
    brights = palette["brights"]

    # Resolve visual settings
    font_family = _get_setting(settings, "font", "family", "JetBrains Mono")
    font_size = _get_setting(settings, "font", "size", 12.0)
    font_weight = _get_setting(settings, "font", "weight", "Regular")
    line_height = _get_setting(settings, "font", "line_height", 1.0)

    cursor_style = _get_setting(settings, "cursor", "default_cursor_style", "SteadyBlock")
    cursor_blink = "blink" if "Blinking" in cursor_style else "steady"
    cursor_char = _CURSOR_CHARS.get(cursor_style, "\u2588")
    cursor_label = cursor_style.replace("Steady", "").replace("Blinking", "").lower()

    opacity = _get_setting(settings, "window", "background_opacity", 1.0)
    if not isinstance(opacity, (int, float)):
        opacity = 1.0
    padding = _get_setting(settings, "window", "padding", {"left": 0, "right": 0, "top": 0, "bottom": 0})
    if not isinstance(padding, dict):
        padding = {"left": 0, "right": 0, "top": 0, "bottom": 0}

    # Apply opacity to background
    effective_bg = blend_opacity(bg, opacity)

    # Build styles
    bg_color = Color.parse(effective_bg)
    base = Style(color=fg, bgcolor=bg_color)
    dim = Style(color=fg, bgcolor=bg_color, dim=True)
    green = Style(color=ansi[2], bgcolor=bg_color, bold=True)
    cyan = Style(color=ansi[6], bgcolor=bg_color)
    blue = Style(color=ansi[4], bgcolor=bg_color)
    magenta = Style(color=ansi[5], bgcolor=bg_color)
    bright_fg = Style(color=brights[7] if len(brights) > 7 else fg, bgcolor=bg_color, bold=True)
    rule_style = Style(color=brights[0] if brights else "#666666", bgcolor=bg_color)

    # Compose the text
    text = Text()

    # Line 1: font info + opacity
    info_left = f" {font_family}  {font_size}pt  {font_weight}"
    opacity_str = f"opacity: {opacity:.2f}"
    if palette["unknown"]:
        opacity_str += "  (unknown scheme)"
    text.append(info_left, style=dim)
    gap = max(1, 40 - len(info_left))
    text.append(" " * gap, style=base)
    text.append(opacity_str, style=dim)
    text.append("\n")

    # Line 2: horizontal rule
    text.append(" " + "\u2500" * 62, style=rule_style)
    text.append("\n")

    # Line 3: prompt + command
    text.append(" ", style=base)
    text.append("user@host", style=green)
    text.append(" ", style=base)
    text.append("~", style=cyan)
    text.append(" $ ", style=base)
    text.append("ls -la", style=base)
    text.append("\n")

    # Lines 4-6: file listing
    text.append(" drwxr-xr-x  5 user staff  160 Mar 28 10:00 ", style=base)
    text.append("src/", style=blue)
    text.append("\n")

    text.append(" -rw-r--r--  1 user staff 4096 Mar 28 09:45 ", style=base)
    text.append("README.md", style=base)
    text.append("\n")

    text.append(" -rwxr-xr-x  1 user staff  512 Mar 27 14:20 ", style=base)
    text.append("run.sh", style=magenta)
    text.append("\n")

    # Line 7: second prompt with cursor
    text.append(" ", style=base)
    text.append("user@host", style=green)
    text.append(" ", style=base)
    text.append("~", style=cyan)
    text.append(" $ ", style=base)
    text.append(cursor_char, style=bright_fg)
    text.append("\n")

    # Line 8: horizontal rule
    text.append(" " + "\u2500" * 62, style=rule_style)
    text.append("\n")

    # Line 9: status strip
    pad_l = padding.get("left", 0)
    pad_r = padding.get("right", 0)
    pad_t = padding.get("top", 0)
    pad_b = padding.get("bottom", 0)
    status = f" padding: {pad_l}/{pad_r}/{pad_t}/{pad_b}  cursor: {cursor_label}, {cursor_blink}  line-height: {line_height}"
    text.append(status, style=dim)

    return text
