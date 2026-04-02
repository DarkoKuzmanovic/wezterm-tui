# wezterm-tui

Python TUI settings manager for WezTerm terminal.

## Commands

- `./run.sh` - Run the app
- `pytest` - Run all tests
- `pytest tests/test_schema.py -v` - Run a single test file

## Architecture

- `src/wezterm_tui/` contains app code (`app.py`, schema, config I/O, importer/exporter, preview, screens)
- `src/wezterm_tui/screens/` contains category-specific Textual screens
- `tests/` contains pytest coverage for core modules and UI behavior

## Conventions

- Entry point: `wezterm_tui.__main__:main`
- Settings file: `~/.config/wezterm/settings.json`
- Generated Lua file: `~/.config/wezterm/settings.lua`
- Keep setting definitions and validation in `schema.py`

## Lessons Learned

### 2026-04-02: Idempotent installer behavior

**Problem:** Re-running curl installer with `uv` failed with `Executable already exists: wezterm-tui`.
**Root cause:** Installer used `uv tool install` without overwrite behavior.
**Solution:** Use `uv tool install --force` (and `pipx install --force` for parity).
**Prevention:** Installer paths should support repeat runs and upgrades without manual cleanup.
