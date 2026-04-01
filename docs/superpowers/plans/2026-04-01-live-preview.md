# Live Preview Pane Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a bottom-panel live preview that renders a Rich Text terminal mock, updating via debounce as users change visual settings (font, colors, cursor, window).

**Architecture:** A standalone `PreviewPanel(Static)` widget in `preview.py` with a pure `build_preview_text()` rendering function. The app mounts it below the sidebar+content row and wires debounced refresh via `Input.Changed`, `Switch.Changed`, `Select.Changed` handlers.

**Tech Stack:** Python 3.12+, Textual 3.0+, Rich `Text`/`Style`/`Color`

**Spec:** `docs/superpowers/specs/2026-04-01-live-preview-design.md`

---

### Task 1: Pure rendering helpers — color resolution and opacity blending

**Files:**
- Create: `src/wezterm_tui/preview.py`
- Test: `tests/test_preview.py`

This task builds the foundational helper functions that the preview renderer depends on. All are pure functions with no Textual dependency.

- [ ] **Step 1: Write failing tests for color resolution and opacity blending**

```python
# tests/test_preview.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_preview.py -v`
Expected: FAIL — `ImportError: cannot import name 'resolve_palette' from 'wezterm_tui.preview'`

- [ ] **Step 3: Implement resolve_palette and blend_opacity**

```python
# src/wezterm_tui/preview.py
"""Live preview panel for WezTerm settings."""

from __future__ import annotations

_DEFAULT_FG = "#d4d4d4"
_DEFAULT_BG = "#1e1e1e"
_DEFAULT_ANSI = [
    "#000000", "#cd3131", "#0dbc79", "#e5e510",
    "#2472c8", "#bc3fbc", "#11a8cd", "#e5e5e5",
]
_DEFAULT_BRIGHTS = [
    "#666666", "#f14c4c", "#23d18b", "#f5f543",
    "#3b8eea", "#d670d6", "#29b8db", "#e5e5e5",
]


def resolve_palette(scheme_name: str, palettes: dict) -> dict:
    """Look up a color scheme palette, falling back to defaults."""
    scheme = palettes.get(scheme_name)
    if scheme is None:
        return {
            "fg": _DEFAULT_FG,
            "bg": _DEFAULT_BG,
            "ansi": list(_DEFAULT_ANSI),
            "brights": list(_DEFAULT_BRIGHTS),
            "unknown": True,
        }
    return {
        "fg": scheme.get("foreground", _DEFAULT_FG),
        "bg": scheme.get("background", _DEFAULT_BG),
        "ansi": scheme.get("ansi", list(_DEFAULT_ANSI)),
        "brights": scheme.get("brights", list(_DEFAULT_BRIGHTS)),
        "unknown": False,
    }


def blend_opacity(hex_color: str, opacity: float) -> str:
    """Blend a hex color toward black by opacity (1.0 = unchanged, 0.0 = black)."""
    opacity = max(0.0, min(1.0, opacity))
    hex_color = hex_color.lstrip("#")
    r = int(int(hex_color[0:2], 16) * opacity)
    g = int(int(hex_color[2:4], 16) * opacity)
    b = int(int(hex_color[4:6], 16) * opacity)
    return f"#{r:02x}{g:02x}{b:02x}"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_preview.py -v`
Expected: All 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/wezterm_tui/preview.py tests/test_preview.py
git commit -m "feat(preview): add color resolution and opacity blending helpers"
```

---

### Task 2: Pure rendering function — build_preview_text()

**Files:**
- Modify: `src/wezterm_tui/preview.py`
- Modify: `tests/test_preview.py`

This task builds the core rendering function that takes settings + palette and produces a Rich `Text` object. It is a pure function with no Textual widget dependency.

- [ ] **Step 1: Write failing tests for build_preview_text**

Append to `tests/test_preview.py`:

```python
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
    # Verify the Rich Text has styles applied (not just plain text)
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
    assert "\u2588" in result.plain  # █


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
    assert "\u2581" in result.plain  # ▁


