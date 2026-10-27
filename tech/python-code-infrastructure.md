# Infrastructure layer code

## What it is

The adapters: the code that really reads files, talks to a database or a network, and reads the environment. (Every term is explained where it first appears in the walkthrough below.)

## Why this repository uses it

This is where the repository's infrastructure work happens. Reading it file by file, with every line explained, is how a reader sees the work that was done.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `src/design_review/infrastructure/__init__.py` | 1 lines. Adapters: the file system, the Markdown and TOML readers, settings from the environment. |
| `src/design_review/infrastructure/filesystem.py` | 31 lines. The document store on the local file system. |
| `src/design_review/infrastructure/markdown.py` | 191 lines. Parse the Markdown of each document type into the domain's values. |
| `src/design_review/infrastructure/model_toml.py` | 65 lines. Load and validate `model/uploads.toml` into the fitness model. |
| `src/design_review/infrastructure/settings.py` | 24 lines. Settings from the environment, validated once at start-up (twelve-factor). |

## How it works underneath

Each adapter implements a port from the application layer using a real technology (the file system, SQLite or PostgreSQL, HTTP, the environment). They are kept thin, so that swapping one changes nothing above. Tests exercise them on real temporary files or a real database.

## Walkthrough of this repository's use

### `src/design_review/infrastructure/__init__.py`

`src/design_review/infrastructure/__init__.py` lines 1 to 1:

```python
"""Adapters: the file system, the Markdown and TOML readers, settings from the environment."""
```

> **In plain words.** A **docstring** is a text in triple quotes as the first thing in a module, class or function. Python keeps it as the thing's description, and ruff requires one on public code.

**Module description.** Adapters: the file system, the Markdown and TOML readers, settings from the environment.

### `src/design_review/infrastructure/filesystem.py`

`src/design_review/infrastructure/filesystem.py` lines 1 to 5:

```python
"""The document store on the local file system."""

from __future__ import annotations

from pathlib import Path
```

> **In plain words.** A **docstring** is a text in triple quotes as the first thing in a module, class or function. Python keeps it as the thing's description, and ruff requires one on public code.
> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.
> **In plain words.** `from __future__ import annotations` makes every type hint in the file lazy text. Python no longer evaluates a hint when the file loads, so a hint may name a class defined further down.

**Module description.** The document store on the local file system.

Imports:

- From `__future__` it takes `annotations`.
- From `pathlib` it takes `Path`.

`src/design_review/infrastructure/filesystem.py` lines 8 to 9:

```python
class FileSystemStore:
    """Reads the repository's documents under one root. Paths are relative and may not leave the root."""
```

> **In plain words.** A **class** is a blueprint for objects that bundle data with the functions that work on it. `class B(A)` means B is a kind of A and starts with everything A has.

**Class `FileSystemStore`**. Reads the repository's documents under one root. Paths are relative and may not leave the root.

`src/design_review/infrastructure/filesystem.py` lines 11 to 12:

```python
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()
```

> **In plain words.** A **type hint** such as `x: int` or `-> str` says what kind of value a name holds or a function gives back. Python does not enforce hints when the program runs; the type checker mypy reads them before.

**Method `__init__` of class `FileSystemStore`.**

It takes: `root` (a `Path`).

It gives back a `None`.

Step by step:

- Stores the result of calling `root.resolve()` in `self._root`.

`src/design_review/infrastructure/filesystem.py` lines 14 to 18:

```python
    def _resolve(self, path: str) -> Path:
        resolved = (self._root / path).resolve()
        if self._root != resolved and self._root not in resolved.parents:
            raise ValueError(f"path escapes the repository root: {path}")
        return resolved
```

> **In plain words.** `return value` ends the function and gives the value back to whoever called it.
> **In plain words.** `raise Error(...)` stops the current function by signalling an error. `raise ... from None` hides the earlier error, so the user sees only the new, clearer message.
> **In plain words.** `==` tests equality, `is` tests that two names are the very same object (used for `None` and enum members), `in` tests membership.
> **In plain words.** An **f-string** `f"...{value}..."` is text with Python expressions in braces; Python replaces each by its value. `{x!r}` shows the value the way Python would write it, with quotes.

**Method `_resolve` of class `FileSystemStore`.**

It takes: `path` (a `str`).

It gives back a `Path`.

Step by step:

- Stores the result of calling `(self._root / path).resolve()` in `resolved`.
- If `self._root` is different from `resolved` and `self._root` is not in `resolved.parents`:
  - Stops here by raising `ValueError(f'path escapes the repository root: {path}')`.
- Gives back `resolved`.

`src/design_review/infrastructure/filesystem.py` lines 20 to 27:

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

> **In plain words.** `obj[key]` looks a value up by key or position.
> **In plain words.** A **generator expression** `(x for x in items)` is like a list comprehension, but it hands out one value at a time instead of building the whole list; here it is passed straight to a function such as `tuple(...)` or `sum(...)`.

**Method `list_paths` of class `FileSystemStore`.** Markdown files directly inside the folder, sorted.

It takes: `folder` (a `str`).

It gives back a `list[str]`.

Step by step:

- Stores the result of calling `self._resolve(folder)` in `directory`.
- If not (`directory.is_dir()`):
  - Gives back the list `[]`.
- Gives back the result of calling `sorted((f'{folder}/{entry.name}' for entry in directory.iterdir() if entry.suffix == '.md…`.

