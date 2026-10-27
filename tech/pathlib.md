# pathlib and file access

## What it is

`pathlib.Path` is the standard Python way to work with file and folder names. A `Path` object knows how to join
names with `/`, ask whether something exists, read and write text, and list a folder. It works the same on macOS,
Linux and Windows.

## Why this repository uses it

The program reads the repository's documents and writes a report. All file access goes through one small class
(`FileSystemStore`), which also refuses paths that escape the root folder.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `src/design_review/infrastructure/filesystem.py` | `FileSystemStore`: the only code that touches the disk. |
| `src/design_review/infrastructure/settings.py` | Turns the root setting into a `Path`. |
| `tests/conftest.py` | `REPOSITORY_ROOT` from `Path(__file__)`. |
| `tests/**` | `tmp_path / "docs"` and `write_text` to build sample folders. |

## How it works underneath

- A `Path` is only a name until you use it. `Path("docs") / "adr"` builds `docs/adr` without touching the disk.
- `.read_text(encoding="utf-8")` opens the file, reads all of it as text using that encoding, and closes it.
- `.resolve()` makes a path absolute and follows `..` and symbolic links. Comparing resolved paths is the safe way to
  test "is this inside that folder".
- `.parents` is the chain of containing folders.

## Walkthrough of this repository's use

`src/design_review/infrastructure/filesystem.py`:

```python
class FileSystemStore:
    """Reads the repository's documents under one root. Paths are relative and may not leave the root."""

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def _resolve(self, path: str) -> Path:
        resolved = (self._root / path).resolve()
        if self._root != resolved and self._root not in resolved.parents:
            raise ValueError(f"path escapes the repository root: {path}")
```

- `root.resolve()` stores the absolute root.
- `self._root / path` joins the root with a relative name, `.resolve()` removes any `..`.
- The `if` rejects a path that is neither the root itself nor inside it (`self._root not in resolved.parents`).
  A document name like `../secret.md` therefore raises `ValueError` instead of reading outside the repository.

`src/design_review/infrastructure/filesystem.py`:

```python
    def list_paths(self, folder: str) -> list[str]:
        """Markdown files directly inside the folder, sorted."""
        directory = self._resolve(folder)
        if not directory.is_dir():
            return []
        return sorted(
            f"{folder}/{entry.name}" for entry in directory.iterdir() if entry.suffix == ".md" and entry.is_file()
        )
```

`iterdir()` lists a folder's entries; `entry.suffix == ".md"` keeps Markdown files; `entry.is_file()` skips
sub-folders; `sorted(...)` gives a stable order. The generator expression builds `folder/name` strings.

`src/design_review/infrastructure/filesystem.py`:

```python
    def write_text(self, path: str, text: str) -> None:
        """Replace a file, creating its folder."""
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
```

`target.parent.mkdir(parents=True, exist_ok=True)` creates the folder and any missing parents, and does not fail if
it already exists.

## Try it yourself

```bash
.venv/bin/python -c "from pathlib import Path; p = Path('docs/reviews'); print(p, p.is_dir(), sorted(x.name for x in p.iterdir())[:2])"
```
Prints `docs/reviews True` and the first two file names in that folder.

```bash
.venv/bin/python -c "from pathlib import Path; from design_review.infrastructure.filesystem import FileSystemStore; FileSystemStore(Path('.')).read_text('../x.md')" 2>&1 | tail -1
```
Prints `ValueError: path escapes the repository root: ../x.md`.

```bash
.venv/bin/python -c "from pathlib import Path; print(Path('src/design_review/domain/text.py').suffix, Path('a/b/c.md').parents[1])"
```
Prints `.py a`.

```bash
.venv/bin/pytest -q tests/unit/infrastructure/test_readers.py
```
Runs tests that include the store on a real temporary folder (`tmp_path`).

## Mistakes people make

- **Joining paths with `+`** and a slash character. Use `/`.
- **Forgetting the encoding** on Windows, where the default is not UTF-8.
- **Comparing unresolved paths**, so `docs/../x` looks like it is inside `docs`.
- **Letting user-supplied names reach the disk unchecked.** The store checks every path.

## Check yourself

1. What does `Path('a') / 'b'` give?
   **Answer:** The path `a/b`, with no file access.
2. Why `.resolve()` before comparing?
   **Answer:** It removes `..` and links so the check cannot be fooled.
3. What does `mkdir(parents=True, exist_ok=True)` do?
   **Answer:** Creates the folder and missing parents; no error if it exists.
4. Why does only one class touch the disk?
   **Answer:** So the rules can be tested without files and the path check lives in one place.
5. What does `Path(__file__).resolve().parents[1]` find in `conftest.py`?
   **Answer:** The repository root (two levels up from the test file).

## Further reading

- `pathlib` (Python 3.12): <https://docs.python.org/3.12/library/pathlib.html>