def test_render_opacity_affects_background():
    from wezterm_tui.schema import get_defaults
    settings = get_defaults()
    settings["window"]["background_opacity"] = 0.5
    result = build_preview_text(settings, {})
    # The text should still render (not crash)
    assert "user@host" in result.plain


def test_render_empty_settings():
    result = build_preview_text({}, {})
    text = result.plain
    assert "user@host" in text  # still renders with defaults
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_preview.py::test_render_with_default_settings -v`
Expected: FAIL — `ImportError: cannot import name 'build_preview_text'`

- [ ] **Step 3: Implement build_preview_text**

Add to `src/wezterm_tui/preview.py` after the existing helper functions:

```python
from rich.text import Text
from rich.style import Style
from rich.color import Color


_CURSOR_CHARS = {
    "SteadyBlock": "\u2588",
    "BlinkingBlock": "\u2588",
    "SteadyBar": "|",
    "BlinkingBar": "|",
    "SteadyUnderline": "\u2581",
    "BlinkingUnderline": "\u2581",
}


def _get_setting(settings: dict, category: str, key: str, default):
    """Safely get a nested setting value."""
    return settings.get(category, {}).get(key, default)


def build_preview_text(settings: dict, palettes: dict) -> Text:
    """Build a Rich Text object simulating a terminal session.

    Pure function: settings dict + palettes dict in, Rich Text out.
    """
    # Resolve colors
    scheme_name = _get_setting(settings, "colors", "color_scheme", "Default (Dark)")
    palette = resolve_palette(scheme_name, palettes)
    fg = palette["fg"]
    bg = palette["bg"]
    ansi = palette["ansi"]
    brights = palette["brights"]

    # Resolve visual settings
    font_family = _get_setting(settings, "font", "family", "JetBrains Mono")
    font_size = _get_setting(settings, "font", "size", 12.0)
    font_weight = _get_setting(settings, "font", "weight", "Regular")
    line_height = _get_setting(settings, "font", "line_height", 1.0)

    cursor_style = _get_setting(settings, "cursor", "default_cursor_style", "SteadyBlock")
    cursor_blink = "blink" if "Blinking" in cursor_style else "steady"
    cursor_char = _CURSOR_CHARS.get(cursor_style, "\u2588")
    cursor_label = cursor_style.replace("Steady", "").replace("Blinking", "").lower()

    opacity = _get_setting(settings, "window", "background_opacity", 1.0)
    if not isinstance(opacity, (int, float)):
        opacity = 1.0
    padding = _get_setting(settings, "window", "padding", {"left": 0, "right": 0, "top": 0, "bottom": 0})
    if not isinstance(padding, dict):
        padding = {"left": 0, "right": 0, "top": 0, "bottom": 0}

    # Apply opacity to background
    effective_bg = blend_opacity(bg, opacity)

    # Build styles
    bg_color = Color.parse(effective_bg)
    base = Style(color=fg, bgcolor=bg_color)
    dim = Style(color=fg, bgcolor=bg_color, dim=True)
    green = Style(color=ansi[2], bgcolor=bg_color, bold=True)
    cyan = Style(color=ansi[6], bgcolor=bg_color)
    blue = Style(color=ansi[4], bgcolor=bg_color)
    magenta = Style(color=ansi[5], bgcolor=bg_color)
    bright_fg = Style(color=brights[7] if len(brights) > 7 else fg, bgcolor=bg_color, bold=True)
    rule_style = Style(color=brights[0] if brights else "#666666", bgcolor=bg_color)

    # Compose the text
    text = Text()

    # Line 1: font info + opacity
    info_left = f" {font_family}  {font_size}pt  {font_weight}"
    opacity_str = f"opacity: {opacity:.2f}"
    if palette["unknown"]:
        opacity_str += "  (unknown scheme)"
    text.append(info_left, style=dim)
    # Pad to push opacity right (approximate — Textual will handle width)
    gap = max(1, 40 - len(info_left))
    text.append(" " * gap, style=base)
    text.append(opacity_str, style=dim)
    text.append("\n")

    # Line 2: horizontal rule
    text.append(" " + "\u2500" * 62, style=rule_style)
    text.append("\n")

    # Line 3: prompt + command
    text.append(" ", style=base)
    text.append("user@host", style=green)
    text.append(" ", style=base)
    text.append("~", style=cyan)
    text.append(" $ ", style=base)
    text.append("ls -la", style=base)
    text.append("\n")

    # Lines 4-6: file listing
    text.append(" drwxr-xr-x  5 user staff  160 Mar 28 10:00 ", style=base)
    text.append("src/", style=blue)
    text.append("\n")

    text.append(" -rw-r--r--  1 user staff 4096 Mar 28 09:45 ", style=base)
    text.append("README.md", style=base)
    text.append("\n")

    text.append(" -rwxr-xr-x  1 user staff  512 Mar 27 14:20 ", style=base)
    text.append("run.sh", style=magenta)
    text.append("\n")

    # Line 7: second prompt with cursor
    text.append(" ", style=base)
    text.append("user@host", style=green)
    text.append(" ", style=base)
    text.append("~", style=cyan)
    text.append(" $ ", style=base)
    text.append(cursor_char, style=bright_fg)
    text.append("\n")

    # Line 8: horizontal rule
    text.append(" " + "\u2500" * 62, style=rule_style)
    text.append("\n")

    # Line 9: status strip
    pad_l = padding.get("left", 0)
    pad_r = padding.get("right", 0)
    pad_t = padding.get("top", 0)
    pad_b = padding.get("bottom", 0)
    status = f" padding: {pad_l}/{pad_r}/{pad_t}/{pad_b}  cursor: {cursor_label}, {cursor_blink}  line-height: {line_height}"
    text.append(status, style=dim)

    return text
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_preview.py -v`
Expected: All 14 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/wezterm_tui/preview.py tests/test_preview.py
git commit -m "feat(preview): add build_preview_text rendering function"
```

