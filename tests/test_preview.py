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
