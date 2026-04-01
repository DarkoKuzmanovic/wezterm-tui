# Live Preview Pane — Design Spec

## Overview

Add a live preview pane to wezterm-tui that shows a real-time Rich Text terminal mock, updating as users tweak visual settings. The preview gives instant feedback on how font, color scheme, cursor, and window settings will look — without saving or reloading WezTerm.

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Placement | Bottom panel | Full-width terminal mock; no horizontal squeeze on settings form |
| Rendering | Rich Text mock | Strongest "this is your terminal" feel; leverages existing Rich/Textual stack |
| Update timing | Debounced ~300ms | Feels live without flickering during mid-edit keystrokes |
| Settings scope | Visual-only (~15 settings) | Font, colors, cursor, window opacity/padding. Non-visual settings (keybindings, mouse, scrollback) are excluded |
| Visibility | Always visible | No layout shifts between categories; consistent mental model |
| Architecture | Standalone PreviewPanel widget | One new file, minimal changes to existing code, follows established patterns |

## Architecture

### New File: `src/wezterm_tui/preview.py`

A `PreviewPanel` class extending Textual's `Static`.

**Public API:**
- `update_preview(settings: dict, palettes: dict) -> None` — rebuilds the Rich renderable from current settings and color palettes
- `render() -> RenderableType` — returns the cached Rich renderable

**No dependencies on screens.** The widget reads settings and palettes directly; it does not import or reference any screen class.

### App Layout Change (`app.py`)

Current:
```
Header
├── Horizontal
│   ├── Sidebar (ListView)
│   └── Content (VerticalScroll)
Footer
```

New:
```
Header
├── Vertical
│   ├── Horizontal
│   │   ├── Sidebar (ListView)
│   │   └── Content (VerticalScroll)
│   └── PreviewPanel
Footer
```

`PreviewPanel` sits below the sidebar+content row, spanning full width.

### CSS

```css
PreviewPanel {
    height: 10;
    border-top: tall $accent;
    padding: 0 1;
    background: $surface;
}
```

## Debounced Refresh Mechanism

1. App-level message handlers catch `Input.Changed`, `Switch.Changed`, `Select.Changed` events
2. Each calls `_schedule_preview_refresh()` which cancels any pending Textual `Timer` (stored as `self._preview_timer`) and sets a new 300ms timer via `self.set_timer(0.3, ...)`
3. When the timer fires: `current_screen.collect_values()` to snapshot settings, then `preview_panel.update_preview(settings, palettes)`
4. Palettes loaded once on mount via existing `color_schemes.load_scheme_palettes()`, cached on the app instance

## Rendering Logic

### Step 1: Resolve Colors

Given `settings["colors"]["color_scheme"]`, look up palette from the cached palettes dict. Extract:
- `bg` — background color
- `fg` — foreground color
- `ansi[0..7]` — standard ANSI colors
- `brights[0..7]` — bright ANSI colors

If palette lookup fails, fall back to hardcoded defaults: `bg=#1e1e1e`, `fg=#d4d4d4`, standard ANSI dark palette (VGA-style: black, red, green, yellow, blue, magenta, cyan, white).

### Step 2: Resolve Visual Settings

From the settings dict:
- `font.family`, `font.size`, `font.weight`, `font.line_height`
- `cursor.default_cursor_style`, `cursor.cursor_blink_rate`, `cursor.cursor_thickness`
- `window.window_background_opacity`, `window.window_padding` (all 4 sides)

### Step 3: Compose Rich Text

Build a single Rich `Text` object with styled spans:

```
 JetBrains Mono  12.0pt  Regular                 opacity: 0.95
 ──────────────────────────────────────────────────────────────
 user@host ~ $ ls -la
 drwxr-xr-x  5 user staff  160 Mar 28 10:00 src/
 -rw-r--r--  1 user staff 4096 Mar 28 09:45 README.md
 -rwxr-xr-x  1 user staff  512 Mar 27 14:20 run.sh
 user@host ~ $ █
 ──────────────────────────────────────────────────────────────
 padding: 8/8/4/4  cursor: block, blink  line-height: 1.0
```

Color mapping:
- Prompt user → `ansi[2]` (green)
- Prompt path → `ansi[6]` (cyan)
- Directories → `ansi[4]` (blue)
- Executables → `ansi[5]` (magenta)
- Regular text → `fg`
- Cursor character: `█` (block), `|` (bar), `▁` (underline) — based on `default_cursor_style`

### Step 4: Apply Background

The entire `Text` gets `Style(bgcolor=bg)`. If `window_background_opacity < 1.0`, linear-interpolate each RGB channel of `bg` toward 0 (black) by `1 - opacity`. For example, opacity 0.8 with bg `#1e1e1e` → `rgb(int(30*0.8), int(30*0.8), int(30*0.8))` = `#181818`. This is a cosmetic approximation of transparency over a black desktop.

### Font Display

The TUI cannot change the terminal's actual font. Font family, size, and weight are displayed as text in the header strip so the user sees what they've configured.

## Edge Cases

| Case | Behavior |
|------|----------|
| Unknown color scheme | Render with default dark colors; show "(unknown scheme)" in status strip |
| Palette not yet loaded | Show "Loading preview..." placeholder until palettes are cached |
| Invalid mid-edit values | Use current/default value; preview never errors |
| ColorsScreen's existing preview | Leave it alone — it's a palette swatch for scheme selection; the bottom preview is a terminal mock. They coexist and serve different purposes |
| Very small terminal | Fixed height of 10 rows; Textual handles overflow via its layout engine |

## Testing

**New file: `tests/test_preview.py`** — unit tests for the rendering logic:

| Test | What it verifies |
|------|-----------------|
| `test_render_with_default_settings` | Renders without error; output contains prompt elements |
| `test_render_with_custom_scheme` | Known palette colors appear in Rich styles |
| `test_render_unknown_scheme` | Falls back gracefully; shows "(unknown scheme)" |
| `test_render_cursor_styles` | Block/bar/underline produce correct cursor characters |
| `test_opacity_blending` | Opacity < 1.0 darkens background color |
| `test_empty_settings` | Missing keys don't crash; defaults used |

No async/integration tests needed. The preview is a pure function (settings + palettes in, Rich Text out). Debounce wiring is thin enough for manual verification.

## Files Changed

| File | Change |
|------|--------|
| `src/wezterm_tui/preview.py` | **New.** PreviewPanel widget with rendering logic |
| `src/wezterm_tui/app.py` | Mount PreviewPanel in layout; add debounced refresh handlers; cache palettes |
| `tests/test_preview.py` | **New.** Unit tests for rendering |

## Out of Scope

- Tab bar rendering in preview
- Keybinding, mouse, scrollback, misc settings in preview
- Collapsible/toggleable preview panel
- Actual font rendering (impossible in a TUI)
