# The tests (application)

## What it is

The pytest tests in `tests/unit/application`. Each function whose name starts with `test_` is one check; pytest finds and runs them. (Every term is explained where it first appears in the walkthrough below.)

## Why this repository uses it

The tests turn every rule, adapter and command of this repository into something that can fail. A rule without a test is only a claim.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `tests/unit/application/test_check_documents.py` | 56 lines.  |

## How it works underneath

pytest imports each `test_*.py` file, builds the fixtures a test asks for by parameter name, runs the function, and counts it as passed when no `assert` fails and nothing raises. A fixture such as `tmp_path` or `monkeypatch` is prepared fresh for each test, so tests do not affect each other.

## Walkthrough of this repository's use

### `tests/unit/application/test_check_documents.py`

`tests/unit/application/test_check_documents.py` lines 1 to 7:

```python
import pytest

from design_review.application.check_documents import CheckSettings, check_documents, run_fitness_functions
from design_review.application.reporting import render_fitness, render_markdown, render_text
from design_review.infrastructure.markdown import MarkdownDocumentReader
from design_review.infrastructure.model_toml import TomlModelSource
from tests.conftest import MemoryStore, repository_files
```

> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.

Imports:

- It imports module `pytest`.
- From `design_review.application.check_documents` it takes `CheckSettings, check_documents, run_fitness_functions`.
- From `design_review.application.reporting` it takes `render_fitness, render_markdown, render_text`.
- From `design_review.infrastructure.markdown` it takes `MarkdownDocumentReader`.
- From `design_review.infrastructure.model_toml` it takes `TomlModelSource`.
- From `tests.conftest` it takes `MemoryStore, repository_files`.

`tests/unit/application/test_check_documents.py` lines 10 to 12:

```python
def run(files):
    store = MemoryStore(files)
    return check_documents(store, MarkdownDocumentReader(store), CheckSettings())
```

> **In plain words.** `return value` ends the function and gives the value back to whoever called it.

**Function `run`.**

It takes: `files`.

Step by step:

- Stores the result of calling `MemoryStore(files)` in `store`.
- Gives back the result of calling `check_documents(store, MarkdownDocumentReader(store), CheckSettings())`.

`tests/unit/application/test_check_documents.py` lines 15 to 19:

```python
def test_the_repository_documents_pass():
    report = run(repository_files())
    assert report.ok
    assert report.findings == ()
    assert len(report.subjects) == 6
```

> **In plain words.** `assert condition` checks that something is true. In a test, a false condition fails the test and pytest shows both sides of the comparison.
> **In plain words.** `==` tests equality, `is` tests that two names are the very same object (used for `None` and enum members), `in` tests membership.
> **In plain words.** A **tuple** `(a, b)` is a fixed list of values that cannot be changed.
> **In plain words.** A **test** is a function whose name starts with `test_`. pytest finds it, runs it, and reports a pass when no `assert` fails and nothing raises.

**Test `test_the_repository_documents_pass`** checks: the repository documents pass.

Step by step:

- Stores the result of calling `run(repository_files())` in `report`.
- Checks that `report.ok`; if not, the test fails.
- Checks that `report.findings` equals `()`; if not, the test fails.
- Checks that `len(report.subjects)` equals `6`; if not, the test fails.

`tests/unit/application/test_check_documents.py` lines 22 to 26:

```python
def test_a_review_pointing_at_an_unknown_requirements_file_is_reported():
    files = repository_files()
    path = "docs/reviews/review-2026-10-22-uploads-service.md"
    files[path] = files[path].replace("docs/requirements/uploads-nfrs.md", "docs/requirements/missing.md")
    assert {f.code for f in run(files).findings} == {"REV002"}
```

> **In plain words.** `obj[key]` looks a value up by key or position.
> **In plain words.** A **set comprehension** `{x for ...}` builds a set (a collection with no duplicates) with a loop.
> **In plain words.** A **set** `{a, b}` holds items without duplicates; `frozenset` is a set that cannot be changed.

