# wezterm-tui

A terminal UI for managing [WezTerm](https://wezfurlong.org/wezterm/) settings. Configure fonts, colors, keybindings, and more without manually editing Lua files.

![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

## Features

- **10 settings categories** -- font, colors, window, tabs, cursor, scrollback, performance, keybindings, mouse, miscellaneous
- **Color scheme browser** -- searchable selector with 76+ built-in WezTerm schemes
- **Keybindings editor** -- table-based UI for adding, editing, and deleting key mappings
- **Import existing config** -- reads your current `wezterm.lua` and imports settings
- **Lua generation** -- saves a clean, commented `settings.lua` you can `require()` from your config
- **Validation** -- type checking, range constraints, and enum validation on all settings

## Quick Start

```bash
git clone https://github.com/DarkoKuzmanovic/wezterm-tui.git
cd wezterm-tui
./run.sh
```

The `run.sh` script creates a virtual environment, installs dependencies, and launches the app automatically.

### Manual Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
wezterm-tui
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv run wezterm-tui
```

## Usage

Navigate categories with the sidebar. Edit settings in the main panel.

| Shortcut | Action                    |
| -------- | ------------------------- |
| `Ctrl+S` | Save settings             |
| `Ctrl+R` | Reset to last save        |
| `Ctrl+I` | Import from `wezterm.lua` |
| `Ctrl+Q` | Quit                      |

### Where settings are stored

Settings are saved to `~/.config/wezterm/`:

- `settings.json` -- your settings (read/written by the app)
- `settings.lua` -- generated Lua config

To use the generated config, add this to your `wezterm.lua`:

```lua
local settings = require("settings")
for k, v in pairs(settings) do
    config[k] = v
end
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT
