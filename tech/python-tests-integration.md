# The tests (integration)

## What it is

The pytest tests in `tests/integration`. Each function whose name starts with `test_` is one check; pytest finds and runs them. (Every term is explained where it first appears in the walkthrough below.)

## Why this repository uses it

The tests turn every rule, adapter and command of this repository into something that can fail. A rule without a test is only a claim.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `tests/integration/test_done_when.py` | 94 lines. One test per 'Done when' line of the lesson, run over copies of the repository's own documents. |

## How it works underneath

pytest imports each `test_*.py` file, builds the fixtures a test asks for by parameter name, runs the function, and counts it as passed when no `assert` fails and nothing raises. A fixture such as `tmp_path` or `monkeypatch` is prepared fresh for each test, so tests do not affect each other.

## Walkthrough of this repository's use

### `tests/integration/test_done_when.py`

`tests/integration/test_done_when.py` lines 1 to 13:

```python
"""One test per 'Done when' line of the lesson, run over copies of the repository's own documents."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from design_review.application.check_documents import CheckSettings, check_documents
from design_review.infrastructure.filesystem import FileSystemStore
from design_review.infrastructure.markdown import MarkdownDocumentReader
from tests.conftest import REPOSITORY_ROOT
```

> **In plain words.** A **docstring** is a text in triple quotes as the first thing in a module, class or function. Python keeps it as the thing's description, and ruff requires one on public code.
> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.
> **In plain words.** `from __future__ import annotations` makes every type hint in the file lazy text. Python no longer evaluates a hint when the file loads, so a hint may name a class defined further down.

**Module description.** One test per 'Done when' line of the lesson, run over copies of the repository's own documents.

Imports:

- From `__future__` it takes `annotations`.
- It imports module `shutil`.
- From `pathlib` it takes `Path`.
- It imports module `pytest`.
- From `design_review.application.check_documents` it takes `CheckSettings, check_documents`.
- From `design_review.infrastructure.filesystem` it takes `FileSystemStore`.
- From `design_review.infrastructure.markdown` it takes `MarkdownDocumentReader`.
- From `tests.conftest` it takes `REPOSITORY_ROOT`.

`tests/integration/test_done_when.py` lines 15 to 17:

```python
PROPOSAL = "docs/proposals/uploads-service-draft-1.md"
REQUIREMENTS = "docs/requirements/uploads-nfrs.md"
REVIEW = "docs/reviews/review-2026-10-22-uploads-service.md"
```

> **In plain words.** A name written in CAPITAL letters is a **constant** by convention: a value set once, not changed later.

These module-level lines:

- Stores the text `'docs/proposals/uploads-service-draft-1.md'` in `PROPOSAL`.
- Stores the text `'docs/requirements/uploads-nfrs.md'` in `REQUIREMENTS`.
- Stores the text `'docs/reviews/review-2026-10-22-uploads-service.md'` in `REVIEW`.

`tests/integration/test_done_when.py` lines 20 to 24:

```python
@pytest.fixture
def repo(tmp_path: Path) -> Path:
    shutil.copytree(REPOSITORY_ROOT / "docs", tmp_path / "docs")
    shutil.copytree(REPOSITORY_ROOT / "model", tmp_path / "model")
    return tmp_path
```

> **In plain words.** A **type hint** such as `x: int` or `-> str` says what kind of value a name holds or a function gives back. Python does not enforce hints when the program runs; the type checker mypy reads them before.
> **In plain words.** `return value` ends the function and gives the value back to whoever called it.
> **In plain words.** `tmp_path` is a built-in pytest fixture: a fresh, empty temporary folder (a `Path`) that is removed after the test.

**Function `repo`.**

It takes: `tmp_path` (a `Path`).

It gives back a `Path`.

Decorators: `@pytest.fixture`.

Step by step:

