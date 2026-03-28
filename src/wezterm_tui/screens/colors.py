"""Colors settings screen with searchable color scheme selector."""

from __future__ import annotations

from rich.console import Group
from rich.panel import Panel
from rich.text import Text
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Input, Label, ListItem, ListView, Static

from wezterm_tui.color_schemes import load_scheme_names, load_scheme_palettes


class ColorsScreen(VerticalScroll):
    CATEGORY = "colors"
    DEFAULT_CSS = """
    ColorsScreen {
        height: 1fr;
    }
    #colors-layout {
        layout: horizontal;
        height: 1fr;
        margin-top: 1;
    }
    #scheme-picker {
        width: 38;
        min-width: 30;
        height: 1fr;
    }
    #scheme-search {
        margin-bottom: 1;
    }
    #scheme-list {
        height: 1fr;
        border: round $accent;
    }
    #scheme-preview {
        width: 1fr;
        min-height: 20;
    }
    """

    def __init__(self, settings: dict, **kwargs):
        super().__init__(**kwargs)
        self.settings = settings
        self.schemes = load_scheme_names()
        self.scheme_palettes = load_scheme_palettes()
        self.current_scheme = settings.get("colors", {}).get("color_scheme", "")
        self.preview_scheme = self.current_scheme
        self._displayed_schemes: list[str] = []

    def compose(self):
        yield Static(" COLOR SCHEME ", classes="screen-title")
        yield Label(f"Current: {self.current_scheme or 'None'}", id="current-scheme")
        with Horizontal(id="colors-layout"):
            with Vertical(id="scheme-picker"):
                yield Input(placeholder="Search color schemes...", id="scheme-search")
                yield ListView(id="scheme-list")
            yield Static(id="scheme-preview")

    async def on_mount(self) -> None:
        await self._populate_list(self.schemes)
        self._update_preview(self.preview_scheme)

    async def _populate_list(self, schemes: list[str]) -> None:
        list_view = self.query_one("#scheme-list", ListView)
        await list_view.clear()
        self._displayed_schemes = schemes
        items = []
        for idx, name in enumerate(schemes):
            prefix = " > " if name == self.current_scheme else "   "
            items.append(ListItem(Static(f"{prefix}{name}"), id=f"scheme-idx-{idx}"))
        if items:
            await list_view.extend(items)
            focus_name = self.preview_scheme or self.current_scheme
            list_view.index = schemes.index(focus_name) if focus_name in schemes else 0
        else:
            self._update_preview(None, message="No color schemes match your search.")

    async def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "scheme-search":
            query = event.value.lower()
            filtered = [s for s in self.schemes if query in s.lower()]
            await self._populate_list(filtered)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item is None:
            return
        name = self._name_from_item_id(event.item.id)
        if name is None:
            return
        self.preview_scheme = name
        self._update_preview(name)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        name = self._name_from_item_id(event.item.id)
        if name is None:
            return
        self.current_scheme = name
        self.preview_scheme = name
        self.settings.setdefault("colors", {})["color_scheme"] = name
        self.query_one("#current-scheme", Label).update(f"Current: {name}")
        self._refresh_markers()
        self._update_preview(name)

    def _name_from_item_id(self, item_id: str | None) -> str | None:
        if not item_id or not item_id.startswith("scheme-idx-"):
            return None
        idx = int(item_id[len("scheme-idx-"):])
        if idx >= len(self._displayed_schemes):
            return None
        return self._displayed_schemes[idx]

    def _refresh_markers(self) -> None:
        list_view = self.query_one("#scheme-list", ListView)
        for i, item in enumerate(list_view.children):
            scheme_name = self._displayed_schemes[i]
            prefix = " > " if scheme_name == self.current_scheme else "   "
            item.query_one(Static).update(f"{prefix}{scheme_name}")

    def _update_preview(self, scheme_name: str | None, message: str | None = None) -> None:
        self.query_one("#scheme-preview", Static).update(self._render_preview(scheme_name, message))

    def _render_preview(self, scheme_name: str | None, message: str | None = None) -> Panel:
        if message:
            return Panel(message, title=" Preview ", border_style="yellow")

        if not scheme_name:
            return Panel("Select a color scheme to preview it.", title=" Preview ", border_style="yellow")

        palette = self.scheme_palettes.get(scheme_name)
        if palette is None:
            return Panel(
                f"Preview data is unavailable for '{scheme_name}'. You can still select and save it.",
                title=f" Preview: {scheme_name} ",
                border_style="yellow",
            )

        background = str(palette.get("background") or "#1e1e1e")
        foreground = str(palette.get("foreground") or "#d0d0d0")
        cursor = str(palette.get("cursor_bg") or foreground)
        selection_bg = str(palette.get("selection_bg") or "#3a3a3a")
        selection_fg = str(palette.get("selection_fg") or foreground)
        accent_colors = list(palette.get("brights") or []) or list(palette.get("ansi") or [])
        accent = str(accent_colors[4] if len(accent_colors) > 4 else accent_colors[0] if accent_colors else foreground)

        sample_header = Text("Terminal Sample", style=f"bold {foreground}")
        prompt = Text()
        prompt.append("quzma", style=f"bold {accent}")
        prompt.append("@endeavour", style=foreground)
        prompt.append(" ~/source/wezterm-tui", style=f"italic {foreground}")

        command = Text()
        command.append("$ ", style=f"bold {cursor}")
        command.append("wezterm-tui", style=foreground)
        command.append(" --preview", style=accent)

        selection = Text("selected text", style=f"{selection_fg} on {selection_bg}")
        selection.append("  cursor", style=f"bold {cursor}")

        swatches = Text("ANSI    ", style=f"bold {foreground}")
        for color in palette.get("ansi", []):
            swatches.append("  ", style=f"on {color}")
            swatches.append(" ")

        brights = Text("Brights ", style=f"bold {foreground}")
        for color in palette.get("brights", []):
            brights.append("  ", style=f"on {color}")
            brights.append(" ")

        codes = Text()
        codes.append("bg ", style=f"bold {foreground}")
        codes.append(background, style=foreground)
        codes.append("  fg ", style=f"bold {foreground}")
        codes.append(foreground, style=foreground)

        return Panel(
            Group(sample_header, prompt, command, selection, Text(""), swatches, brights, Text(""), codes),
            title=f" Preview: {scheme_name} ",
            border_style=accent,
            style=f"{foreground} on {background}",
            padding=(1, 2),
        )

    def collect_values(self) -> dict:
        return self.settings
