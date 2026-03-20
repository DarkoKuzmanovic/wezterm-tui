"""Keybindings screen with table view and add/edit/delete."""

from __future__ import annotations

import json as json_mod

from textual.containers import VerticalScroll, Horizontal
from textual.widgets import Static, Button, DataTable, Input, Select, Label

ACTIONS_NO_ARGS = [
    "IncreaseFontSize", "DecreaseFontSize", "ResetFontSize",
    "Copy", "Paste", "ToggleFullScreen",
    "ShowLauncher", "ShowTabNavigator", "ActivateCommandPalette",
    "QuickSelect", "Nop", "DisableDefaultAssignment",
    "ScrollToTop", "ScrollToBottom",
    "SpawnWindow", "ReloadConfiguration",
]

ACTIONS_STRING_ARG = ["ActivatePaneDirection", "PasteFrom"]

ACTIONS_TABLE_ARG = ["SplitHorizontal", "SplitVertical", "CloseCurrentPane", "SendKey"]

ALL_ACTIONS = sorted(ACTIONS_NO_ARGS + ACTIONS_STRING_ARG + ACTIONS_TABLE_ARG)

MODIFIER_OPTIONS = ["CTRL", "SHIFT", "ALT", "SUPER", "CTRL|SHIFT", "CTRL|ALT", "ALT|SHIFT"]


class KeybindingsScreen(VerticalScroll):
    CATEGORY = "keybindings"

    def __init__(self, settings: dict, **kwargs):
        super().__init__(**kwargs)
        self.settings = settings
        self.keybindings: list[dict] = list(settings.get("keybindings", []))

    def compose(self):
        yield Static(" KEYBINDINGS ", classes="screen-title")
        yield DataTable(id="kb-table")
        with Horizontal(id="kb-buttons"):
            yield Button("Delete Selected", id="kb-delete", variant="error")

        yield Static(" Add Keybinding ", classes="screen-title")
        yield Label("Key")
        yield Input(id="kb-key", placeholder="e.g. d, =, Enter, Tab")
        yield Label("Modifiers")
        yield Select(
            [(m, m) for m in MODIFIER_OPTIONS],
            id="kb-mods", allow_blank=True, prompt="None",
        )
        yield Label("Action")
        yield Select(
            [(a, a) for a in ALL_ACTIONS],
            id="kb-action", allow_blank=False, value=ALL_ACTIONS[0],
        )
        yield Label("Args (optional)")
        yield Input(id="kb-args", placeholder='e.g. Left or {"domain": "CurrentPaneDomain"}')
        yield Button("Add Keybinding", id="kb-confirm-add", variant="primary")

    def on_mount(self) -> None:
        table = self.query_one("#kb-table", DataTable)
        table.add_columns("Key", "Modifiers", "Action", "Args")
        table.cursor_type = "row"
        self._refresh_table()

    def _refresh_table(self) -> None:
        table = self.query_one("#kb-table", DataTable)
        table.clear()
        for kb in self.keybindings:
            args_str = ""
            if "args" in kb:
                args = kb["args"]
                args_str = str(args) if not isinstance(args, str) else args
            table.add_row(kb.get("key", ""), kb.get("mods", ""), kb.get("action", ""), args_str)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "kb-delete":
            table = self.query_one("#kb-table", DataTable)
            if table.cursor_row is not None and 0 <= table.cursor_row < len(self.keybindings):
                self.keybindings.pop(table.cursor_row)
                self._refresh_table()

        elif event.button.id == "kb-confirm-add":
            key_input = self.query_one("#kb-key", Input)
            mods_select = self.query_one("#kb-mods", Select)
            action_select = self.query_one("#kb-action", Select)
            args_input = self.query_one("#kb-args", Input)

            key = key_input.value.strip()
            if not key:
                return

            binding: dict = {"key": key}

            mods = mods_select.value
            if mods is not Select.BLANK and mods:
                binding["mods"] = mods

            action = action_select.value
            if action is not Select.BLANK:
                binding["action"] = action

            args_raw = args_input.value.strip()
            if args_raw:
                try:
                    binding["args"] = json_mod.loads(args_raw)
                except json_mod.JSONDecodeError:
                    binding["args"] = args_raw

            self.keybindings.append(binding)
            self._refresh_table()
            key_input.value = ""
            args_input.value = ""

    def collect_values(self) -> dict:
        self.settings["keybindings"] = self.keybindings
        return self.settings
