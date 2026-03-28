# Performance Optimization Suggestions

## High Impact

### 1. Color scheme search (`screens/colors.py:80-84`)

```python
async def on_input_changed(self, event: Input.Changed) -> None:
    if event.input.id == "scheme-search":
        query = event.value.lower()
        filtered = [s for s in self.schemes if query in s.lower()]
        await self._populate_list(filtered)
```

- O(n) linear scan on every keystroke with no debouncing
- With 100+ color schemes, typing will lag

**Fix**: Add debouncing (~150ms) or use a trie/fuzzy search structure.

---

## Medium Impact

### 2. Importer keybindings parsing (`importer.py:174-198`)

- Three separate `finditer()` passes over the keybindings block
- Sort by position, then deduplicate

**Fix**: Single pass with a combined regex or state machine.

### 3. `_extract_outer_block` (`importer.py:91-104`)

- Character-by-character brace matching
- Could use a stack-based approach or `textwrap.dedent` for simpler cases

---

## Low Impact (already well-optimized)

- **Lua generation**: Uses `list.append()` + `"".join()` — efficient pattern
- **Regex patterns**: All pre-compiled at module level (`importer.py:54-88`)
- **Deep merge**: Recursive but O(n) for config size (~40 options)
- **Subprocess spawn**: Only on startup with 5s timeout and fallback

---

## Summary

The color scheme search is the only **actionable issue** that users would notice in normal operation. The others are micro-optimizations for one-time operations on small data structures.
