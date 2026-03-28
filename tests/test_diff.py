from wezterm_tui.diff import compute_diff, format_diff_text


def test_no_changes():
    old = {"font": {"size": 12}, "colors": {"color_scheme": "Default"}}
    new = {"font": {"size": 12}, "colors": {"color_scheme": "Default"}}
    assert compute_diff(old, new) == []


def test_changed_value():
    old = {"font": {"size": 12, "family": "Mono"}}
    new = {"font": {"size": 14, "family": "Mono"}}
    diff = compute_diff(old, new)
    assert len(diff) == 1
    assert diff[0] == ("font", "size", 12, 14)


def test_multiple_changes():
    old = {"font": {"size": 12}, "colors": {"color_scheme": "Default"}}
    new = {"font": {"size": 14}, "colors": {"color_scheme": "Dracula"}}
    diff = compute_diff(old, new)
    assert len(diff) == 2


def test_added_key():
    old = {"font": {"size": 12}}
    new = {"font": {"size": 12}, "colors": {"color_scheme": "Dracula"}}
    diff = compute_diff(old, new)
    assert ("colors", "color_scheme", None, "Dracula") in diff


def test_skips_internal_keys():
    old = {"_version": 1, "font": {"size": 12}}
    new = {"_version": 2, "font": {"size": 12}}
    assert compute_diff(old, new) == []


def test_keybindings_diff():
    old = {"keybindings": []}
    new = {"keybindings": [{"key": "a", "mods": "CTRL", "action": "Copy"}]}
    diff = compute_diff(old, new)
    assert len(diff) == 1
    assert diff[0][0] == "keybindings"


def test_format_diff_text():
    changes = [("font", "size", 12, 14), ("colors", "color_scheme", "Default", "Dracula")]
    text = format_diff_text(changes)
    assert "font.size" in text
    assert "12" in text
    assert "14" in text
