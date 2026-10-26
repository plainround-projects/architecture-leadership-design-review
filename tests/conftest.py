"""Shared builders and the repository's own root."""

from __future__ import annotations

from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class MemoryStore:
    """A DocumentStore held in a dict, for tests that need no disk."""

    def __init__(self, files: dict[str, str] | None = None) -> None:
        self.files = dict(files or {})

    def list_paths(self, folder: str) -> list[str]:
        return sorted(
            path for path in self.files if path.startswith(f"{folder}/") and "/" not in path[len(folder) + 1 :]
        )

    def read_text(self, path: str) -> str:
        return self.files[path]

    def exists(self, path: str) -> bool:
        return path in self.files

    def write_text(self, path: str, text: str) -> None:
        self.files[path] = text


def repository_files() -> dict[str, str]:
    """Every text file the checks read, keyed by repository-relative path."""
    files: dict[str, str] = {}
    for pattern in ("docs/**/*.md", "model/*.toml"):
        for path in REPOSITORY_ROOT.glob(pattern):
            files[path.relative_to(REPOSITORY_ROOT).as_posix()] = path.read_text()
    return files


@pytest.fixture
def store() -> MemoryStore:
    return MemoryStore(repository_files())