---

### Task 3: PreviewPanel Textual widget

**Files:**
- Modify: `src/wezterm_tui/preview.py`
- Modify: `tests/test_preview.py`

This task wraps the pure rendering function in a Textual `Static` widget with `update_preview()` and `render()` methods, plus a loading placeholder state.

- [ ] **Step 1: Write failing tests for PreviewPanel**

Append to `tests/test_preview.py`:

```python
from wezterm_tui.preview import PreviewPanel


def test_preview_panel_initial_state():
    """PreviewPanel renders a loading message before update_preview is called."""
    panel = PreviewPanel()
    renderable = panel.render()
    # Before any update, should show loading text
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_preview.py::test_preview_panel_initial_state -v`
Expected: FAIL — `ImportError: cannot import name 'PreviewPanel'`

- [ ] **Step 3: Implement PreviewPanel class**

Add to the end of `src/wezterm_tui/preview.py`:

```python
from textual.widgets import Static
from textual.app import RenderableType


class PreviewPanel(Static):
    """Bottom-panel live preview showing a Rich Text terminal mock."""

    DEFAULT_CSS = """
    PreviewPanel {
        height: 10;
        border-top: tall $accent;
        padding: 0 1;
        background: $surface;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._renderable: Text = Text("Loading preview...", style="dim")

    def update_preview(self, settings: dict, palettes: dict) -> None:
        """Rebuild the preview from current settings and palettes."""
        self._renderable = build_preview_text(settings, palettes)

    def render(self) -> RenderableType:
        return self._renderable
```

Note: The `from textual.widgets import Static` and `from textual.app import RenderableType` imports go at the top of the file with the other imports.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_preview.py -v`
Expected: All 17 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/wezterm_tui/preview.py tests/test_preview.py
git commit -m "feat(preview): add PreviewPanel Textual widget"
```

---

### Task 4: App layout integration — mount PreviewPanel

**Files:**
- Modify: `src/wezterm_tui/app.py`

This task changes the app's `compose()` to mount the `PreviewPanel` below the sidebar+content row, and loads palettes on mount.

