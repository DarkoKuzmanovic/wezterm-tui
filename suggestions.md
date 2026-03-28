# Suggestions

## New Features

### 1. ~~Settings profiles~~ DONE

~~Let users save/load named profiles (e.g., "Coding", "Presentation", "Dark room"). Store as separate JSON files in `~/.config/wezterm/profiles/`. Add a profile switcher to the sidebar or a `Ctrl+P` shortcut.~~

### 2. ~~Undo/redo~~ DONE

~~Track setting changes in a stack so users can undo individual edits before saving. Textual's reactive system could drive this with a simple command history list.~~

### 3. ~~Settings diff view~~ DONE

~~Before saving, show a diff of what changed since last save. Helps users review modifications, especially after an import.~~

### 4. ~~Export/share config~~ DONE

~~Export current settings as a shareable snippet (Lua, JSON, or a URL-safe base64 blob). Useful for sharing configs on forums or across machines.~~

### 5. ~~Additional WezTerm settings~~ DONE

~~\~30% of WezTerm config options are missing. High-value additions:~~

~~- `window_frame` (title bar, border styling)~~
~~- `adjust_window_size_when_changing_font_size` (bool)~~
~~- `use_ime` / `ime_preedit_rendering_type` (input method support)~~
~~- `command_palette_font_size` (numeric)~~
~~- Tab formatting (`tab_bar_style`, custom tab titles)~~

~~Could live in new "Advanced" or "Window Frame" categories to avoid cluttering the basic UI.~~

*Added 6 settings: `adjust_window_size_when_changing_font_size`, `use_ime`, `ime_preedit_rendering`, `command_palette_font_size`, `window_close_confirmation`, `cell_width`. Complex compound types like `window_frame` and `tab_bar_style` deferred to a future release.*

### 6. ~~Free-text action input for keybindings~~ DONE

~~The 16 hardcoded actions in `keybindings.py` can't keep up with WezTerm releases. Add an "Other..." option that lets users type any action name. Validate format only (alphanumeric + underscores), not against a fixed list.~~

### 7. ~~Inline validation feedback~~ DONE

~~Currently, invalid inputs are silently ignored (`except Exception: pass` in `collect_values()`). Show red borders or inline error messages when a value fails validation — font size out of range, non-numeric input in a number field, etc.~~

### 8. ~~Lazy palette loading~~ DONE

~~Color scheme palettes are extracted from WezTerm on app startup, even if the user never opens the Colors screen. Defer the subprocess call to the first time `ColorsScreen` is mounted.~~

---

## Code Optimizations

### 1. ~~Derive Lua mappings from schema~~ DONE

~~`DIRECT_MAP` in `lua_gen.py` duplicates key names already defined in `schema.py`. If a setting is added or renamed in the schema, Lua output breaks silently. Fix: add a `lua_key` field to the `Option` dataclass and generate the mapping automatically.~~

### 2. ~~Single-pass keybinding import~~ REJECTED

~~`importer.py` runs three separate `finditer()` passes over the keybindings block (no-arg, string-arg, table-arg), then sorts by position and deduplicates. A single combined regex with named groups would halve the iteration count.~~

*Rejected: the three regexes match fundamentally different patterns and are clearer as separate expressions. A combined regex would be harder to maintain for negligible performance gain on small text blocks.*

### 3. ~~Early return in `_switch_screen()`~~ REJECTED

~~`app.py._switch_screen()` tears down and rebuilds the screen even when re-selecting the current category. A one-line `if category == self.current_category: return` guard avoids the wasted mount/unmount cycle.~~

*Rejected: `action_reset()` and `action_import_config()` intentionally call `_switch_screen(self.active_category)` to remount the screen with updated settings. An early return guard would break both features.*

### 4. ~~Cache scheme name filtering~~ REJECTED

~~In `ColorsScreen`, the filtered list is re-computed from scratch on every debounced keystroke. For incremental typing (adding characters), the previous filtered list is a valid subset to search — narrowing the haystack as the query grows.~~

*Rejected: the scheme list is a few hundred entries; substring filtering is instant. The debounce already throttles invocations. Premature optimization.*

---

## Code Simplifications

### 1. ~~Remove bare `except Exception: pass` blocks~~ DONE

~~Two locations silently swallow errors:~~

~~- `app.py:~99` in `_switch_screen()` — if `collect_values()` fails, the user loses edits with no feedback~~
~~- `screens/base.py:~80` in `collect_values()` — invalid widget reads are silently skipped~~

~~Replace with specific exception types and surface errors via `self.notify()` or Textual's built-in toast system.~~

### 2. ~~Consolidate padding widget logic~~ REJECTED

~~`base.py.compose_field()` special-cases `PADDING` with four inline `Input()` calls plus matching `collect_values()` logic. Extract a small `PaddingInput` compound widget that handles its own compose/collect cycle.~~

*Rejected: ~12 lines across two methods doesn't justify a new compound widget. The current code is clear and simple.*

### 3. ~~Parameterize preview prompt text~~ DONE

~~`colors.py` hardcodes `"quzma@endeavour ~/source/wezterm-tui"` in the sample terminal preview. Use a generic string like `"user@host ~/projects"` or pull from `$USER` and `$HOSTNAME`.~~

### 4. ~~Unify action category lists in keybindings~~ DONE

~~`keybindings.py` defines three separate lists (`ACTIONS_NO_ARGS`, `ACTIONS_STRING_ARG`, `ACTIONS_TABLE_ARG`). A single dict mapping action name → arg type would simplify both the Select widget population and the arg-parsing branch in `on_button_pressed()`.~~
