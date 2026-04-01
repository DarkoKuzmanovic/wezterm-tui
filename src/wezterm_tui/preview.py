"""Live preview panel for WezTerm settings."""

from __future__ import annotations

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
