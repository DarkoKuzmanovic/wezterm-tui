import pytest
from wezterm_tui.app import WezTermSettingsApp
from wezterm_tui.screens import SCREEN_MAP


async def test_app_starts():
    app = WezTermSettingsApp()
    async with app.run_test() as pilot:
        assert app.title == "WezTerm Settings"
        assert app.active_category == "font"


async def test_sidebar_navigation():
    app = WezTermSettingsApp()
    async with app.run_test() as pilot:
        sidebar = app.query_one("#sidebar")
        items = sidebar.query("ListItem")
        assert len(items) == 10


@pytest.mark.parametrize("category", list(SCREEN_MAP.keys()))
async def test_screen_renders(category):
    """Verify each settings screen mounts without errors."""
    app = WezTermSettingsApp()
    async with app.run_test() as pilot:
        await app._switch_screen(category)
        await pilot.pause()
        # Verify the screen mounted
        content = app.query_one("#content-area")
        assert content.children