- [ ] **Step 1: Add import to app.py**

At the top of `src/wezterm_tui/app.py`, add to the imports:

```python
from wezterm_tui.preview import PreviewPanel
from wezterm_tui.color_schemes import load_scheme_palettes
```

- [ ] **Step 2: Add palette cache to __init__**

In `WezTermSettingsApp.__init__`, after `self.current_screen = None`, add:

```python
        self._palettes: dict = {}
        self._preview_timer = None
```

- [ ] **Step 3: Change compose() layout**

Replace the `compose` method body in `WezTermSettingsApp`. The current code:

```python
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-container"):
            yield Sidebar(id="sidebar")
            with Vertical(id="content-area"):
                pass
        with Horizontal(id="footer-bar"):
            yield Button("Save [^S]", id="btn-save", variant="success")
            yield Button("Reset [^R]", id="btn-reset", variant="warning")
            yield Button("Import [^I]", id="btn-import", variant="default")
            yield Button("Diff [^D]", id="btn-diff", variant="default")
            yield Button("Profiles [^P]", id="btn-profiles", variant="default")
            yield Button("Export [^E]", id="btn-export", variant="default")
        yield Footer()
```

Replace with:

```python
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="app-body"):
            with Horizontal(id="main-container"):
                yield Sidebar(id="sidebar")
                with Vertical(id="content-area"):
                    pass
            yield PreviewPanel(id="preview-panel")
        with Horizontal(id="footer-bar"):
            yield Button("Save [^S]", id="btn-save", variant="success")
            yield Button("Reset [^R]", id="btn-reset", variant="warning")
            yield Button("Import [^I]", id="btn-import", variant="default")
            yield Button("Diff [^D]", id="btn-diff", variant="default")
            yield Button("Profiles [^P]", id="btn-profiles", variant="default")
            yield Button("Export [^E]", id="btn-export", variant="default")
        yield Footer()
```

- [ ] **Step 4: Add CSS for the new layout**

In the `CSS` string of `WezTermSettingsApp`, add after the `#main-container` rule:

```css
    #app-body {
        height: 1fr;
    }
```

And update `#main-container` to use `height: 1fr;` so it fills the remaining space above the preview:

```css
    #main-container {
        layout: horizontal;
        height: 1fr;
    }
```

(The `height: 1fr` is already on `#main-container` — no change needed there. Just add `#app-body`.)

- [ ] **Step 5: Add _refresh_preview helper and load palettes on mount**

Add the `_refresh_preview` method to `WezTermSettingsApp`, after `on_mount`:

```python
    def _refresh_preview(self) -> None:
        """Update the preview panel with current settings."""
        try:
            panel = self.query_one("#preview-panel", PreviewPanel)
            panel.update_preview(self.settings, self._palettes)
            panel.refresh()
        except Exception:
            pass  # Preview is non-critical; never crash the app
```

Then in `WezTermSettingsApp.on_mount`, after the existing code, add palette loading and initial preview update:

```python
    async def on_mount(self) -> None:
        saved_theme = self.settings.get("_app", {}).get("theme")
        if saved_theme:
            self.theme = saved_theme
        self._theme_ready = True
        await self._switch_screen("font")
        sidebar = self.query_one("#sidebar", Sidebar)
        sidebar.index = 0
        self._palettes = load_scheme_palettes()
        self._refresh_preview()
```

- [ ] **Step 6: Verify the app starts without errors**

Run: `python -m wezterm_tui`
Expected: App launches with the preview panel visible at the bottom showing a terminal mock with default settings. Press Ctrl+Q to exit.

- [ ] **Step 7: Commit**

```bash
git add src/wezterm_tui/app.py
git commit -m "feat(preview): mount PreviewPanel in app layout"
```

---

### Task 5: Debounced refresh wiring

**Files:**
- Modify: `src/wezterm_tui/app.py`

This task adds the debounced preview refresh mechanism. When any `Input.Changed`, `Switch.Changed`, or `Select.Changed` event fires, the app schedules a 300ms timer that collects current settings and updates the preview.

