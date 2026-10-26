"""Small text helpers shared by the rules."""

from __future__ import annotations

import re

_WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9'-]*")


def words(text: str) -> list[str]:
    """The words of a text, lower-cased."""
    return [match.lower() for match in _WORD.findall(text)]


def has_figure(text: str) -> bool:
    """True when the text holds at least one digit: a number, a date or a count."""
    return any(character.isdigit() for character in text)
