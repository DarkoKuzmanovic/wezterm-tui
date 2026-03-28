from wezterm_tui.history import SettingsHistory


def test_initial_state():
    h = SettingsHistory({"font": {"size": 12}})
    assert not h.can_undo
    assert not h.can_redo


def test_push_and_undo():
    h = SettingsHistory({"font": {"size": 12}})
    h.push({"font": {"size": 14}})
    assert h.can_undo
    result = h.undo()
    assert result == {"font": {"size": 12}}
    assert not h.can_undo


def test_undo_and_redo():
    h = SettingsHistory({"font": {"size": 12}})
    h.push({"font": {"size": 14}})
    h.push({"font": {"size": 16}})
    h.undo()
    assert h.can_redo
    result = h.redo()
    assert result == {"font": {"size": 16}}
    assert not h.can_redo


def test_push_after_undo_truncates_redo():
    h = SettingsHistory({"a": 1})
    h.push({"a": 2})
    h.push({"a": 3})
    h.undo()  # back to {"a": 2}
    h.push({"a": 4})  # truncates {"a": 3}
    assert not h.can_redo
    result = h.undo()
    assert result == {"a": 2}


def test_undo_returns_none_at_bottom():
    h = SettingsHistory({"a": 1})
    assert h.undo() is None


def test_redo_returns_none_at_top():
    h = SettingsHistory({"a": 1})
    assert h.redo() is None


def test_deep_copy_isolation():
    original = {"font": {"size": 12}}
    h = SettingsHistory(original)
    original["font"]["size"] = 999
    h.push({"font": {"size": 14}})
    result = h.undo()
    assert result["font"]["size"] == 12
