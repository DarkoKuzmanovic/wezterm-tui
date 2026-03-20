from wezterm_tui.schema import SCHEMA, OptionType, get_defaults, get_category_options, validate_value


def test_schema_has_all_categories():
    categories = {opt.category for opt in SCHEMA}
    expected = {"font", "colors", "window", "tabs", "cursor", "scrollback", "performance", "keybindings", "mouse", "misc"}
    assert categories == expected


def test_get_defaults_returns_nested_dict():
    defaults = get_defaults()
    assert defaults["font"]["family"] == "JetBrains Mono"
    assert defaults["font"]["size"] == 12.0
    assert defaults["cursor"]["default_cursor_style"] == "SteadyBlock"
    assert isinstance(defaults["keybindings"], list)


def test_get_category_options():
    font_opts = get_category_options("font")
    keys = [o.key for o in font_opts]
    assert "family" in keys
    assert "size" in keys


def test_validate_value_enum():
    cursor_opt = next(o for o in SCHEMA if o.key == "default_cursor_style")
    assert validate_value(cursor_opt, "BlinkingBar") is True
    assert validate_value(cursor_opt, "InvalidStyle") is False


def test_validate_value_number_range():
    fps_opt = next(o for o in SCHEMA if o.key == "max_fps")
    assert validate_value(fps_opt, 120) is True
    assert validate_value(fps_opt, -5) is False


def test_validate_value_bool():
    tab_opt = next(o for o in SCHEMA if o.key == "enable_tab_bar")
    assert validate_value(tab_opt, True) is True
    assert validate_value(tab_opt, "yes") is False