**Test `test_a_review_pointing_at_an_unknown_requirements_file_is_reported`** checks: a review pointing at an unknown requirements file is reported.

Step by step:

- Stores the result of calling `repository_files()` in `files`.
- Stores the text `'docs/reviews/review-2026-10-22-uploads-service.md'` in `path`.
- Stores the result of calling `files[path].replace('docs/requirements/uploads-nfrs.md', 'docs/requirements/missing.md')` in `files[path]`.
- Checks that `{f.code for f in run(files).findings}` equals `{'REV002'}`; if not, the test fails.

`tests/unit/application/test_check_documents.py` lines 29 to 32:

```python
def test_a_missing_checklist_is_reported():
    files = repository_files()
    del files["docs/checklists/design-checklist.md"]
    assert {f.code for f in run(files).findings} == {"DOC001"}
```

**Test `test_a_missing_checklist_is_reported`** checks: a missing checklist is reported.

Step by step:

- Stores the result of calling `repository_files()` in `files`.
- Removes `files['docs/checklists/design-checklist.md']`.
- Checks that `{f.code for f in run(files).findings}` equals `{'DOC001'}`; if not, the test fails.

`tests/unit/application/test_check_documents.py` lines 35 to 38:

```python
def test_the_template_is_not_mistaken_for_a_review():
    files = repository_files()
    files["docs/reviews/comparison.md"] = "not a review"
    assert run(files).ok
```

**Test `test_the_template_is_not_mistaken_for_a_review`** checks: the template is not mistaken for a review.

Step by step:

- Stores the result of calling `repository_files()` in `files`.
- Stores the text `'not a review'` in `files['docs/reviews/comparison.md']`.
- Checks that `run(files).ok`; if not, the test fails.

`tests/unit/application/test_check_documents.py` lines 41 to 44:

```python
@pytest.fixture(scope="module")
def fitness():
    store = MemoryStore(repository_files())
    return run_fitness_functions(TomlModelSource(store), horizon_seconds=43_200)
```

> **In plain words.** A **fixture** is a helper function marked `@pytest.fixture`. A test that names it as a parameter receives its return value, prepared fresh for that test.
> **In plain words.** A call such as `f(a, key=value)` passes `a` by position and `key` by name (a **keyword argument**).

**Function `fitness`.**

Decorators: `@pytest.fixture(scope='module')`.

Step by step:

- Stores the result of calling `MemoryStore(repository_files())` in `store`.
- Gives back the result of calling `run_fitness_functions(TomlModelSource(store), horizon_seconds=43200)`.

`tests/unit/application/test_check_documents.py` lines 47 to 50:

```python
def test_the_models_scenarios_give_the_recorded_verdicts(fitness):
    assert fitness.ok
    assert [r.passed for r in fitness.thumbnails] == [False, False, True]
    assert [v.result.holds for v in fitness.durability] == [False, True, True]
```

> **In plain words.** A **list comprehension** `[x for x in items if test]` is a loop written inside brackets: it builds a new list from the items that pass the test.

**Test `test_the_models_scenarios_give_the_recorded_verdicts`** checks: the models scenarios give the recorded verdicts.

It takes: `fitness`.

Step by step:

- Checks that `fitness.ok`; if not, the test fails.
- Checks that `[r.passed for r in fitness.thumbnails]` equals `[False, False, True]`; if not, the test fails.
- Checks that `[v.result.holds for v in fitness.durability]` equals `[False, True, True]`; if not, the test fails.

`tests/unit/application/test_check_documents.py` lines 53 to 64:

```python
def test_reports_render_text_and_markdown(fitness):
    text = render_fitness(fitness)
    assert "peak needs 80 workers" in text
    assert "lost: crash after put_object, respond" in text
    assert "orphan:" in text
    assert text.splitlines()[-1].startswith("OK:")
    report = run(repository_files())
    assert render_text(report).splitlines()[-1] == "OK: 6 documents checked, 0 errors, 0 warnings"
    markdown = render_markdown(report, fitness)
    assert "**Verdict:** OK" in markdown
    assert "None." in markdown
    assert "## Fitness functions" in markdown
```