`src/design_review/infrastructure/filesystem.py` lines 29 to 31:

```python
    def read_text(self, path: str) -> str:
        """The text of a file."""
        return self._resolve(path).read_text(encoding="utf-8")
```

> **In plain words.** A call such as `f(a, key=value)` passes `a` by position and `key` by name (a **keyword argument**).

**Method `read_text` of class `FileSystemStore`.** The text of a file.

It takes: `path` (a `str`).

It gives back a `str`.

Step by step:

- Gives back the result of calling `self._resolve(path).read_text(encoding='utf-8')`.

`src/design_review/infrastructure/filesystem.py` lines 33 to 35:

```python
    def exists(self, path: str) -> bool:
        """True when the file exists."""
        return self._resolve(path).is_file()
```

**Method `exists` of class `FileSystemStore`.** True when the file exists.

It takes: `path` (a `str`).

It gives back a `bool`.

Step by step:

- Gives back the result of calling `self._resolve(path).is_file()`.

`src/design_review/infrastructure/filesystem.py` lines 37 to 41:

```python
    def write_text(self, path: str, text: str) -> None:
        """Replace a file, creating its folder."""
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
```

**Method `write_text` of class `FileSystemStore`.** Replace a file, creating its folder.

It takes: `path` (a `str`); `text` (a `str`).

It gives back a `None`.

Step by step:

- Stores the result of calling `self._resolve(path)` in `target`.
- Calls `target.parent.mkdir(parents=True, exist_ok=True)`.
- Calls `target.write_text(text, encoding='utf-8')`.

### `src/design_review/infrastructure/markdown.py`

`src/design_review/infrastructure/markdown.py` lines 1 to 19:

```python
"""Parse the Markdown of each document type into the domain's values."""

from __future__ import annotations

import re

from design_review.application.ports import DocumentStore
from design_review.domain.checklist import ITEM, Checklist, ChecklistItem
from design_review.domain.proposal import Proposal
from design_review.domain.requirements import REQUIRED_CATEGORIES, Requirement, RequirementSet
from design_review.domain.review import (
    AcceptedRisk,
    ActionItem,
    Assessment,
    Disagreement,
    ReviewFinding,
    ReviewRecord,
    UsedRequirement,
)
```

> **In plain words.** A **docstring** is a text in triple quotes as the first thing in a module, class or function. Python keeps it as the thing's description, and ruff requires one on public code.
> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.
> **In plain words.** `from __future__ import annotations` makes every type hint in the file lazy text. Python no longer evaluates a hint when the file loads, so a hint may name a class defined further down.

**Module description.** Parse the Markdown of each document type into the domain's values.

Imports:

- From `__future__` it takes `annotations`.
- It imports module `re`.
- From `design_review.application.ports` it takes `DocumentStore`.
- From `design_review.domain.checklist` it takes `ITEM, Checklist, ChecklistItem`.
- From `design_review.domain.proposal` it takes `Proposal`.
- From `design_review.domain.requirements` it takes `REQUIRED_CATEGORIES, Requirement, RequirementSet`.
- From `design_review.domain.review` it takes `AcceptedRisk, ActionItem, Assessment, Disagreement, ReviewFinding, ReviewRecord, UsedRequirement`.

`src/design_review/infrastructure/markdown.py` lines 21 to 23:

````python
_HEADING2 = re.compile(r"^## (.+?)\s*$")
_FENCE = re.compile(r"^```")
_FIELD = re.compile(r"^(Author|Date|Reviewers|System|Requirements file):\s*(.*?)\s*$")
````

> **In plain words.** A **regular expression** is a short pattern for text, such as `^## (.+)$` for "a line starting with ## ". `re.compile` prepares it once; `.match` tries it at the start of a string and returns a match object or `None`.
> **In plain words.** A name written in CAPITAL letters is a **constant** by convention: a value set once, not changed later.

These module-level lines:

- Stores the result of calling `re.compile('^## (.+?)\\s*$')` in `_HEADING2`.
- Stores the result of calling `re.compile('^```')` in `_FENCE`.
- Stores the result of calling `re.compile('^(Author|Date|Reviewers|System|Requirements file):\\s*(.*?)\\s*$')` in `_FIELD`.

`src/design_review/infrastructure/markdown.py` lines 26 to 36:

```python
def _sections(lines: list[str]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {"": []}
    current = ""
    for line in lines:
        match = _HEADING2.match(line)
        if match:
            current = match.group(1)
            grouped[current] = []
        else:
            grouped[current].append(line)
    return grouped
```

> **In plain words.** A **type hint** such as `x: int` or `-> str` says what kind of value a name holds or a function gives back. Python does not enforce hints when the program runs; the type checker mypy reads them before.
> **In plain words.** A **`for` loop** repeats its steps once for each item of a collection. `range(n)` counts from 0 to n-1.
> **In plain words.** `return value` ends the function and gives the value back to whoever called it.
> **In plain words.** `obj[key]` looks a value up by key or position.
> **In plain words.** A **dictionary** `{key: value}` maps keys to values.
> **In plain words.** A **tuple** `(a, b)` is a fixed list of values that cannot be changed.

**Function `_sections`.**

It takes: `lines` (a `list[str]`).

It gives back a `dict[str, list[str]]`.

Step by step:

