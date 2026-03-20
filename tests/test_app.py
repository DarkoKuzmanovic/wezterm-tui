from wezterm_tui.app import WezTermSettingsApp


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
