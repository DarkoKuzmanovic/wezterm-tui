# Changelog

All notable changes to wezterm-tui will be documented in this file.

## [1.0.0] - 2026-03-28

### Added
- Settings profiles: save/load named configuration profiles (`Ctrl+P`). Stored as JSON in `~/.config/wezterm/profiles/`.
- Undo/redo: track setting changes and revert with `Ctrl+Z` / `Ctrl+Y`.
- Settings diff view: review pending changes before saving with `Ctrl+D`.
- Export/share config: export current settings as Lua, JSON, or URL-safe base64 with `Ctrl+E`.
- 6 additional WezTerm settings: `adjust_window_size_when_changing_font_size`, `use_ime`, `ime_preedit_rendering`, `command_palette_font_size`, `window_close_confirmation`, `cell_width`.
- Free-text action input: "Other..." option in keybindings lets you type any WezTerm action name.
- Inline validation feedback: numeric inputs show red borders when values are out of range.
- Lazy palette loading: color scheme palettes are loaded on first Colors screen visit instead of during construction.

### Changed
- Lua key mappings are now derived from schema instead of maintained as separate dicts.
- Bare `except Exception: pass` blocks replaced with specific exception handling and user notifications.
- Preview prompt text uses generic `user@host` instead of hardcoded values.
- Keybinding actions consolidated from three lists into a single `ACTIONS` dict.

## [0.1.0] - 2025-01-01

### Added
- Initial release with 10 settings categories.
- Color scheme browser with live preview.
- Keybindings editor.
- Import from existing `wezterm.lua`.
- Lua config generation.
- Validation and safe saves.
