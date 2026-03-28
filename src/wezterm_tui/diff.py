"""Compute and format diffs between settings states."""

from __future__ import annotations

from typing import Any


def compute_diff(
    old: dict, new: dict
) -> list[tuple[str, str, Any, Any]]:
    """Return list of (category, key, old_value, new_value) for changed settings."""
    changes: list[tuple[str, str, Any, Any]] = []

    all_keys = set(old) | set(new)
    for cat in sorted(all_keys):
        if cat.startswith("_"):
            continue
        old_val = old.get(cat)
        new_val = new.get(cat)
        if old_val == new_val:
            continue
        old_is_dict = isinstance(old_val, dict)
        new_is_dict = isinstance(new_val, dict)
        if old_is_dict or new_is_dict:
            old_dict = old_val if old_is_dict else {}
            new_dict = new_val if new_is_dict else {}
            sub_keys = set(old_dict) | set(new_dict)
            for key in sorted(sub_keys):
                ov = old_dict.get(key)
                nv = new_dict.get(key)
                if ov != nv:
                    changes.append((cat, key, ov, nv))
        else:
            changes.append((cat, cat, old_val, new_val))
    return changes


def format_diff_text(changes: list[tuple[str, str, Any, Any]]) -> str:
    """Format a diff as human-readable text."""
    if not changes:
        return "No changes."
    lines: list[str] = []
    for cat, key, old_val, new_val in changes:
        label = f"{cat}.{key}" if cat != key else cat
        if old_val is None:
            lines.append(f"  + {label}: {new_val}")
        elif new_val is None:
            lines.append(f"  - {label}: {old_val}")
        else:
            lines.append(f"  ~ {label}: {old_val} -> {new_val}")
    return "\n".join(lines)
