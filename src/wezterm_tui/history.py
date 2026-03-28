"""Undo/redo history for settings changes."""

from __future__ import annotations

import copy


class SettingsHistory:
    """Stack-based undo/redo tracking for settings dicts."""

    def __init__(self, initial: dict):
        self._stack: list[dict] = [copy.deepcopy(initial)]
        self._index: int = 0

    def push(self, settings: dict) -> None:
        self._stack = self._stack[: self._index + 1]
        self._stack.append(copy.deepcopy(settings))
        self._index += 1

    def undo(self) -> dict | None:
        if self._index <= 0:
            return None
        self._index -= 1
        return copy.deepcopy(self._stack[self._index])

    def redo(self) -> dict | None:
        if self._index >= len(self._stack) - 1:
            return None
        self._index += 1
        return copy.deepcopy(self._stack[self._index])

    @property
    def can_undo(self) -> bool:
        return self._index > 0

    @property
    def can_redo(self) -> bool:
        return self._index < len(self._stack) - 1
