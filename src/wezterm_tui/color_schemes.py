"""Color scheme helpers for names and preview palettes."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from functools import lru_cache
from importlib import resources


def _load_bundled_names() -> list[str]:
    data_path = resources.files("wezterm_tui") / "data" / "color_schemes.json"
    return json.loads(data_path.read_text())


def _dump_wezterm_palettes() -> dict[str, dict]:
    lua = """
local wezterm = require 'wezterm'
local raw = wezterm.color.get_builtin_schemes()
local out = {}

for name, scheme in pairs(raw) do
  out[name] = {
    foreground = scheme.foreground,
    background = scheme.background,
    cursor_bg = scheme.cursor_bg,
    cursor_fg = scheme.cursor_fg,
    cursor_border = scheme.cursor_border,
    selection_fg = scheme.selection_fg,
    selection_bg = scheme.selection_bg,
    ansi = scheme.ansi,
    brights = scheme.brights,
  }
end

local path = os.getenv('WEZTERM_TUI_DUMP_PATH')
local file = assert(io.open(path, 'w'))
file:write(wezterm.json_encode(out))
file:close()

return {}
"""

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "dump_schemes.lua")
            output_path = os.path.join(tmpdir, "schemes.json")
            with open(config_path, "w") as config_file:
                config_file.write(lua)

            env = os.environ.copy()
            env["WEZTERM_TUI_DUMP_PATH"] = output_path
            subprocess.run(
                ["wezterm", "--config-file", config_path, "ls-fonts"],
                check=False,
                capture_output=True,
                env=env,
                text=True,
                timeout=5,
            )

            if not os.path.exists(output_path):
                return {}

            with open(output_path) as output_file:
                return json.load(output_file)
    except (FileNotFoundError, OSError, json.JSONDecodeError, subprocess.SubprocessError):
        return {}


@lru_cache(maxsize=1)
def load_scheme_palettes() -> dict[str, dict]:
    return _dump_wezterm_palettes()


def load_scheme_names() -> list[str]:
    palettes = load_scheme_palettes()
    if palettes:
        return sorted(palettes)
    return _load_bundled_names()