- Declares `grouped` as a `dict[str, list[str]]` and stores the dictionary `{'': []}` in it.
- Stores the text `''` in `current`.
- For each `line` in `lines`:
  - Stores the result of calling `_HEADING2.match(line)` in `match`.
  - If `match`:
    - Stores the result of calling `match.group(1)` in `current`.
    - Stores the list `[]` in `grouped[current]`.
  - Otherwise:
    - Calls `grouped[current].append(line)`.
- Gives back `grouped`.

`src/design_review/infrastructure/markdown.py` lines 39 to 41:

```python
def _header_fields(sections: dict[str, list[str]]) -> dict[str, str]:
    """`Author:`, `Date:` and the other header fields, read only from the lines before the first heading."""
    return {m.group(1): m.group(2) for line in sections[""] if (m := _FIELD.match(line))}
```

> **In plain words.** A **dictionary comprehension** `{k: v for ...}` builds a dictionary with a loop written inside braces.
> **In plain words.** The **walrus operator** `:=` stores a value in a name and uses it in the same expression.

**Function `_header_fields`.** `Author:`, `Date:` and the other header fields, read only from the lines before the first heading.

It takes: `sections` (a `dict[str, list[str]]`).

It gives back a `dict[str, str]`.

Step by step:

- Gives back a new dictionary made by a loop (`{m.group(1): m.group(2) for line in sections[''] if (m := _FIELD.matc…`).

`src/design_review/infrastructure/markdown.py` lines 44 to 49:

```python
def _section(sections: dict[str, list[str]], prefix: str) -> list[str]:
    """The lines of the first section whose heading starts with the prefix (headings may carry a parenthetical)."""
    for name, lines in sections.items():
        if name.startswith(prefix):
            return lines
    return []
```

**Function `_section`.** The lines of the first section whose heading starts with the prefix (headings may carry a parenthetical).

It takes: `sections` (a `dict[str, list[str]]`); `prefix` (a `str`).

It gives back a `list[str]`.

Step by step:

- For each `(name, lines)` in the result of calling `sections.items()`:
  - If `name.startswith(prefix)`:
    - Gives back `lines`.
- Gives back the list `[]`.

`src/design_review/infrastructure/markdown.py` lines 52 to 64:

```python
def table_rows(lines: list[str]) -> list[dict[str, str]]:
    """The rows of the first Markdown table in the lines, keyed by the header cells."""
    rows: list[list[str]] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|"):
            rows.append([cell.strip() for cell in stripped.strip("|").split("|")])
        elif rows:
            break
    if len(rows) < 3:
        return []
    header, body = rows[0], rows[2:]
    return [dict(zip(header, row, strict=False)) | dict.fromkeys(header[len(row) :], "") for row in body]
```

> **In plain words.** `==` tests equality, `is` tests that two names are the very same object (used for `None` and enum members), `in` tests membership.
> **In plain words.** A **list comprehension** `[x for x in items if test]` is a loop written inside brackets: it builds a new list from the items that pass the test.
> **In plain words.** On sets, `a | b` is the union (everything in either) and `a & b` the intersection (what both have).
> **In plain words.** A **slice** such as `text[:7]` or `items[1:]` takes part of a sequence: `[:7]` the first seven items, `[1:]` everything after the first.
> **In plain words.** A call such as `f(a, key=value)` passes `a` by position and `key` by name (a **keyword argument**).

**Function `table_rows`.** The rows of the first Markdown table in the lines, keyed by the header cells.

It takes: `lines` (a `list[str]`).

It gives back a `list[dict[str, str]]`.

Step by step:

- Declares `rows` as a `list[list[str]]` and stores the list `[]` in it.
- For each `line` in `lines`:
  - Stores the result of calling `line.strip()` in `stripped`.
  - If `stripped.startswith('|')`:
    - Calls `rows.append([cell.strip() for cell in stripped.strip('|').split('|')])`.
  - Otherwise, if `rows`:
    - Leaves the loop (`break`).
- If `len(rows)` is less than `3`:
  - Gives back the list `[]`.
- Unpacks the tuple `(rows[0], rows[2:])` into `(header, body)`.
- Gives back a new list made by a loop (`[dict(zip(header, row, strict=False)) | dict.fromkeys(header[len(row)…`).

`src/design_review/infrastructure/markdown.py` lines 67 to 75:

```python
def _bullets(lines: list[str]) -> tuple[str, ...]:
    items: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("- ", "* ")):
            items.append(stripped[2:].strip())
        elif stripped and items and not stripped.startswith("|"):
            items[-1] += " " + stripped
    return tuple(items)
```

**Function `_bullets`.**

It takes: `lines` (a `list[str]`).

It gives back a `tuple[str, ...]`.

Step by step:

- Declares `items` as a `list[str]` and stores the list `[]` in it.
- For each `line` in `lines`:
  - Stores the result of calling `line.strip()` in `stripped`.
  - If `stripped.startswith(('- ', '* '))`:
    - Calls `items.append(stripped[2:].strip())`.
  - Otherwise, if `stripped` and `items` and not (`stripped.startswith('|')`):
    - Adds `' ' + stripped` to `items[-1]`.
- Gives back the result of calling `tuple(items)`.

`src/design_review/infrastructure/markdown.py` lines 78 to 79:

```python
def _paragraph(lines: list[str]) -> str:
    return " ".join(line.strip() for line in lines if line.strip())
```

