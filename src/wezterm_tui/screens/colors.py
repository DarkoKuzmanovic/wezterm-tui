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

    async def on_mount(self) -> None:
        await self._populate_list(self.schemes)

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

    async def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "scheme-search":
            query = event.value.lower()
            filtered = [s for s in self.schemes if query in s.lower()]
            await self._populate_list(filtered)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id or ""
        if item_id.startswith("scheme-idx-"):
            idx = int(item_id[len("scheme-idx-"):])
            name = self._displayed_schemes[idx]
            self.current_scheme = name
            self.settings.setdefault("colors", {})["color_scheme"] = name
            self.query_one("Label").update(f"Current: {name}")
            # Update prefix markers in-place instead of repopulating
            for i, item in enumerate(self.query_one("#scheme-list", ListView).children):
                scheme_name = self._displayed_schemes[i]
                prefix = " > " if scheme_name == name else "   "
                item.query_one(Static).update(f"{prefix}{scheme_name}")

    def collect_values(self) -> dict:
        return self.settings
