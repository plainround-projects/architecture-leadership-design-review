"""Settings from the environment, validated once at start-up (twelve-factor)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from design_review.application.check_documents import CheckSettings


class SettingsError(ValueError):
    """An environment variable holds a value the program cannot use."""


@dataclass(frozen=True)
class Settings:
    """Where the documents are, where the report goes, and the proposal size limit."""

    root: Path
    report_dir: str
    check: CheckSettings


def load_settings(env: Mapping[str, str]) -> Settings:
    """Read REVIEW_ROOT, REPORT_DIR and PROPOSAL_MAX_WORDS."""
    raw = env.get("PROPOSAL_MAX_WORDS", "1000")
    try:
        words = int(raw)
    except ValueError:
        raise SettingsError(f"PROPOSAL_MAX_WORDS must be a whole number, got {raw!r}") from None
    if words <= 0:
        raise SettingsError(f"PROPOSAL_MAX_WORDS must be positive, got {words}")
    return Settings(Path(env.get("REVIEW_ROOT", ".")), env.get("REPORT_DIR", "build"), CheckSettings(words))