> **In plain words.** A **generator expression** `(x for x in items)` is like a list comprehension, but it hands out one value at a time instead of building the whole list; here it is passed straight to a function such as `tuple(...)` or `sum(...)`.

**Function `_paragraph`.**

It takes: `lines` (a `list[str]`).

It gives back a `str`.

Step by step:

- Gives back the result of calling `' '.join((line.strip() for line in lines if line.strip()))`.

`src/design_review/infrastructure/markdown.py` lines 82 to 83:

```python
class MarkdownDocumentReader:
    """Reads the repository's four document types from a store."""
```

> **In plain words.** A **class** is a blueprint for objects that bundle data with the functions that work on it. `class B(A)` means B is a kind of A and starts with everything A has.

**Class `MarkdownDocumentReader`**. Reads the repository's four document types from a store.

`src/design_review/infrastructure/markdown.py` lines 85 to 86:

```python
    def __init__(self, store: DocumentStore) -> None:
        self._store = store
```

**Method `__init__` of class `MarkdownDocumentReader`.**

It takes: `store` (a `DocumentStore`).

It gives back a `None`.

Step by step:

- Stores `store` in `self._store`.

`src/design_review/infrastructure/markdown.py` lines 88 to 107:

```python
    def read_requirements(self, path: str) -> RequirementSet:
        """The `## Requirements` table: ID, Category, Requirement, Target, How to verify."""
        lines = self._store.read_text(path).splitlines()
        rows = table_rows(_section(_sections(lines), "Requirements"))
        declared = next((line.partition(":")[2] for line in lines if line.startswith("Categories:")), "")
        categories = tuple(part.strip() for part in declared.split(",") if part.strip()) or REQUIRED_CATEGORIES
        return RequirementSet(
            path=path,
            required_categories=categories,
            requirements=tuple(
                Requirement(
                    id=row.get("ID", ""),
                    category=row.get("Category", ""),
                    name=row.get("Requirement", ""),
                    target=row.get("Target", ""),
                    verification=row.get("How to verify", ""),
                )
                for row in rows
            ),
        )
```

**Method `read_requirements` of class `MarkdownDocumentReader`.** The `## Requirements` table: ID, Category, Requirement, Target, How to verify.

It takes: `path` (a `str`).

It gives back a `RequirementSet`.

Step by step:

- Stores the result of calling `self._store.read_text(path).splitlines()` in `lines`.
- Stores the result of calling `table_rows(_section(_sections(lines), 'Requirements'))` in `rows`.
- Stores the result of calling `next((line.partition(':')[2] for line in lines if line.startswith('Categories:')), '')` in `declared`.
- Stores whether `tuple((part.strip() for part in declared.split(',') if part.strip()))` or `REQUIRED_CATEGORIES` in `categories`.
- Gives back the result of calling `RequirementSet(path=path, required_categories=categories, requirements=tuple((Requirement…`.

`src/design_review/infrastructure/markdown.py` lines 109 to 131:

```python
    def read_proposal(self, path: str) -> Proposal:
        """A proposal: the title, the author, the sections, and the fenced diagram under `Data flow`."""
        text = self._store.read_text(path)
        lines = text.splitlines()
        sections = _sections(lines)
        flow = sections.get("Data flow", [])
        diagram: list[str] = []
        inside = False
        for line in flow:
            if _FENCE.match(line):
                inside = not inside
            elif inside:
                diagram.append(line)
        author = _header_fields(sections).get("Author", "")
        title = lines[0].removeprefix("# ").strip() if lines else ""
        return Proposal(
            path=path,
            title=title,
            author=author,
            sections={name: _paragraph(body) for name, body in sections.items() if name},
            diagram="\n".join(diagram),
            word_count=len(text.split()),
        )
```

> **In plain words.** `A if test else B` is a **conditional expression**: its value is A when the test is true, otherwise B.

**Method `read_proposal` of class `MarkdownDocumentReader`.** A proposal: the title, the author, the sections, and the fenced diagram under `Data flow`.

It takes: `path` (a `str`).

It gives back a `Proposal`.

Step by step:

- Stores the result of calling `self._store.read_text(path)` in `text`.
- Stores the result of calling `text.splitlines()` in `lines`.
- Stores the result of calling `_sections(lines)` in `sections`.
- Stores the result of calling `sections.get('Data flow', [])` in `flow`.
- Declares `diagram` as a `list[str]` and stores the list `[]` in it.
- Stores `False` in `inside`.
- For each `line` in `flow`:
  - If `_FENCE.match(line)`:
    - Stores whether not (`inside`) in `inside`.
  - Otherwise, if `inside`:
    - Calls `diagram.append(line)`.
- Stores the result of calling `_header_fields(sections).get('Author', '')` in `author`.
- Stores `lines[0].removeprefix('# ').strip()` if `lines`, otherwise `''` in `title`.
- Gives back the result of calling `Proposal(path=path, title=title, author=author, sections={name: _paragraph(body) for name…`.

`src/design_review/infrastructure/markdown.py` lines 133 to 134:

```python
    def read_review(self, path: str) -> ReviewRecord:
        """A review record: the header fields and the seven sections."""
```

**Method `read_review` of class `MarkdownDocumentReader`.** A review record: the header fields and the seven sections.

It takes: `path` (a `str`).

It gives back a `ReviewRecord`.

`src/design_review/infrastructure/markdown.py` lines 135 to 187:

