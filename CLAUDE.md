# CLAUDE.md

## Project

wezterm-tui -- a Python TUI (Textual) settings manager for WezTerm terminal.

## Stack

- Python 3.12+, Textual 3.0+
- Build: hatchling
- Tests: pytest + pytest-asyncio

## Layout

- `src/wezterm_tui/` -- package source
  - `app.py` -- main Textual app
  - `config.py` -- JSON settings I/O
  - `schema.py` -- settings schema, categories, validation
  - `lua_gen.py` -- generates Lua config from settings dict
  - `importer.py` -- parses existing wezterm.lua
  - `screens/` -- per-category UI screens (base.py, colors.py, keybindings.py)
  - `data/color_schemes.json` -- color scheme list
- `tests/` -- pytest tests

## Commands

```bash
# Run
./run.sh

# Tests
pytest

# Single test
pytest tests/test_schema.py -v
```

## Conventions

- Entry point: `wezterm_tui.__main__:main`
- Settings stored at `~/.config/wezterm/settings.json`
- Generated Lua at `~/.config/wezterm/settings.lua`
- All settings defined in schema.py with types, defaults, and validation
- Screens auto-generate widgets from schema; specialized screens override for custom UI
