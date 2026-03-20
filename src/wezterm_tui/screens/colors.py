"""Colors settings screen with searchable color scheme selector."""

from __future__ import annotations

import json
from importlib import resources

from textual.containers import VerticalScroll
from textual.widgets import Static, Input, ListView, ListItem, Label


class ColorsScreen(VerticalScroll):
    CATEGORY = "colors"

    def __init__(self, settings: dict, **kwargs):
        super().__init__(**kwargs)
        self.settings = settings
        self.schemes = self._load_schemes()
        self.current_scheme = settings.get("colors", {}).get("color_scheme", "")
        self._displayed_schemes: list[str] = []

    def _load_schemes(self) -> list[str]:
        data_path = resources.files("wezterm_tui") / "data" / "color_schemes.json"
        return json.loads(data_path.read_text())

    def compose(self):
        yield Static(" COLOR SCHEME ", classes="screen-title")
        yield Label(f"Current: {self.current_scheme}")
        yield Input(placeholder="Search color schemes...", id="scheme-search")
        yield ListView(id="scheme-list")

    def on_mount(self) -> None:
        self._populate_list(self.schemes)

    def _populate_list(self, schemes: list[str]) -> None:
        list_view = self.query_one("#scheme-list", ListView)
        list_view.clear()
        self._displayed_schemes = schemes
        for idx, name in enumerate(schemes):
            prefix = " > " if name == self.current_scheme else "   "
            list_view.append(ListItem(Static(f"{prefix}{name}"), id=f"scheme-idx-{idx}"))

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "scheme-search":
            query = event.value.lower()
            filtered = [s for s in self.schemes if query in s.lower()]
            self._populate_list(filtered)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id or ""
        if item_id.startswith("scheme-idx-"):
            idx = int(item_id[len("scheme-idx-"):])
            name = self._displayed_schemes[idx]
            self.current_scheme = name
            self.settings.setdefault("colors", {})["color_scheme"] = name
            self.query_one("Label").update(f"Current: {name}")
            search_val = self.query_one("#scheme-search", Input).value
            if search_val:
                filtered = [s for s in self.schemes if search_val.lower() in s.lower()]
            else:
                filtered = self.schemes
            self._populate_list(filtered)

    def collect_values(self) -> dict:
        return self.settings