```python
        lines = self._store.read_text(path).splitlines()
        sections = _sections(lines)
        fields = _header_fields(sections)
        title = lines[0].removeprefix("# Design review:").strip() if lines else ""
        findings = []
        for row in table_rows(_section(sections, "Findings")):
            cls, _, note = row.get("Class", "").partition(",")
            findings.append(
                ReviewFinding(
                    row.get("#", ""), row.get("Finding", ""), row.get("Requirement", ""), cls.strip(), note.strip()
                )
            )
        disagreement_fields = _labeled(_section(sections, "Disagreement"))
        return ReviewRecord(
            path=path,
            system=title,
            date_text=fields.get("Date", ""),
            reviewers=fields.get("Reviewers", ""),
            author=fields.get("Author", ""),
            requirements_path=fields.get("Requirements file", ""),
            sections=tuple(name.split(" (")[0] for name in sections if name),
            used=tuple(
                UsedRequirement(
                    r.get("ID", ""), r.get("Requirement", ""), r.get("Target", ""), r.get("How to verify", "")
                )
                for r in table_rows(_section(sections, "Requirements used"))
            ),
            assessments=tuple(
                Assessment(r.get("ID", ""), r.get("Verdict", ""), r.get("Reason", ""))
                for r in table_rows(_section(sections, "Assessment"))
            ),
            findings=tuple(findings),
            decisions=_bullets(_section(sections, "Decisions")),
            risks=tuple(
                AcceptedRisk(r.get("Risk", ""), r.get("Owner", ""), r.get("Look again", ""))
                for r in table_rows(_section(sections, "Accepted risks"))
            ),
            actions=tuple(
                ActionItem(r.get("Action", ""), r.get("Owner", ""), r.get("Date", ""))
                for r in table_rows(_section(sections, "Action items"))
            ),
            disagreements=(
                (
                    Disagreement(
                        disagreement_fields.get("Finding", ""),
                        disagreement_fields.get("Author", ""),
                        disagreement_fields.get("Outcome", ""),
                    ),
                )
                if disagreement_fields
                else ()
            ),
        )
```

**`read_review`, part 1 of 1.**

Step by step:

- Stores the result of calling `self._store.read_text(path).splitlines()` in `lines`.
- Stores the result of calling `_sections(lines)` in `sections`.
- Stores the result of calling `_header_fields(sections)` in `fields`.
- Stores `lines[0].removeprefix('# Design review:…` if `lines`, otherwise `''` in `title`.
- Stores the list `[]` in `findings`.
- For each `row` in the result of calling `table_rows(_section(sections, 'Findings'))`:
  - Unpacks the result of calling `row.get('Class', '').partition(',')` into `(cls, _, note)`.
  - Calls `findings.append(ReviewFinding(row.get('#', ''), row.get('Finding', ''), row.get('Requirement', ''), cls.strip…`.
- Stores the result of calling `_labeled(_section(sections, 'Disagreement'))` in `disagreement_fields`.
- Gives back the result of calling `ReviewRecord(path=path, system=title, date_text=fields.get('Date', ''), reviewers=fields.…`.

`src/design_review/infrastructure/markdown.py` lines 189 to 201:

```python
    def read_checklist(self, path: str) -> Checklist:
        """Checklist items are lines like `- [ ] CHK-01 [throughput] Is the peak computed?`."""
        items: list[ChecklistItem] = []
        malformed: list[str] = []
        for line in self._store.read_text(path).splitlines():
            if not line.startswith("- ["):
                continue
            match = ITEM.match(line)
            if match:
                items.append(ChecklistItem(match.group(1), match.group(2), match.group(3)))
            else:
                malformed.append(line)
        return Checklist(path, tuple(items), tuple(malformed))
```

**Method `read_checklist` of class `MarkdownDocumentReader`.** Checklist items are lines like `- [ ] CHK-01 [throughput] Is the peak computed?`.

It takes: `path` (a `str`).

It gives back a `Checklist`.

Step by step:

- Declares `items` as a `list[ChecklistItem]` and stores the list `[]` in it.
- Declares `malformed` as a `list[str]` and stores the list `[]` in it.
- For each `line` in the result of calling `self._store.read_text(path).splitlines()`:
  - If not (`line.startswith('- [')`):
    - Skips to the next item (`continue`).
  - Stores the result of calling `ITEM.match(line)` in `match`.
  - If `match`:
    - Calls `items.append(ChecklistItem(match.group(1), match.group(2), match.group(3)))`.
  - Otherwise:
    - Calls `malformed.append(line)`.
- Gives back the result of calling `Checklist(path, tuple(items), tuple(malformed))`.

`src/design_review/infrastructure/markdown.py` lines 204 to 216:

```python
def _labeled(lines: list[str]) -> dict[str, str]:
    """`Label: text` paragraphs (Finding, Author, Outcome), text continuing until the next label."""
    pattern = re.compile(r"^(Finding|Author|Outcome):\s*(.*)$")
    values: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines:
        match = pattern.match(line.strip())
        if match:
            current = match.group(1)
            values[current] = [match.group(2)]
        elif current is not None and line.strip():
            values[current].append(line.strip())
    return {key: " ".join(parts) for key, parts in values.items()}
```

> **In plain words.** `A | B` in a type hint means "either A or B". `X | None` means a value that may be missing.