**Test `test_reports_render_text_and_markdown`** checks: reports render text and markdown.

It takes: `fitness`.

Step by step:

- Stores the result of calling `render_fitness(fitness)` in `text`.
- Checks that `'peak needs 80 workers'` is in `text`; if not, the test fails.
- Checks that `'lost: crash after put_object, respond'` is in `text`; if not, the test fails.
- Checks that `'orphan:'` is in `text`; if not, the test fails.
- Checks that `text.splitlines()[-1].startswith('OK:')`; if not, the test fails.
- Stores the result of calling `run(repository_files())` in `report`.
- Checks that `render_text(report).splitlines()[-1]` equals `'OK: 6 documents checked, 0 errors, 0 warnings'`; if not, the test fails.
- Stores the result of calling `render_markdown(report, fitness)` in `markdown`.
- Checks that `'**Verdict:** OK'` is in `markdown`; if not, the test fails.
- Checks that `'None.'` is in `markdown`; if not, the test fails.
- Checks that `'## Fitness functions'` is in `markdown`; if not, the test fails.

`tests/unit/application/test_check_documents.py` lines 67 to 75:

```python
def test_failing_reports_say_so():
    files = repository_files()
    del files["docs/checklists/design-checklist.md"]
    report = run(files)
    assert render_text(report).splitlines()[0].startswith("ERROR")
    assert "FAILED" in render_text(report)
    assert "| error | DOC001 |" in render_markdown(
        report, run_fitness_functions(TomlModelSource(MemoryStore(repository_files())), horizon_seconds=7200)
    )
```

**Test `test_failing_reports_say_so`** checks: failing reports say so.

Step by step:

- Stores the result of calling `repository_files()` in `files`.
- Removes `files['docs/checklists/design-checklist.md']`.
- Stores the result of calling `run(files)` in `report`.
- Checks that `render_text(report).splitlines()[0].startswith('ERROR')`; if not, the test fails.
- Checks that `'FAILED'` is in `render_text(report)`; if not, the test fails.
- Checks that `'| error | DOC001 |'` is in `render_markdown(report, run_fitness_functions(Tom…`; if not, the test fails.

## Try it yourself

```bash
.venv/bin/pytest -q tests/unit/application
```
Prints a row of dots, one per passing test, and a summary line such as `N passed in 0.5s` (skipped tests show as `s`).

```bash
.venv/bin/mypy
```
Checks the whole project (the `files` setting in `pyproject.toml`), these files included. Prints `Success: no issues found in 38 source files`.

```bash
.venv/bin/ruff check tests/unit/application/test_check_documents.py
```
Prints `All checks passed!`.

## Mistakes people make

- Tests that depend on each other's order. Each test here builds its own data.
- Asserting only the happy path. These tests also break the input on purpose and check the exact rule that fails.
- Forgetting `test_` in a name, so the test never runs.

## Check yourself

1. What does the test `test_the_repository_documents_pass` check?
   **Answer:** it checks: the repository documents pass.
2. What does the test `test_a_review_pointing_at_an_unknown_requirements_file_is_reported` check?
   **Answer:** it checks: a review pointing at an unknown requirements file is reported.
3. What does the test `test_a_missing_checklist_is_reported` check?
   **Answer:** it checks: a missing checklist is reported.
4. What does the test `test_the_template_is_not_mistaken_for_a_review` check?
   **Answer:** it checks: the template is not mistaken for a review.
5. What does the test `test_the_models_scenarios_give_the_recorded_verdicts` check?
   **Answer:** it checks: the models scenarios give the recorded verdicts.

## Further reading

- pytest 9.1 documentation: <https://docs.pytest.org/en/stable/>
- How to use fixtures: <https://docs.pytest.org/en/stable/how-to/fixtures.html>
- `assert` rewriting: <https://docs.pytest.org/en/stable/how-to/assert.html>
