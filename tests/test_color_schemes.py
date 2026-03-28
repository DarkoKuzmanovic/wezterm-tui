from wezterm_tui import color_schemes


def teardown_function():
    color_schemes.load_scheme_palettes.cache_clear()


def test_load_scheme_names_prefers_wezterm_palettes(monkeypatch):
    monkeypatch.setattr(
        color_schemes,
        "_dump_wezterm_palettes",
        lambda: {"Gruvbox Dark": {}, "Dracula": {}},
    )

    assert color_schemes.load_scheme_names() == ["Dracula", "Gruvbox Dark"]


def test_load_scheme_names_falls_back_to_bundled_names(monkeypatch):
    monkeypatch.setattr(color_schemes, "_dump_wezterm_palettes", lambda: {})
    monkeypatch.setattr(color_schemes, "_load_bundled_names", lambda: ["Builtin One", "Builtin Two"])

    assert color_schemes.load_scheme_names() == ["Builtin One", "Builtin Two"]