**Function `_labeled`.** `Label: text` paragraphs (Finding, Author, Outcome), text continuing until the next label.

It takes: `lines` (a `list[str]`).

It gives back a `dict[str, str]`.

Step by step:

- Stores the result of calling `re.compile('^(Finding|Author|Outcome):\\s*(.*)$')` in `pattern`.
- Declares `values` as a `dict[str, list[str]]` and stores the dictionary `{}` in it.
- Declares `current` as a `str | None` and stores nothing (`None`) in it.
- For each `line` in `lines`:
  - Stores the result of calling `pattern.match(line.strip())` in `match`.
  - If `match`:
    - Stores the result of calling `match.group(1)` in `current`.
    - Stores the list `[match.group(2)]` in `values[current]`.
  - Otherwise, if `current` is not the same object as `None` and `line.strip()`:
    - Calls `values[current].append(line.strip())`.
- Gives back a new dictionary made by a loop (`{key: ' '.join(parts) for key, parts in values.items()}`).

### `src/design_review/infrastructure/model_toml.py`

`src/design_review/infrastructure/model_toml.py` lines 1 to 12:

```python
"""Load and validate `model/uploads.toml` into the fitness model."""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from typing import Any

from design_review.application.ports import DocumentStore
from design_review.domain.capacity import LoadModel, ModelError
from design_review.domain.fitness import DurabilityScenario, FitnessModel, ThumbnailRequirement, ThumbnailScenario
from design_review.domain.queue_model import BurstProfile
```

> **In plain words.** A **docstring** is a text in triple quotes as the first thing in a module, class or function. Python keeps it as the thing's description, and ruff requires one on public code.
> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.
> **In plain words.** `from __future__ import annotations` makes every type hint in the file lazy text. Python no longer evaluates a hint when the file loads, so a hint may name a class defined further down.

**Module description.** Load and validate `model/uploads.toml` into the fitness model.

Imports:

- From `__future__` it takes `annotations`.
- It imports module `tomllib`.
- From `collections.abc` it takes `Mapping`.
- From `typing` it takes `Any`.
- From `design_review.application.ports` it takes `DocumentStore`.
- From `design_review.domain.capacity` it takes `LoadModel, ModelError`.
- From `design_review.domain.fitness` it takes `DurabilityScenario, FitnessModel, ThumbnailRequirement, ThumbnailScenario`.
- From `design_review.domain.queue_model` it takes `BurstProfile`.

`src/design_review/infrastructure/model_toml.py` lines 15 to 19:

```python
def _table(data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ModelError(f"the model file has no [{key}] table")
    return value
```

> **In plain words.** A **type hint** such as `x: int` or `-> str` says what kind of value a name holds or a function gives back. Python does not enforce hints when the program runs; the type checker mypy reads them before.
> **In plain words.** `return value` ends the function and gives the value back to whoever called it.
> **In plain words.** `obj[key]` looks a value up by key or position.
> **In plain words.** `raise Error(...)` stops the current function by signalling an error. `raise ... from None` hides the earlier error, so the user sees only the new, clearer message.
> **In plain words.** A **tuple** `(a, b)` is a fixed list of values that cannot be changed.
> **In plain words.** An **f-string** `f"...{value}..."` is text with Python expressions in braces; Python replaces each by its value. `{x!r}` shows the value the way Python would write it, with quotes.

**Function `_table`.**

It takes: `data` (a `Mapping[str, Any]`); `key` (a `str`).

It gives back a `Mapping[str, Any]`.

Step by step:

- Stores the result of calling `data.get(key)` in `value`.
- If not (`isinstance(value, dict)`):
  - Stops here by raising `ModelError(f'the model file has no [{key}] table')`.
- Gives back `value`.

`src/design_review/infrastructure/model_toml.py` lines 22 to 26:

```python
def _expect(table: Mapping[str, Any], name: str) -> bool:
    expect = table.get("expect")
    if expect not in ("pass", "fail"):
        raise ModelError(f"scenario {name!r}: expect must be 'pass' or 'fail', got {expect!r}")
    return bool(expect == "pass")
```

> **In plain words.** `==` tests equality, `is` tests that two names are the very same object (used for `None` and enum members), `in` tests membership.

**Function `_expect`.**

It takes: `table` (a `Mapping[str, Any]`); `name` (a `str`).

It gives back a `bool`.

Step by step:

- Stores the result of calling `table.get('expect')` in `expect`.
- If `expect` is not in `('pass', 'fail')`:
  - Stops here by raising `ModelError(f"scenario {name!r}: expect must be 'pass' or 'fail', got {expect!r}")`.
- Gives back the result of calling `bool(expect == 'pass')`.

`src/design_review/infrastructure/model_toml.py` lines 29 to 30:

```python
class TomlModelSource:
    """Reads the model through the document store, so tests need no disk."""
```

> **In plain words.** A **class** is a blueprint for objects that bundle data with the functions that work on it. `class B(A)` means B is a kind of A and starts with everything A has.

**Class `TomlModelSource`**. Reads the model through the document store, so tests need no disk.

`src/design_review/infrastructure/model_toml.py` lines 32 to 33:

```python
    def __init__(self, store: DocumentStore) -> None:
        self._store = store
```

**Method `__init__` of class `TomlModelSource`.**

It takes: `store` (a `DocumentStore`).

It gives back a `None`.

Step by step:

