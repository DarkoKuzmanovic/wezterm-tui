import re
import pytest
from wezterm_tui.screens.keybindings import ACTIONS, ALL_ACTIONS


def test_other_option_in_all_actions():
    assert "Other..." in ALL_ACTIONS


def test_custom_action_validation():
    """Custom action names must be alphanumeric + underscores."""
    pattern = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
    assert pattern.match("MyCustomAction")
    assert pattern.match("SomeAction_v2")
    assert not pattern.match("")
    assert not pattern.match("foo bar")
    assert not pattern.match('Foo")')


async def test_other_action_shows_custom_input():
    from textual.widgets import Input, Select
    from wezterm_tui.app import WezTermSettingsApp

    app = WezTermSettingsApp()
    async with app.run_test() as pilot:
        await app._switch_screen("keybindings")
        await pilot.pause()

        screen = app.current_screen
        action_select = screen.query_one("#kb-action", Select)
        action_select.value = "Other..."
        await pilot.pause()

        custom_input = screen.query_one("#kb-custom-action", Input)
        assert custom_input.display is True
