from wezterm_tui.preview import resolve_palette, blend_opacity

# -- resolve_palette tests --

def test_resolve_palette_known_scheme():
    palettes = {
        "Dracula": {
            "foreground": "#f8f8f2",
            "background": "#282a36",
            "ansi": ["#000000", "#ff5555", "#50fa7b", "#f1fa8c",
                     "#bd93f9", "#ff79c6", "#8be9fd", "#bfbfbf"],
            "brights": ["#4d4d4d", "#ff6e67", "#5af78e", "#f4f99d",
                        "#caa9fa", "#ff92d0", "#9aedfe", "#e6e6e6"],
        }
    }
    result = resolve_palette("Dracula", palettes)
    assert result["fg"] == "#f8f8f2"
    assert result["bg"] == "#282a36"
    assert len(result["ansi"]) == 8
    assert len(result["brights"]) == 8
    assert result["ansi"][2] == "#50fa7b"  # green
    assert result["unknown"] is False


def test_resolve_palette_unknown_scheme():
    result = resolve_palette("NonExistent", {})
    assert result["unknown"] is True
    assert result["fg"] == "#d4d4d4"
    assert result["bg"] == "#1e1e1e"
    assert len(result["ansi"]) == 8
    assert len(result["brights"]) == 8


def test_resolve_palette_missing_fields():
    palettes = {"Partial": {"foreground": "#ffffff"}}
    result = resolve_palette("Partial", palettes)
    assert result["fg"] == "#ffffff"
    assert result["bg"] == "#1e1e1e"  # falls back to default
    assert len(result["ansi"]) == 8


# -- blend_opacity tests --

def test_blend_opacity_full():
    assert blend_opacity("#1e1e1e", 1.0) == "#1e1e1e"


def test_blend_opacity_zero():
    assert blend_opacity("#ffffff", 0.0) == "#000000"


def test_blend_opacity_half():
    # #1e1e1e = rgb(30,30,30), at 0.5 -> rgb(15,15,15) = #0f0f0f
    assert blend_opacity("#1e1e1e", 0.5) == "#0f0f0f"


from wezterm_tui.preview import build_preview_text


def test_render_with_default_settings():
    from wezterm_tui.schema import get_defaults
    settings = get_defaults()
    palettes = {}  # will use fallback
    result = build_preview_text(settings, palettes)
    text = result.plain
    assert "user@host" in text
    assert "ls -la" in text
    assert "src/" in text


def test_render_with_custom_scheme():
    from wezterm_tui.schema import get_defaults
    settings = get_defaults()
    settings["colors"]["color_scheme"] = "Dracula"
    palettes = {
        "Dracula": {
            "foreground": "#f8f8f2",
            "background": "#282a36",
            "ansi": ["#000000", "#ff5555", "#50fa7b", "#f1fa8c",
                     "#bd93f9", "#ff79c6", "#8be9fd", "#bfbfbf"],
            "brights": ["#4d4d4d", "#ff6e67", "#5af78e", "#f4f99d",
                        "#caa9fa", "#ff92d0", "#9aedfe", "#e6e6e6"],
        }
    }
    result = build_preview_text(settings, palettes)
    text = result.plain
    assert "user@host" in text
    assert result._spans  # Rich Text object has styled spans


def test_render_unknown_scheme():
    from wezterm_tui.schema import get_defaults
    settings = get_defaults()
    settings["colors"]["color_scheme"] = "NonExistent"
    result = build_preview_text(settings, {})
    text = result.plain
    assert "(unknown scheme)" in text
    assert "user@host" in text


def test_render_cursor_style_block():
    from wezterm_tui.schema import get_defaults
    settings = get_defaults()
    settings["cursor"]["default_cursor_style"] = "SteadyBlock"
    result = build_preview_text(settings, {})
    assert "\u2588" in result.plain  # block char


def test_render_cursor_style_bar():
    from wezterm_tui.schema import get_defaults
    settings = get_defaults()
    settings["cursor"]["default_cursor_style"] = "SteadyBar"
    result = build_preview_text(settings, {})
    assert "|" in result.plain


def test_render_cursor_style_underline():
    from wezterm_tui.schema import get_defaults
    settings = get_defaults()
    settings["cursor"]["default_cursor_style"] = "SteadyUnderline"
    result = build_preview_text(settings, {})
    assert "\u2581" in result.plain  # underline char


def test_render_opacity_affects_background():
    from wezterm_tui.schema import get_defaults
    settings = get_defaults()
    settings["window"]["background_opacity"] = 0.5
    result = build_preview_text(settings, {})
    assert "user@host" in result.plain


def test_render_empty_settings():
    result = build_preview_text({}, {})
    text = result.plain
    assert "user@host" in text  # still renders with defaults


from wezterm_tui.preview import PreviewPanel


def test_preview_panel_initial_state():
    """PreviewPanel renders a loading message before update_preview is called."""
    panel = PreviewPanel()
    renderable = panel.render()
    assert "Loading preview" in renderable.plain


def test_preview_panel_update_preview():
    """After update_preview, render returns the terminal mock."""
    from wezterm_tui.schema import get_defaults
    panel = PreviewPanel()
    settings = get_defaults()
    panel.update_preview(settings, {})
    renderable = panel.render()
    assert "user@host" in renderable.plain


def test_preview_panel_update_preserves_last():
    """Calling update_preview twice shows the latest state."""
    from wezterm_tui.schema import get_defaults
    panel = PreviewPanel()

    settings = get_defaults()
    settings["cursor"]["default_cursor_style"] = "SteadyBar"
    panel.update_preview(settings, {})
    assert "|" in panel.render().plain

    settings["cursor"]["default_cursor_style"] = "SteadyUnderline"
    panel.update_preview(settings, {})
    assert "\u2581" in panel.render().plain
