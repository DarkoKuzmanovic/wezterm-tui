"""Screen registry — maps category IDs to screen classes."""

from wezterm_tui.screens.base import SettingsScreen
from wezterm_tui.screens.colors import ColorsScreen
from wezterm_tui.screens.keybindings import KeybindingsScreen


def _make_simple_screen(category: str) -> type[SettingsScreen]:
    return type(
        f"{category.capitalize()}Screen",
        (SettingsScreen,),
        {"CATEGORY": category},
    )


FontScreen = _make_simple_screen("font")
WindowScreen = _make_simple_screen("window")
TabsScreen = _make_simple_screen("tabs")
CursorScreen = _make_simple_screen("cursor")
ScrollbackScreen = _make_simple_screen("scrollback")
PerformanceScreen = _make_simple_screen("performance")
MouseScreen = _make_simple_screen("mouse")
MiscScreen = _make_simple_screen("misc")

SCREEN_MAP: dict[str, type[SettingsScreen]] = {
    "font": FontScreen,
    "colors": ColorsScreen,
    "window": WindowScreen,
    "tabs": TabsScreen,
    "cursor": CursorScreen,
    "scrollback": ScrollbackScreen,
    "performance": PerformanceScreen,
    "keybindings": KeybindingsScreen,
    "mouse": MouseScreen,
    "misc": MiscScreen,
}