- Stores `store` in `self._store`.

`src/design_review/infrastructure/model_toml.py` lines 35 to 36:

```python
    def load(self, path: str) -> FitnessModel:
        """Parse the file; a missing table or a value out of range raises ModelError."""
```

**Method `load` of class `TomlModelSource`.** Parse the file; a missing table or a value out of range raises ModelError.

It takes: `path` (a `str`).

It gives back a `FitnessModel`.

`src/design_review/infrastructure/model_toml.py` lines 37 to 76:

```python
        try:
            data = tomllib.loads(self._store.read_text(path))
        except tomllib.TOMLDecodeError as problem:
            raise ModelError(f"{path} is not valid TOML: {problem}") from None
        load_table, burst_table = _table(data, "load"), _table(data, "burst")
        service, requirement = _table(data, "service"), _table(data, "requirement")
        try:
            load = LoadModel(
                listings_per_week=int(load_table["listings_per_week"]),
                photos_per_listing=int(load_table["photos_per_listing"]),
                weekend_share=float(load_table["weekend_share"]),
                weekend_days=float(load_table["weekend_days"]),
                peak_uploads_per_second=float(requirement["peak_uploads_per_second"]),
            )
            burst = BurstProfile(
                average_rate=load.average_rate,
                peak_rate=load.peak_uploads_per_second,
                every_seconds=int(burst_table["every_seconds"]),
                length_seconds=int(burst_table["length_seconds"]),
            )
            thumbnails = tuple(
                ThumbnailScenario(name, int(table["workers"]), _expect(table, name))
                for name, table in _table(data, "thumbnails").items()
            )
            durability = tuple(
                DurabilityScenario(name, tuple(table["order"]), _expect(table, name))
                for name, table in _table(data, "durability").items()
            )
            return FitnessModel(
                load=load,
                seconds_per_photo=float(service["seconds_per_photo_per_worker"]),
                burst=burst,
                requirement=ThumbnailRequirement(
                    float(requirement["thumbnail_percentile"]), float(requirement["thumbnail_seconds"])
                ),
                thumbnails=thumbnails,
                durability=durability,
            )
        except KeyError as missing:
            raise ModelError(f"the model file is missing {missing}") from None
```

> **In plain words.** A **`try` / `except` block** runs the steps under `try`. If an error of the named kind happens, Python jumps to the matching `except` steps instead of stopping the program. `finally` steps always run.
> **In plain words.** A call such as `f(a, key=value)` passes `a` by position and `key` by name (a **keyword argument**).
> **In plain words.** A **generator expression** `(x for x in items)` is like a list comprehension, but it hands out one value at a time instead of building the whole list; here it is passed straight to a function such as `tuple(...)` or `sum(...)`.

**`load`, part 1 of 1.**

Step by step:

- Tries:
  - Stores the result of calling `tomllib.loads(self._store.read_text(path))` in `data`.
- If `tomllib.TOMLDecodeError` happens (named `problem`):
  - Stops here by raising `ModelError(f'{path} is not valid TOML: {problem}')` (`from None` hides the earlier error).
- Unpacks the tuple `(_table(data, 'load'), _table(data, 'burst'))` into `(load_table, burst_table)`.
- Unpacks the tuple `(_table(data, 'service'), _table(data, 'requirement'))` into `(service, requirement)`.
- Tries:
  - Stores the result of calling `LoadModel(listings_per_week=int(load_table['listings_per_week']), photos_per_listing=int(…` in `load`.
  - Stores the result of calling `BurstProfile(average_rate=load.average_rate, peak_rate=load.peak_uploads_per_second, ever…` in `burst`.
  - Stores the result of calling `tuple((ThumbnailScenario(name, int(table['workers']), _expect(table, name)) for name, tab…` in `thumbnails`.
  - Stores the result of calling `tuple((DurabilityScenario(name, tuple(table['order']), _expect(table, name)) for name, ta…` in `durability`.
  - Gives back the result of calling `FitnessModel(load=load, seconds_per_photo=float(service['seconds_per_photo_per_worker']),…`.
- If `KeyError` happens (named `missing`):
  - Stops here by raising `ModelError(f'the model file is missing {missing}')` (`from None` hides the earlier error).

### `src/design_review/infrastructure/settings.py`

`src/design_review/infrastructure/settings.py` lines 1 to 9:

```python
"""Settings from the environment, validated once at start-up (twelve-factor)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from design_review.application.check_documents import CheckSettings
```

> **In plain words.** A **docstring** is a text in triple quotes as the first thing in a module, class or function. Python keeps it as the thing's description, and ruff requires one on public code.
> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.
> **In plain words.** `from __future__ import annotations` makes every type hint in the file lazy text. Python no longer evaluates a hint when the file loads, so a hint may name a class defined further down.

**Module description.** Settings from the environment, validated once at start-up (twelve-factor).

Imports:

- From `__future__` it takes `annotations`.
- From `collections.abc` it takes `Mapping`.
- From `dataclasses` it takes `dataclass`.
- From `pathlib` it takes `Path`.
- From `design_review.application.check_documents` it takes `CheckSettings`.

`src/design_review/infrastructure/settings.py` lines 12 to 13:

```python
class SettingsError(ValueError):
    """An environment variable holds a value the program cannot use."""
```

