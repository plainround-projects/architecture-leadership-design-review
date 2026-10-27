# Application layer code

## What it is

The use cases: the steps that join domain rules to the outside world through small interfaces (ports). (Every term is explained where it first appears in the walkthrough below.)

## Why this repository uses it

This is where the repository's application work happens. Reading it file by file, with every line explained, is how a reader sees the work that was done.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `src/design_review/application/__init__.py` | 1 lines. Use cases and the ports they need. Depends on the domain only. |
| `src/design_review/application/check_documents.py` | 67 lines. The use case behind `design-review check`, and the one behind `design-review fitness`. |
| `src/design_review/application/ports.py` | 41 lines. What the use cases need from the outside world. |
| `src/design_review/application/reporting.py` | 61 lines. Format reports as text for the terminal and as Markdown for the build artifact. |

## How it works underneath

The application layer says *what* happens in what order (check every document, export a person's data, collect the evidence) and asks the outside world for what it needs only through `ports.py`, a list of `Protocol` classes. It imports the domain and nothing outer.

## Walkthrough of this repository's use

### `src/design_review/application/__init__.py`

`src/design_review/application/__init__.py` lines 1 to 1:

```python
"""Use cases and the ports they need. Depends on the domain only."""
```

> **In plain words.** A **docstring** is a text in triple quotes as the first thing in a module, class or function. Python keeps it as the thing's description, and ruff requires one on public code.

**Module description.** Use cases and the ports they need. Depends on the domain only.

### `src/design_review/application/check_documents.py`

`src/design_review/application/check_documents.py` lines 1 to 13:

```python
"""The use case behind `design-review check`, and the one behind `design-review fitness`."""

from __future__ import annotations

from dataclasses import dataclass

from design_review.application.ports import DocumentReader, DocumentStore, ModelSource
from design_review.domain.checklist import check_checklist
from design_review.domain.findings import Finding, Report, error
from design_review.domain.fitness import FitnessReport, run_fitness
from design_review.domain.proposal import check_proposal
from design_review.domain.requirements import RequirementSet, check_requirements
from design_review.domain.review import ReviewRecord, check_review, warn_long_must_fix
```

> **In plain words.** A **docstring** is a text in triple quotes as the first thing in a module, class or function. Python keeps it as the thing's description, and ruff requires one on public code.
> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.
> **In plain words.** `from __future__ import annotations` makes every type hint in the file lazy text. Python no longer evaluates a hint when the file loads, so a hint may name a class defined further down.

**Module description.** The use case behind `design-review check`, and the one behind `design-review fitness`.

Imports:

- From `__future__` it takes `annotations`.
- From `dataclasses` it takes `dataclass`.
- From `design_review.application.ports` it takes `DocumentReader, DocumentStore, ModelSource`.
- From `design_review.domain.checklist` it takes `check_checklist`.
- From `design_review.domain.findings` it takes `Finding, Report, error`.
- From `design_review.domain.fitness` it takes `FitnessReport, run_fitness`.
- From `design_review.domain.proposal` it takes `check_proposal`.
- From `design_review.domain.requirements` it takes `RequirementSet, check_requirements`.
- From `design_review.domain.review` it takes `ReviewRecord, check_review, warn_long_must_fix`.

`src/design_review/application/check_documents.py` lines 15 to 20:

```python
PROPOSAL_FOLDER = "docs/proposals"
REQUIREMENTS_FOLDER = "docs/requirements"
REVIEW_FOLDER = "docs/reviews"
CHECKLIST_PATH = "docs/checklists/design-checklist.md"
MODEL_PATH = "model/uploads.toml"
PRIMARY_REQUIREMENTS = "docs/requirements/uploads-nfrs.md"
```

> **In plain words.** A name written in CAPITAL letters is a **constant** by convention: a value set once, not changed later.

These module-level lines:

- Stores the text `'docs/proposals'` in `PROPOSAL_FOLDER`.
- Stores the text `'docs/requirements'` in `REQUIREMENTS_FOLDER`.
- Stores the text `'docs/reviews'` in `REVIEW_FOLDER`.
- Stores the text `'docs/checklists/design-checklist.md'` in `CHECKLIST_PATH`.
- Stores the text `'model/uploads.toml'` in `MODEL_PATH`.
- Stores the text `'docs/requirements/uploads-nfrs.md'` in `PRIMARY_REQUIREMENTS`.

`src/design_review/application/check_documents.py` lines 23 to 27:

```python
@dataclass(frozen=True)
class CheckSettings:
    """The size of two pages."""

    proposal_max_words: int = 1000
```

> **In plain words.** A **class** is a blueprint for objects that bundle data with the functions that work on it. `class B(A)` means B is a kind of A and starts with everything A has.
> **In plain words.** A **type hint** such as `x: int` or `-> str` says what kind of value a name holds or a function gives back. Python does not enforce hints when the program runs; the type checker mypy reads them before.
> **In plain words.** A call such as `f(a, key=value)` passes `a` by position and `key` by name (a **keyword argument**).
> **In plain words.** A **dataclass** is a class that mainly holds data. `@dataclass` writes `__init__`, `__repr__` and `__eq__` for you from the annotated fields; `frozen=True` forbids changing a field after the object is created.

**Class `CheckSettings`**. The size of two pages. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `proposal_max_words`: a `int`, default `1000`.

`src/design_review/application/check_documents.py` lines 30 to 31:

```python
def check_documents(store: DocumentStore, reader: DocumentReader, settings: CheckSettings) -> Report:
    """Proposals, requirements, review records and the checklist: every rule, every file."""
```

**Function `check_documents`.** Proposals, requirements, review records and the checklist: every rule, every file.

It takes: `store` (a `DocumentStore`); `reader` (a `DocumentReader`); `settings` (a `CheckSettings`).

It gives back a `Report`.

`src/design_review/application/check_documents.py` lines 32 to 61:

```python
    findings: list[Finding] = []
    subjects: list[str] = []
    requirement_sets: dict[str, RequirementSet] = {}
    for path in store.list_paths(REQUIREMENTS_FOLDER):
        requirement_sets[path] = reader.read_requirements(path)
        subjects.append(path)
        findings.extend(check_requirements(requirement_sets[path]))
    for path in store.list_paths(PROPOSAL_FOLDER):
        subjects.append(path)
        findings.extend(check_proposal(reader.read_proposal(path), settings.proposal_max_words))
    reviews: list[ReviewRecord] = []
    for path in store.list_paths(REVIEW_FOLDER):
        if not path.rsplit("/", 1)[1].startswith("review-"):
            continue
        review = reader.read_review(path)
        if review.requirements_path == PRIMARY_REQUIREMENTS:
            reviews.append(review)
        subjects.append(path)
        requirement_set = requirement_sets.get(review.requirements_path)
        if requirement_set is None:
            findings.append(
                error(
                    "REV002",
                    path,
                    f"'Requirements file' {review.requirements_path!r} is not a requirements document here",
                )
            )
            continue
        findings.extend(check_review(review, requirement_set))
        findings.extend(warn_long_must_fix(review))
```

> **In plain words.** `obj[key]` looks a value up by key or position.
> **In plain words.** A **dictionary** `{key: value}` maps keys to values.
> **In plain words.** A **tuple** `(a, b)` is a fixed list of values that cannot be changed.
> **In plain words.** A **`for` loop** repeats its steps once for each item of a collection. `range(n)` counts from 0 to n-1.
> **In plain words.** `==` tests equality, `is` tests that two names are the very same object (used for `None` and enum members), `in` tests membership.
> **In plain words.** An **f-string** `f"...{value}..."` is text with Python expressions in braces; Python replaces each by its value. `{x!r}` shows the value the way Python would write it, with quotes.

**`check_documents`, part 1 of 2.**

Step by step:

- Declares `findings` as a `list[Finding]` and stores the list `[]` in it.
- Declares `subjects` as a `list[str]` and stores the list `[]` in it.
- Declares `requirement_sets` as a `dict[str, RequirementSet]` and stores the dictionary `{}` in it.
- For each `path` in the result of calling `store.list_paths(REQUIREMENTS_FOLDER)`:
  - Stores the result of calling `reader.read_requirements(path)` in `requirement_sets[path]`.
  - Calls `subjects.append(path)`.
  - Calls `findings.extend(check_requirements(requirement_sets[path]))`.
- For each `path` in the result of calling `store.list_paths(PROPOSAL_FOLDER)`:
  - Calls `subjects.append(path)`.
  - Calls `findings.extend(check_proposal(reader.read_proposal(path), settings.proposal_max_words))`.
- Declares `reviews` as a `list[ReviewRecord]` and stores the list `[]` in it.
- For each `path` in the result of calling `store.list_paths(REVIEW_FOLDER)`:
  - If not (`path.rsplit('/', 1)[1].startswith('review-')`):
    - Skips to the next item (`continue`).
  - Stores the result of calling `reader.read_review(path)` in `review`.
  - If `review.requirements_path` equals `PRIMARY_REQUIREMENTS`:
    - Calls `reviews.append(review)`.
  - Calls `subjects.append(path)`.
  - Stores the result of calling `requirement_sets.get(review.requirements_path)` in `requirement_set`.
  - If `requirement_set` is the same object as `None`:
    - Calls `findings.append(error('REV002', path, f"'Requirements file' {review.requirements_path!r} is not a requirement…`.
    - Skips to the next item (`continue`).
  - Calls `findings.extend(check_review(review, requirement_set))`.
  - Calls `findings.extend(warn_long_must_fix(review))`.

`src/design_review/application/check_documents.py` lines 62 to 71:

```python
    if store.exists(CHECKLIST_PATH) and PRIMARY_REQUIREMENTS in requirement_sets:
        subjects.append(CHECKLIST_PATH)
        findings.extend(
            check_checklist(reader.read_checklist(CHECKLIST_PATH), requirement_sets[PRIMARY_REQUIREMENTS], reviews)
        )
    else:
        findings.append(
            error("DOC001", CHECKLIST_PATH, "the design checklist or the primary requirements document is missing")
        )
    return Report(tuple(subjects), tuple(findings))
```

> **In plain words.** `return value` ends the function and gives the value back to whoever called it.

**`check_documents`, part 2 of 2.**

Step by step:

- If `store.exists(CHECKLIST_PATH)` and `PRIMARY_REQUIREMENTS` is in `requirement_sets`:
  - Calls `subjects.append(CHECKLIST_PATH)`.
  - Calls `findings.extend(check_checklist(reader.read_checklist(CHECKLIST_PATH), requirement_sets[PRIMARY_REQUIREMENTS]…`.
- Otherwise:
  - Calls `findings.append(error('DOC001', CHECKLIST_PATH, 'the design checklist or the primary requirements document is…`.
- Gives back the result of calling `Report(tuple(subjects), tuple(findings))`.

`src/design_review/application/check_documents.py` lines 74 to 78:

```python
def run_fitness_functions(
    models: ModelSource, path: str = MODEL_PATH, horizon_seconds: int | None = None
) -> FitnessReport:
    """Load the model and evaluate every scenario."""
    return run_fitness(models.load(path), horizon_seconds)
```

> **In plain words.** `A | B` in a type hint means "either A or B". `X | None` means a value that may be missing.

**Function `run_fitness_functions`.** Load the model and evaluate every scenario.

It takes: `models` (a `ModelSource`); `path` (a `str`), default `MODEL_PATH`; `horizon_seconds` (a `int | None`), default `None`.

It gives back a `FitnessReport`.

Step by step:

- Gives back the result of calling `run_fitness(models.load(path), horizon_seconds)`.

### `src/design_review/application/ports.py`

`src/design_review/application/ports.py` lines 1 to 11:

```python
"""What the use cases need from the outside world."""

from __future__ import annotations

from typing import Protocol

from design_review.domain.checklist import Checklist
from design_review.domain.fitness import FitnessModel
from design_review.domain.proposal import Proposal
from design_review.domain.requirements import RequirementSet
from design_review.domain.review import ReviewRecord
```

> **In plain words.** A **docstring** is a text in triple quotes as the first thing in a module, class or function. Python keeps it as the thing's description, and ruff requires one on public code.
> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.
> **In plain words.** `from __future__ import annotations` makes every type hint in the file lazy text. Python no longer evaluates a hint when the file loads, so a hint may name a class defined further down.

**Module description.** What the use cases need from the outside world.

Imports:

- From `__future__` it takes `annotations`.
- From `typing` it takes `Protocol`.
- From `design_review.domain.checklist` it takes `Checklist`.
- From `design_review.domain.fitness` it takes `FitnessModel`.
- From `design_review.domain.proposal` it takes `Proposal`.
- From `design_review.domain.requirements` it takes `RequirementSet`.
- From `design_review.domain.review` it takes `ReviewRecord`.

`src/design_review/application/ports.py` lines 14 to 31:

```python
class DocumentStore(Protocol):
    """Reads and writes the repository's files by path relative to its root."""

    def list_paths(self, folder: str) -> list[str]:
        """Markdown files directly inside the folder, sorted; empty when the folder is missing."""
        ...

    def read_text(self, path: str) -> str:
        """The text of a file."""
        ...

    def exists(self, path: str) -> bool:
        """True when the file exists."""
        ...

    def write_text(self, path: str, text: str) -> None:
        """Replace a file, creating its folder."""
        ...
```

> **In plain words.** A **class** is a blueprint for objects that bundle data with the functions that work on it. `class B(A)` means B is a kind of A and starts with everything A has.
> **In plain words.** A **Protocol** describes the methods an object must have, without requiring inheritance. Any class with those methods fits. A body of `...` means "no code here, only the shape".
> **In plain words.** A **type hint** such as `x: int` or `-> str` says what kind of value a name holds or a function gives back. Python does not enforce hints when the program runs; the type checker mypy reads them before.
> **In plain words.** `obj[key]` looks a value up by key or position.

**Class `DocumentStore`**, a kind of `Protocol`. Reads and writes the repository's files by path relative to its root.

Its methods, in order:

**Method `list_paths` of class `DocumentStore`.** Markdown files directly inside the folder, sorted; empty when the folder is missing.

It takes: `folder` (a `str`).

It gives back a `list[str]`.

**Method `read_text` of class `DocumentStore`.** The text of a file.

It takes: `path` (a `str`).

It gives back a `str`.

**Method `exists` of class `DocumentStore`.** True when the file exists.

It takes: `path` (a `str`).

It gives back a `bool`.

**Method `write_text` of class `DocumentStore`.** Replace a file, creating its folder.

It takes: `path` (a `str`); `text` (a `str`).

It gives back a `None`.

`src/design_review/application/ports.py` lines 34 to 51:

```python
class DocumentReader(Protocol):
    """Turns each document type's text into the domain's values."""

    def read_requirements(self, path: str) -> RequirementSet:
        """Parse a requirements document."""
        ...

    def read_proposal(self, path: str) -> Proposal:
        """Parse a proposal."""
        ...

    def read_review(self, path: str) -> ReviewRecord:
        """Parse a review record."""
        ...

    def read_checklist(self, path: str) -> Checklist:
        """Parse a checklist."""
        ...
```

**Class `DocumentReader`**, a kind of `Protocol`. Turns each document type's text into the domain's values.

Its methods, in order:

**Method `read_requirements` of class `DocumentReader`.** Parse a requirements document.

It takes: `path` (a `str`).

It gives back a `RequirementSet`.

**Method `read_proposal` of class `DocumentReader`.** Parse a proposal.

It takes: `path` (a `str`).

It gives back a `Proposal`.

**Method `read_review` of class `DocumentReader`.** Parse a review record.

It takes: `path` (a `str`).

It gives back a `ReviewRecord`.

**Method `read_checklist` of class `DocumentReader`.** Parse a checklist.

It takes: `path` (a `str`).

It gives back a `Checklist`.

`src/design_review/application/ports.py` lines 54 to 59:

```python
class ModelSource(Protocol):
    """Loads the fitness model."""

    def load(self, path: str) -> FitnessModel:
        """Read and validate the model file."""
        ...
```

**Class `ModelSource`**, a kind of `Protocol`. Loads the fitness model.

Its methods, in order:

**Method `load` of class `ModelSource`.** Read and validate the model file.

It takes: `path` (a `str`).

It gives back a `FitnessModel`.

### `src/design_review/application/reporting.py`

`src/design_review/application/reporting.py` lines 1 to 6:

```python
"""Format reports as text for the terminal and as Markdown for the build artifact."""

from __future__ import annotations

from design_review.domain.findings import Report
from design_review.domain.fitness import FitnessReport
```

> **In plain words.** A **docstring** is a text in triple quotes as the first thing in a module, class or function. Python keeps it as the thing's description, and ruff requires one on public code.
> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.
> **In plain words.** `from __future__ import annotations` makes every type hint in the file lazy text. Python no longer evaluates a hint when the file loads, so a hint may name a class defined further down.

**Module description.** Format reports as text for the terminal and as Markdown for the build artifact.

Imports:

- From `__future__` it takes `annotations`.
- From `design_review.domain.findings` it takes `Report`.
- From `design_review.domain.fitness` it takes `FitnessReport`.

`src/design_review/application/reporting.py` lines 9 to 17:

```python
def render_text(report: Report) -> str:
    """One line per finding, then the verdict."""
    lines = [
        f"{finding.severity.value.upper():7} {finding.code} {finding.subject}: {finding.message}"
        for finding in report.findings
    ]
    counts = f"{len(report.subjects)} documents checked, {len(report.errors)} errors, {len(report.warnings)} warnings"
    lines.append(f"{'OK' if report.ok else 'FAILED'}: {counts}")
    return "\n".join(lines)
```

> **In plain words.** A **type hint** such as `x: int` or `-> str` says what kind of value a name holds or a function gives back. Python does not enforce hints when the program runs; the type checker mypy reads them before.
> **In plain words.** `return value` ends the function and gives the value back to whoever called it.
> **In plain words.** A **list comprehension** `[x for x in items if test]` is a loop written inside brackets: it builds a new list from the items that pass the test.
> **In plain words.** An **f-string** `f"...{value}..."` is text with Python expressions in braces; Python replaces each by its value. `{x!r}` shows the value the way Python would write it, with quotes.
> **In plain words.** `A if test else B` is a **conditional expression**: its value is A when the test is true, otherwise B.

**Function `render_text`.** One line per finding, then the verdict.

It takes: `report` (a `Report`).

It gives back a `str`.

Step by step:

- Stores a new list made by a loop (`[f'{finding.severity.value.upper():7} {finding.code} {finding.subject…`) in `lines`.
- Stores a text built with values filled in (`f'{len(report.subjects)} documents checked, {len(report.errors)} erro…`) in `counts`.
- Calls `lines.append(f"{('OK' if report.ok else 'FAILED')}: {counts}")`.
- Gives back the result of calling `'\n'.join(lines)`.

`src/design_review/application/reporting.py` lines 20 to 45:

```python
def render_fitness(report: FitnessReport) -> str:
    """The fitness table: each scenario, what it measured, and whether it matched the review's expectation."""
    lines = ["thumbnails (95% of uploads within the target; capacity must also cover the average rate)"]
    for item in report.thumbnails:
        verdict = "PASS" if item.passed else "FAIL"
        match = "as expected" if item.as_expected else "UNEXPECTED"
        lines.append(
            f"  {item.scenario.name:8} {item.scenario.workers:3} workers  capacity {item.capacity:5.1f}/s  "
            f"average {item.average_rate:4.2f}/s  peak needs {item.workers_for_peak} workers  "
            f"wait at p{item.percentile:g} {item.wait_at_percentile:8.1f} s  {verdict}  ({match})"
        )
    lines.append("write order (a crash at any point must not lose an upload the seller was told about)")
    for verdict_item in report.durability:
        verdict = "PASS" if verdict_item.result.holds else "FAIL"
        match = "as expected" if verdict_item.as_expected else "UNEXPECTED"
        lines.append(
            f"  {verdict_item.scenario.name:8} {' > '.join(verdict_item.scenario.order)}  {verdict}  ({match})"
        )
        lines.extend(f"      lost: {violation}" for violation in verdict_item.result.violations)
        lines.extend(f"      orphan: {orphan}" for orphan in verdict_item.result.orphans)
    lines.append(
        "OK: every scenario gave the verdict the review expected"
        if report.ok
        else "FAILED: a scenario surprised the review"
    )
    return "\n".join(lines)
```

> **In plain words.** A **`for` loop** repeats its steps once for each item of a collection. `range(n)` counts from 0 to n-1.
> **In plain words.** A **generator expression** `(x for x in items)` is like a list comprehension, but it hands out one value at a time instead of building the whole list; here it is passed straight to a function such as `tuple(...)` or `sum(...)`.

**Function `render_fitness`.** The fitness table: each scenario, what it measured, and whether it matched the review's expectation.

It takes: `report` (a `FitnessReport`).

It gives back a `str`.

Step by step:

- Stores the list `['thumbnails (95% of uploads within the target; capacity must also co…` in `lines`.
- For each `item` in `report.thumbnails`:
  - Stores `'PASS'` if `item.passed`, otherwise `'FAIL'` in `verdict`.
  - Stores `'as expected'` if `item.as_expected`, otherwise `'UNEXPECTED'` in `match`.
  - Calls `lines.append(f' {item.scenario.name:8} {item.scenario.workers:3} workers capacity {item.capacity:5.1f}/s aver…`.
- Calls `lines.append('write order (a crash at any point must not lose an upload the seller was told about)')`.
- For each `verdict_item` in `report.durability`:
  - Stores `'PASS'` if `verdict_item.result.holds`, otherwise `'FAIL'` in `verdict`.
  - Stores `'as expected'` if `verdict_item.as_expected`, otherwise `'UNEXPECTED'` in `match`.
  - Calls `lines.append(f" {verdict_item.scenario.name:8} {' > '.join(verdict_item.scenario.order)} {verdict} ({match})")`.
  - Calls `lines.extend((f' lost: {violation}' for violation in verdict_item.result.violations))`.
  - Calls `lines.extend((f' orphan: {orphan}' for orphan in verdict_item.result.orphans))`.
- Calls `lines.append('OK: every scenario gave the verdict the review expected' if report.ok else 'FAILED: a scenario …`.
- Gives back the result of calling `'\n'.join(lines)`.

`src/design_review/application/reporting.py` lines 48 to 69:

````python
def render_markdown(report: Report, fitness: FitnessReport) -> str:
    """The report the CI run uploads: document findings, then the fitness functions."""
    verdict = "OK" if report.ok and fitness.ok else "FAILED"
    lines = [
        "# Design review report",
        "",
        f"**Verdict:** {verdict}",
        "",
        "## Documents checked",
        "",
        *[f"- `{subject}`" for subject in report.subjects],
        "",
        "## Findings",
        "",
    ]
    if report.findings:
        lines += ["| Severity | Code | Document | Message |", "| --- | --- | --- | --- |"]
        lines += [f"| {f.severity.value} | {f.code} | `{f.subject}` | {f.message} |" for f in report.findings]
    else:
        lines.append("None.")
    lines += ["", "## Fitness functions", "", "```text", render_fitness(fitness), "```", ""]
    return "\n".join(lines)
````

> **In plain words.** `*items` **unpacks** a sequence into separate values; `**options` does the same for a dictionary's keys and values.

**Function `render_markdown`.** The report the CI run uploads: document findings, then the fitness functions.

It takes: `report` (a `Report`); `fitness` (a `FitnessReport`).

It gives back a `str`.

Step by step:

- Stores `'OK'` if `report.ok` and `fitness.ok`, otherwise `'FAILED'` in `verdict`.
- Stores the list `['# Design review report', '', f'**Verdict:** {verdict}', '', '## Doc…` in `lines`.
- If `report.findings`:
  - Adds the list `['| Severity | Code | Document | Message |', '| --- | --- | --- | ---…` to `lines`.
  - Adds a new list made by a loop (`[f'| {f.severity.value} | {f.code} | `{f.subject}` | {f.message} |' f…`) to `lines`.
- Otherwise:
  - Calls `lines.append('None.')`.
- Adds the list `['', '## Fitness functions', '', '```text', render_fitness(fitness), …` to `lines`.
- Gives back the result of calling `'\n'.join(lines)`.

## Try it yourself

```bash
.venv/bin/python -c "import design_review.application.check_documents; print(design_review.application.check_documents.__doc__)"
```
Prints the module's description: `The use case behind `design-review check`, and the one behind `design-review fitness`.`

```bash
.venv/bin/python -c "import design_review.application.ports; print(design_review.application.ports.__doc__)"
```
Prints the module's description: `What the use cases need from the outside world.`

```bash
.venv/bin/mypy
```
Checks the whole project (the `files` setting in `pyproject.toml`), these files included. Prints `Success: no issues found in 38 source files`.

```bash
.venv/bin/ruff check src/design_review/application/__init__.py src/design_review/application/check_documents.py src/design_review/application/ports.py src/design_review/application/reporting.py
```
Prints `All checks passed!`.

```bash
grep -c "^def \|^class \|    def " src/design_review/application/check_documents.py
```
Counts the functions, methods and classes in `src/design_review/application/check_documents.py`.

## Mistakes people make

- Importing an adapter directly. Use the port; the adapter is passed in from the outside.
- Putting a rule here that belongs in the domain, where it can be tested without any setup.
- Catching an error too early. Use cases let named errors travel up to the interfaces layer.

## Check yourself

1. What is `CheckSettings` for?
   **Answer:** The size of two pages.
2. What is `check_documents` for?
   **Answer:** Proposals, requirements, review records and the checklist: every rule, every file.
3. What is `run_fitness_functions` for?
   **Answer:** Load the model and evaluate every scenario.
4. What is `DocumentStore` for?
   **Answer:** Reads and writes the repository's files by path relative to its root.
5. What is `DocumentReader` for?
   **Answer:** Turns each document type's text into the domain's values.

## Further reading

- Python 3.12 tutorial, classes: <https://docs.python.org/3.12/tutorial/classes.html>
- Python 3.12 language reference: <https://docs.python.org/3.12/reference/>
- Type hints: <https://docs.python.org/3.12/library/typing.html>
