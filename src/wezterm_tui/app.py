"""Main WezTerm TUI Settings application."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Static, Button, ListItem, ListView
from textual.binding import Binding

from wezterm_tui.config import load_settings, save_settings, get_config_dir
from wezterm_tui.lua_gen import generate_lua
from wezterm_tui.importer import import_from_file
from wezterm_tui.schema import CATEGORIES
from wezterm_tui.screens import SCREEN_MAP


class Sidebar(ListView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.categories = CATEGORIES

    def compose(self) -> ComposeResult:
        for cat_id, cat_label in self.categories:
            yield ListItem(Static(f" {cat_label}"), id=f"cat-{cat_id}")


class WezTermSettingsApp(App):
    TITLE = "WezTerm Settings"
    CSS = """
    Screen {
        layout: vertical;
    }
    #main-container {
        layout: horizontal;
        height: 1fr;
    }
    Sidebar {
        width: 20;
        border-right: solid $accent;
        background: $surface;
    }
    Sidebar > ListItem {
        padding: 0 1;
    }
    Sidebar > ListItem.--highlight {
        background: $accent;
    }
    #content-area {
        width: 1fr;
        padding: 1 2;
    }
    .screen-title {
        text-style: bold;
        margin-bottom: 1;
        color: $text;
        background: $accent;
        padding: 0 1;
        width: 100%;
    }
    Label {
        margin-top: 1;
        color: $text-muted;
    }
    Input {
        margin-bottom: 0;
    }
    Input.-invalid {
        border: tall $error;
    }
    Switch {
        margin-bottom: 0;
    }
    Select {
        margin-bottom: 0;
    }
    #footer-bar {
        layout: horizontal;
        height: 3;
        dock: bottom;
        padding: 0 2;
        background: $surface;
        border-top: solid $accent;
    }
    #footer-bar Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+r", "reset", "Reset"),
        Binding("ctrl+i", "import_config", "Import"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.config_dir = get_config_dir()
        self.json_path = self.config_dir / "settings.json"
        self.lua_path = self.config_dir / "settings.lua"
        self.settings = load_settings(self.json_path)
        self.active_category = "font"
        self.current_screen = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-container"):
            yield Sidebar(id="sidebar")
            with Vertical(id="content-area"):
                pass
        with Horizontal(id="footer-bar"):
            yield Button("Save [^S]", id="btn-save", variant="success")
            yield Button("Reset [^R]", id="btn-reset", variant="warning")
            yield Button("Import [^I]", id="btn-import", variant="default")
        yield Footer()

    async def on_mount(self) -> None:
        await self._switch_screen("font")
        sidebar = self.query_one("#sidebar", Sidebar)
        sidebar.index = 0

    async def _switch_screen(self, category: str) -> None:
        self.active_category = category
        if self.current_screen is not None:
            try:
                self.current_screen.collect_values()
            except Exception as exc:
                self.notify(
                    f"Could not save values: {exc}",
                    title="Warning",
                    severity="warning",
                )
        content = self.query_one("#content-area")
        await content.remove_children()
        screen_class = SCREEN_MAP[category]
        self.current_screen = screen_class(self.settings, id="active-screen")
        await content.mount(self.current_screen)

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id
        if item_id and item_id.startswith("cat-"):
            category = item_id[4:]
            await self._switch_screen(category)

    def action_save(self) -> None:
        if self.current_screen:
            self.current_screen.collect_values()
        save_settings(self.json_path, self.settings)
        lua_code = generate_lua(self.settings)
        self.lua_path.write_text(lua_code)
        self.notify("Settings saved!", title="WezTerm TUI")

    async def action_reset(self) -> None:
        self.settings = load_settings(self.json_path)
        await self._switch_screen(self.active_category)
        self.notify("Settings reset to last save.", title="WezTerm TUI")

    async def action_import_config(self) -> None:
        wezterm_lua = self.config_dir / "wezterm.lua"
        if not wezterm_lua.exists():
            self.notify("No wezterm.lua found!", title="Import", severity="error")
            return
        self.settings = import_from_file(wezterm_lua)
        await self._switch_screen(self.active_category)
        self.notify("Imported from wezterm.lua!", title="Import")