- [ ] **Step 1: Add _schedule_preview_refresh debounce method**

Add this method to `WezTermSettingsApp`, after `_refresh_preview`:

```python
    def _schedule_preview_refresh(self) -> None:
        """Schedule a debounced preview update (300ms)."""
        if self._preview_timer is not None:
            self._preview_timer.stop()
        self._preview_timer = self.set_timer(
            0.3,
            self._do_preview_refresh,
        )

    def _do_preview_refresh(self) -> None:
        """Collect current widget values and refresh the preview."""
        self._preview_timer = None
        if self.current_screen:
            try:
                self.current_screen.collect_values()
            except Exception:
                pass  # Screen may be transitioning
        self._refresh_preview()
```

- [ ] **Step 2: Add event handlers for widget changes**

Add these message handlers to `WezTermSettingsApp`:

```python
    def on_input_changed(self, event: Input.Changed) -> None:
        self._schedule_preview_refresh()

    def on_switch_changed(self, event) -> None:
        self._schedule_preview_refresh()

    def on_select_changed(self, event) -> None:
        self._schedule_preview_refresh()
```

- [ ] **Step 3: Add preview refresh after screen switches**

In `_switch_screen`, after mounting the new screen (after `await content.mount(self.current_screen)`), add:

```python
        self._refresh_preview()
```

Also add a `_refresh_preview()` call at the end of `action_reset`, `action_import_config`, `action_undo`, and `action_redo` — these all replace `self.settings` and switch screens, so the preview should update immediately after:

In `action_reset`, after `await self._switch_screen(self.active_category)`:
```python
        self._refresh_preview()
```

In `action_import_config`, after `await self._switch_screen(self.active_category)`:
```python
        self._refresh_preview()
```

In `action_undo`, after `await self._switch_screen(self.active_category, _skip_history=True)`:
```python
        self._refresh_preview()
```

In `action_redo`, after `await self._switch_screen(self.active_category, _skip_history=True)`:
```python
        self._refresh_preview()
```

- [ ] **Step 4: Verify debounced preview works**

Run: `python -m wezterm_tui`
Expected:
1. Navigate to Font category — preview shows current font info
2. Change font size from 12 to 14 — preview updates ~300ms after typing stops, shows "14.0pt"
3. Navigate to Cursor category — change cursor style to BlinkingBar — preview cursor changes to `|`
4. Navigate to Colors — pick a different scheme — preview colors update
5. Press Ctrl+Q to exit

- [ ] **Step 5: Commit**

```bash
git add src/wezterm_tui/app.py
git commit -m "feat(preview): wire debounced refresh on widget changes"
```

---

### Task 6: Run full test suite and final cleanup

**Files:**
- All modified files

- [ ] **Step 1: Run the full test suite**

Run: `pytest -v`
Expected: All existing tests still pass, plus 17 new tests in `test_preview.py`. Zero failures.

- [ ] **Step 2: Fix any failures**

If any existing tests broke (unlikely since we only added new widgets and event handlers), investigate and fix. The most likely issue would be test_app.py if it snapshot-tests the compose output — update expected output to include the new `#app-body` container and `#preview-panel`.

- [ ] **Step 3: Manual smoke test**

Run: `python -m wezterm_tui`
Walk through each category and verify:
1. Preview is always visible at bottom
2. Changing font family/size/weight updates the preview header strip
3. Changing color scheme updates all preview colors
4. Changing cursor style updates the cursor character
5. Changing opacity updates the preview background darkness
6. Changing window padding updates the status strip
7. Undo/redo updates the preview
8. Import updates the preview
9. Profile load updates the preview
10. No crashes or visual glitches

- [ ] **Step 4: Commit final state**

```bash
git add -A
git commit -m "feat: live preview pane with debounced updates

Adds a bottom-panel terminal mock that updates in real-time as users
change visual settings (font, colors, cursor, window opacity/padding).
Uses Rich Text rendering with actual color scheme palettes."
```