- Calls `shutil.copytree(REPOSITORY_ROOT / 'docs', tmp_path / 'docs')`.
- Calls `shutil.copytree(REPOSITORY_ROOT / 'model', tmp_path / 'model')`.
- Gives back `tmp_path`.

`tests/integration/test_done_when.py` lines 27 to 29:

```python
def codes(root: Path) -> set[str]:
    store = FileSystemStore(root)
    return {f.code for f in check_documents(store, MarkdownDocumentReader(store), CheckSettings()).errors}
```

> **In plain words.** `obj[key]` looks a value up by key or position.
> **In plain words.** A **set comprehension** `{x for ...}` builds a set (a collection with no duplicates) with a loop.

**Function `codes`.**

It takes: `root` (a `Path`).

It gives back a `set[str]`.

Step by step:

- Stores the result of calling `FileSystemStore(root)` in `store`.
- Gives back a new set made by a loop (`{f.code for f in check_documents(store, MarkdownDocumentReader(store)…`).

`tests/integration/test_done_when.py` lines 32 to 35:

```python
def edit(root: Path, path: str, old: str, new: str) -> None:
    text = (root / path).read_text()
    assert old in text, f"{old!r} not in {path}"
    (root / path).write_text(text.replace(old, new))
```

> **In plain words.** `assert condition` checks that something is true. In a test, a false condition fails the test and pytest shows both sides of the comparison.
> **In plain words.** `==` tests equality, `is` tests that two names are the very same object (used for `None` and enum members), `in` tests membership.
> **In plain words.** An **f-string** `f"...{value}..."` is text with Python expressions in braces; Python replaces each by its value. `{x!r}` shows the value the way Python would write it, with quotes.

**Function `edit`.**

It takes: `root` (a `Path`); `path` (a `str`); `old` (a `str`); `new` (a `str`).

It gives back a `None`.

Step by step:

- Stores the result of calling `(root / path).read_text()` in `text`.
- Checks that `old` is in `text` with the message `f'{old!r} not in {path}'`; if not, the test fails.
- Calls `(root / path).write_text(text.replace(old, new))`.

`tests/integration/test_done_when.py` lines 38 to 39:

```python
def test_the_repository_as_committed_passes(repo: Path) -> None:
    assert codes(repo) == set()
```

> **In plain words.** A **test** is a function whose name starts with `test_`. pytest finds it, runs it, and reports a pass when no `assert` fails and nothing raises.

**Test `test_the_repository_as_committed_passes`** checks: the repository as committed passes.

It takes: `repo` (a `Path`).

It gives back a `None`.

Step by step:

- Checks that `codes(repo)` equals `set()`; if not, the test fails.

`tests/integration/test_done_when.py` lines 42 to 53:

```python
def test_done_when_1_the_proposal_names_its_datastore_external_calls_and_scaling(repo: Path) -> None:
    proposal = MarkdownDocumentReader(FileSystemStore(repo)).read_proposal(PROPOSAL)
    assert "PostgreSQL" in proposal.sections["Datastore"]
    assert "object storage" in proposal.sections["External calls"]
    assert "2 instances" in proposal.sections["Scaling"]
    edit(
        repo,
        PROPOSAL,
        "## Scaling\nThe service runs as 2 instances behind a load balancer. The thumbnail job runs with 1 worker.",
        "## Scaling\n",
    )
    assert "PRP001" in codes(repo)
```

**Test `test_done_when_1_the_proposal_names_its_datastore_external_calls_and_scaling`** checks: done when 1 the proposal names its datastore external calls and scaling.

It takes: `repo` (a `Path`).

It gives back a `None`.

Step by step:

- Stores the result of calling `MarkdownDocumentReader(FileSystemStore(repo)).read_proposal(PROPOSAL)` in `proposal`.
- Checks that `'PostgreSQL'` is in `proposal.sections['Datastore']`; if not, the test fails.
- Checks that `'object storage'` is in `proposal.sections['External calls']`; if not, the test fails.
- Checks that `'2 instances'` is in `proposal.sections['Scaling']`; if not, the test fails.
- Calls `edit(repo, PROPOSAL, '## Scaling\nThe service runs as 2 instances behind a load balancer. The thumbnail job r…`.
- Checks that `'PRP001'` is in `codes(repo)`; if not, the test fails.

`tests/integration/test_done_when.py` lines 56 to 66:

```python
def test_done_when_2_each_requirement_is_a_number_with_a_way_to_verify_it(repo: Path) -> None:
    requirements = MarkdownDocumentReader(FileSystemStore(repo)).read_requirements(REQUIREMENTS).requirements
    assert len(requirements) == 6
    assert all(any(ch.isdigit() for ch in r.target) and r.verification for r in requirements)
    edit(
        repo,
        REQUIREMENTS,
        "| 95 percent within 30 seconds of upload | queue age metric |",
        "| fast | queue age metric |",
    )
    assert "REQ001" in codes(repo)
```

> **In plain words.** A **generator expression** `(x for x in items)` is like a list comprehension, but it hands out one value at a time instead of building the whole list; here it is passed straight to a function such as `tuple(...)` or `sum(...)`.

**Test `test_done_when_2_each_requirement_is_a_number_with_a_way_to_verify_it`** checks: done when 2 each requirement is a number with a way to verify it.

It takes: `repo` (a `Path`).

It gives back a `None`.

Step by step:

- Stores `MarkdownDocumentReader(FileSystemStore(repo)).read_requirements(REQUIREMENTS).r…` in `requirements`.
- Checks that `len(requirements)` equals `6`; if not, the test fails.
- Checks that `all((any((ch.isdigit() for ch in r.target)) and r.verification for r …`; if not, the test fails.
- Calls `edit(repo, REQUIREMENTS, '| 95 percent within 30 seconds of upload | queue age metric |', '| fast | queue age…`.
- Checks that `'REQ001'` is in `codes(repo)`; if not, the test fails.

`tests/integration/test_done_when.py` lines 69 to 71:

```python
def test_done_when_2_a_requirement_with_no_check_is_rejected(repo: Path) -> None:
    edit(repo, REQUIREMENTS, "| 2,000 dollars a month | cloud bill |", "| 2,000 dollars a month | TBD |")
    assert "REQ002" in codes(repo)
```

**Test `test_done_when_2_a_requirement_with_no_check_is_rejected`** checks: done when 2 a requirement with no check is rejected.

It takes: `repo` (a `Path`).

It gives back a `None`.

Step by step:

- Calls `edit(repo, REQUIREMENTS, '| 2,000 dollars a month | cloud bill |', '| 2,000 dollars a month | TBD |')`.
- Checks that `'REQ002'` is in `codes(repo)`; if not, the test fails.

`tests/integration/test_done_when.py` lines 74 to 84:

```python
def test_done_when_3_every_concern_points_to_a_requirement(repo: Path) -> None:
    review = MarkdownDocumentReader(FileSystemStore(repo)).read_review(REVIEW)
    cited = {used.id for used in review.used}
    assert all(f.requirement in cited for f in review.findings if f.cls != "taste")
    edit(
        repo,
        REVIEW,
        "| 7 | No latency budget for a 5 MB photo | R2 | should-fix |",
        "| 7 | No latency budget for a 5 MB photo | none | should-fix |",
    )
    assert "REV005" in codes(repo)
```

**Test `test_done_when_3_every_concern_points_to_a_requirement`** checks: done when 3 every concern points to a requirement.

It takes: `repo` (a `Path`).

It gives back a `None`.

Step by step:

- Stores the result of calling `MarkdownDocumentReader(FileSystemStore(repo)).read_review(REVIEW)` in `review`.
- Stores a new set made by a loop (`{used.id for used in review.used}`) in `cited`.
- Checks that `all((f.requirement in cited for f in review.findings if f.cls != 'tas…`; if not, the test fails.
- Calls `edit(repo, REVIEW, '| 7 | No latency budget for a 5 MB photo | R2 | should-fix |', '| 7 | No latency budget f…`.
- Checks that `'REV005'` is in `codes(repo)`; if not, the test fails.

`tests/integration/test_done_when.py` lines 87 to 100:

```python
def test_done_when_4_must_fix_is_short_and_a_preference_was_dropped(repo: Path) -> None:
    review = MarkdownDocumentReader(FileSystemStore(repo)).read_review(REVIEW)
    must = [f for f in review.findings if f.cls == "must-fix"]
    taste = [f for f in review.findings if f.cls == "taste"]
    assert len(must) == 2
    assert len(taste) == 2
    assert all("dropped" in f.note for f in taste)
    edit(
        repo,
        REVIEW,
        "| 5 | A preference for another CDN | none | taste, dropped |",
        "| 5 | A preference for another CDN | none | taste |",
    )
    assert "REV006" in codes(repo)
```

> **In plain words.** A **list comprehension** `[x for x in items if test]` is a loop written inside brackets: it builds a new list from the items that pass the test.

**Test `test_done_when_4_must_fix_is_short_and_a_preference_was_dropped`** checks: done when 4 must fix is short and a preference was dropped.

It takes: `repo` (a `Path`).

It gives back a `None`.

Step by step:

- Stores the result of calling `MarkdownDocumentReader(FileSystemStore(repo)).read_review(REVIEW)` in `review`.
- Stores a new list made by a loop (`[f for f in review.findings if f.cls == 'must-fix']`) in `must`.
- Stores a new list made by a loop (`[f for f in review.findings if f.cls == 'taste']`) in `taste`.
- Checks that `len(must)` equals `2`; if not, the test fails.
- Checks that `len(taste)` equals `2`; if not, the test fails.
- Checks that `all(('dropped' in f.note for f in taste))`; if not, the test fails.
- Calls `edit(repo, REVIEW, '| 5 | A preference for another CDN | none | taste, dropped |', '| 5 | A preference for an…`.
- Checks that `'REV006'` is in `codes(repo)`; if not, the test fails.

`tests/integration/test_done_when.py` lines 103 to 109:

```python
def test_done_when_5_someone_not_in_the_room_can_tell_what_was_decided_and_what_is_open(repo: Path) -> None:
    review = MarkdownDocumentReader(FileSystemStore(repo)).read_review(REVIEW)
    assert review.decisions
    assert all(risk.owner and risk.look_again for risk in review.risks)
    assert all(action.owner and action.due for action in review.actions)
    edit(repo, REVIEW, "| Uploads team lead | 2026-10-29 |", "| the team | 2026-10-29 |")
    assert "REV011" in codes(repo)
```

**Test `test_done_when_5_someone_not_in_the_room_can_tell_what_was_decided_and_what_is_open`** checks: done when 5 someone not in the room can tell what was decided and what is open.

It takes: `repo` (a `Path`).

It gives back a `None`.

Step by step:

- Stores the result of calling `MarkdownDocumentReader(FileSystemStore(repo)).read_review(REVIEW)` in `review`.
- Checks that `review.decisions`; if not, the test fails.
- Checks that `all((risk.owner and risk.look_again for risk in review.risks))`; if not, the test fails.
- Checks that `all((action.owner and action.due for action in review.actions))`; if not, the test fails.
- Calls `edit(repo, REVIEW, '| Uploads team lead | 2026-10-29 |', '| the team | 2026-10-29 |')`.
- Checks that `'REV011'` is in `codes(repo)`; if not, the test fails.

`tests/integration/test_done_when.py` lines 112 to 118:

```python
def test_done_when_6_the_record_shows_the_author_changing_the_reviewers_position(repo: Path) -> None:
    review = MarkdownDocumentReader(FileSystemStore(repo)).read_review(REVIEW)
    contested = next(f for f in review.findings if f.number == review.disagreements[0].finding)
    assert contested.cls == "withdrawn"
    assert review.disagreements[0].outcome.startswith("accepted")
    edit(repo, REVIEW, "Outcome: accepted.", "Outcome: rejected.")
    assert "REV012" in codes(repo)
```

**Test `test_done_when_6_the_record_shows_the_author_changing_the_reviewers_position`** checks: done when 6 the record shows the author changing the reviewers position.

It takes: `repo` (a `Path`).

It gives back a `None`.

Step by step:

- Stores the result of calling `MarkdownDocumentReader(FileSystemStore(repo)).read_review(REVIEW)` in `review`.
- Stores the result of calling `next((f for f in review.findings if f.number == review.disagreements[0].finding))` in `contested`.
- Checks that `contested.cls` equals `'withdrawn'`; if not, the test fails.
- Checks that `review.disagreements[0].outcome.startswith('accepted')`; if not, the test fails.
- Calls `edit(repo, REVIEW, 'Outcome: accepted.', 'Outcome: rejected.')`.
- Checks that `'REV012'` is in `codes(repo)`; if not, the test fails.

`tests/integration/test_done_when.py` lines 121 to 123:

```python
def test_the_stretch_checklist_covers_every_category_the_reviews_found_fault_in(repo: Path) -> None:
    edit(repo, "docs/checklists/design-checklist.md", "- [ ] CHK-06 [durability]", "- [ ] CHK-06 [cost]")
    assert "CHK002" in codes(repo)
```

**Test `test_the_stretch_checklist_covers_every_category_the_reviews_found_fault_in`** checks: the stretch checklist covers every category the reviews found fault in.

It takes: `repo` (a `Path`).

It gives back a `None`.

Step by step:

- Calls `edit(repo, 'docs/checklists/design-checklist.md', '- [ ] CHK-06 [durability]', '- [ ] CHK-06 [cost]')`.
- Checks that `'CHK002'` is in `codes(repo)`; if not, the test fails.

## Try it yourself

```bash
.venv/bin/pytest -q tests/integration
```
Prints a row of dots, one per passing test, and a summary line such as `N passed in 0.5s` (skipped tests show as `s`).

```bash
.venv/bin/mypy
```
Checks the whole project (the `files` setting in `pyproject.toml`), these files included. Prints `Success: no issues found in 38 source files`.

```bash
.venv/bin/ruff check tests/integration/test_done_when.py
```
Prints `All checks passed!`.

## Mistakes people make

- Tests that depend on each other's order. Each test here builds its own data.
- Asserting only the happy path. These tests also break the input on purpose and check the exact rule that fails.
- Forgetting `test_` in a name, so the test never runs.

## Check yourself

1. What does the test `test_the_repository_as_committed_passes` check?
   **Answer:** it checks: the repository as committed passes.
2. What does the test `test_done_when_1_the_proposal_names_its_datastore_external_calls_and_scaling` check?
   **Answer:** it checks: done when 1 the proposal names its datastore external calls and scaling.
3. What does the test `test_done_when_2_each_requirement_is_a_number_with_a_way_to_verify_it` check?
   **Answer:** it checks: done when 2 each requirement is a number with a way to verify it.
4. What does the test `test_done_when_2_a_requirement_with_no_check_is_rejected` check?
   **Answer:** it checks: done when 2 a requirement with no check is rejected.
5. What does the test `test_done_when_3_every_concern_points_to_a_requirement` check?
   **Answer:** it checks: done when 3 every concern points to a requirement.

## Further reading

- pytest 9.1 documentation: <https://docs.pytest.org/en/stable/>
- How to use fixtures: <https://docs.pytest.org/en/stable/how-to/fixtures.html>
- `assert` rewriting: <https://docs.pytest.org/en/stable/how-to/assert.html>
