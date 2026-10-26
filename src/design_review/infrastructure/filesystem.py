"""The document store on the local file system."""

from __future__ import annotations

from pathlib import Path


class FileSystemStore:
    """Reads the repository's documents under one root. Paths are relative and may not leave the root."""

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def _resolve(self, path: str) -> Path:
        resolved = (self._root / path).resolve()
        if self._root != resolved and self._root not in resolved.parents:
            raise ValueError(f"path escapes the repository root: {path}")
        return resolved

    def list_paths(self, folder: str) -> list[str]:
        """Markdown files directly inside the folder, sorted."""
        directory = self._resolve(folder)
        if not directory.is_dir():
            return []
        return sorted(
            f"{folder}/{entry.name}" for entry in directory.iterdir() if entry.suffix == ".md" and entry.is_file()
        )

    def read_text(self, path: str) -> str:
        """The text of a file."""
        return self._resolve(path).read_text(encoding="utf-8")

    def exists(self, path: str) -> bool:
        """True when the file exists."""
        return self._resolve(path).is_file()

    def write_text(self, path: str, text: str) -> None:
        """Replace a file, creating its folder."""
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