> **In plain words.** A **class** is a blueprint for objects that bundle data with the functions that work on it. `class B(A)` means B is a kind of A and starts with everything A has.
> **In plain words.** A class that inherits from `Exception` is a new kind of **error**. `raise` stops the current function with it, and a `try ... except` further up decides what to do.

**Class `SettingsError`**, a kind of `ValueError`. An environment variable holds a value the program cannot use.

`src/design_review/infrastructure/settings.py` lines 16 to 22:

```python
@dataclass(frozen=True)
class Settings:
    """Where the documents are, where the report goes, and the proposal size limit."""

    root: Path
    report_dir: str
    check: CheckSettings
```

> **In plain words.** A **type hint** such as `x: int` or `-> str` says what kind of value a name holds or a function gives back. Python does not enforce hints when the program runs; the type checker mypy reads them before.
> **In plain words.** A call such as `f(a, key=value)` passes `a` by position and `key` by name (a **keyword argument**).
> **In plain words.** A **dataclass** is a class that mainly holds data. `@dataclass` writes `__init__`, `__repr__` and `__eq__` for you from the annotated fields; `frozen=True` forbids changing a field after the object is created.

**Class `Settings`**. Where the documents are, where the report goes, and the proposal size limit. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `root`: a `Path`.
- Field `report_dir`: a `str`.
- Field `check`: a `CheckSettings`.

`src/design_review/infrastructure/settings.py` lines 25 to 34:

```python
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
```

> **In plain words.** A **`try` / `except` block** runs the steps under `try`. If an error of the named kind happens, Python jumps to the matching `except` steps instead of stopping the program. `finally` steps always run.
> **In plain words.** `return value` ends the function and gives the value back to whoever called it.
> **In plain words.** `==` tests equality, `is` tests that two names are the very same object (used for `None` and enum members), `in` tests membership.
> **In plain words.** `raise Error(...)` stops the current function by signalling an error. `raise ... from None` hides the earlier error, so the user sees only the new, clearer message.
> **In plain words.** `obj[key]` looks a value up by key or position.
> **In plain words.** A **tuple** `(a, b)` is a fixed list of values that cannot be changed.
> **In plain words.** An **f-string** `f"...{value}..."` is text with Python expressions in braces; Python replaces each by its value. `{x!r}` shows the value the way Python would write it, with quotes.

**Function `load_settings`.** Read REVIEW_ROOT, REPORT_DIR and PROPOSAL_MAX_WORDS.

It takes: `env` (a `Mapping[str, str]`).

It gives back a `Settings`.

Step by step:

- Stores the result of calling `env.get('PROPOSAL_MAX_WORDS', '1000')` in `raw`.
- Tries:
  - Stores the result of calling `int(raw)` in `words`.
- If `ValueError` happens:
  - Stops here by raising `SettingsError(f'PROPOSAL_MAX_WORDS must be a whole number, got {raw!r}')` (`from None` hides the earlier error).
- If `words` is at most `0`:
  - Stops here by raising `SettingsError(f'PROPOSAL_MAX_WORDS must be positive, got {words}')`.
- Gives back the result of calling `Settings(Path(env.get('REVIEW_ROOT', '.')), env.get('REPORT_DIR', 'build'), CheckSettings…`.

## Try it yourself

```bash
.venv/bin/python -c "import design_review.infrastructure.filesystem; print(design_review.infrastructure.filesystem.__doc__)"
```
Prints the module's description: `The document store on the local file system.`

```bash
.venv/bin/python -c "import design_review.infrastructure.markdown; print(design_review.infrastructure.markdown.__doc__)"
```
Prints the module's description: `Parse the Markdown of each document type into the domain's values.`

```bash
.venv/bin/mypy
```
Checks the whole project (the `files` setting in `pyproject.toml`), these files included. Prints `Success: no issues found in 38 source files`.

```bash
.venv/bin/ruff check src/design_review/infrastructure/__init__.py src/design_review/infrastructure/filesystem.py src/design_review/infrastructure/markdown.py src/design_review/infrastructure/model_toml.py src/design_review/infrastructure/settings.py
```
Prints `All checks passed!`.

```bash
grep -c "^def \|^class \|    def " src/design_review/infrastructure/filesystem.py
```
Counts the functions, methods and classes in `src/design_review/infrastructure/filesystem.py`.

## Mistakes people make

- Putting a business rule in an adapter, where the domain tests cannot see it.
- Forgetting to close a connection or file. The adapters use `with` blocks and context managers.
- Trusting input from outside. Adapters check paths, shapes and ranges before handing values inward.

## Check yourself

1. What is `FileSystemStore` for?
   **Answer:** Reads the repository's documents under one root. Paths are relative and may not leave the root.
2. What is `_header_fields` for?
   **Answer:** `Author:`, `Date:` and the other header fields, read only from the lines before the first heading.
3. What is `_section` for?
   **Answer:** The lines of the first section whose heading starts with the prefix (headings may carry a parenthetical).
4. What is `table_rows` for?
   **Answer:** The rows of the first Markdown table in the lines, keyed by the header cells.
5. What is `MarkdownDocumentReader` for?
   **Answer:** Reads the repository's four document types from a store.

## Further reading

- Python 3.12 tutorial, classes: <https://docs.python.org/3.12/tutorial/classes.html>
- Python 3.12 language reference: <https://docs.python.org/3.12/reference/>
- Type hints: <https://docs.python.org/3.12/library/typing.html>
