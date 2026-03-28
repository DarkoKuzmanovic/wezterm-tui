import pytest
from wezterm_tui.schema import Option, OptionType


def test_int_input_validates_range():
    """Verify that INT options with min/max produce validators."""
    opt = Option("max_fps", "performance", "Max FPS", OptionType.INT, 60,
                 min_value=1, max_value=255)
    assert opt.min_value == 1
    assert opt.max_value == 255


def test_float_input_validates_range():
    """Verify that FLOAT options with min/max produce validators."""
    opt = Option("background_opacity", "window", "Background Opacity",
                 OptionType.FLOAT, 1.0, min_value=0.0, max_value=1.0)
    assert opt.min_value == 0.0
    assert opt.max_value == 1.0


async def test_invalid_input_gets_visual_feedback():
    """An out-of-range number in an Input should have the -invalid CSS class."""
    from wezterm_tui.app import WezTermSettingsApp

    app = WezTermSettingsApp()
    async with app.run_test() as pilot:
        await app._switch_screen("performance")
        await pilot.pause()

        screen = app.current_screen
        from textual.widgets import Input
        fps_input = screen.query_one("#field-performance-max_fps", Input)

        # Set an invalid value (over max of 255)
        fps_input.value = "999"
        await pilot.pause()

        assert fps_input.has_class("-invalid")

        # Set a valid value
        fps_input.value = "120"
        await pilot.pause()

        assert not fps_input.has_class("-invalid")
