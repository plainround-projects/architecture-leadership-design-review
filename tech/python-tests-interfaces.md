# The tests (interfaces)

## What it is

The pytest tests in `tests/unit/interfaces`. Each function whose name starts with `test_` is one check; pytest finds and runs them. (Every term is explained where it first appears in the walkthrough below.)

## Why this repository uses it

The tests turn every rule, adapter and command of this repository into something that can fail. A rule without a test is only a claim.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `tests/unit/interfaces/test_cli.py` | 40 lines.  |

## How it works underneath

pytest imports each `test_*.py` file, builds the fixtures a test asks for by parameter name, runs the function, and counts it as passed when no `assert` fails and nothing raises. A fixture such as `tmp_path` or `monkeypatch` is prepared fresh for each test, so tests do not affect each other.

## Walkthrough of this repository's use

### `tests/unit/interfaces/test_cli.py`

`tests/unit/interfaces/test_cli.py` lines 1 to 7:

```python
import shutil
from pathlib import Path

import pytest

from design_review.interfaces.cli import main
from tests.conftest import REPOSITORY_ROOT
```

> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.

Imports:

- It imports module `shutil`.
- From `pathlib` it takes `Path`.
- It imports module `pytest`.
- From `design_review.interfaces.cli` it takes `main`.
- From `tests.conftest` it takes `REPOSITORY_ROOT`.

`tests/unit/interfaces/test_cli.py` lines 10 to 15:

```python
@pytest.fixture
def copy_of_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    shutil.copytree(REPOSITORY_ROOT / "docs", tmp_path / "docs")
    shutil.copytree(REPOSITORY_ROOT / "model", tmp_path / "model")
    monkeypatch.setenv("REVIEW_ROOT", str(tmp_path))
    return tmp_path
```

> **In plain words.** A **type hint** such as `x: int` or `-> str` says what kind of value a name holds or a function gives back. Python does not enforce hints when the program runs; the type checker mypy reads them before.
> **In plain words.** `return value` ends the function and gives the value back to whoever called it.
> **In plain words.** `tmp_path` is a built-in pytest fixture: a fresh, empty temporary folder (a `Path`) that is removed after the test.
> **In plain words.** `monkeypatch` is a built-in pytest fixture that changes something (an environment variable, an attribute) for this test only and undoes it afterwards.

**Function `copy_of_repo`.**

It takes: `tmp_path` (a `Path`); `monkeypatch` (a `pytest.MonkeyPatch`).

It gives back a `Path`.

Decorators: `@pytest.fixture`.

Step by step:

- Calls `shutil.copytree(REPOSITORY_ROOT / 'docs', tmp_path / 'docs')`.
- Calls `shutil.copytree(REPOSITORY_ROOT / 'model', tmp_path / 'model')`.
- Calls `monkeypatch.setenv('REVIEW_ROOT', str(tmp_path))`.
- Gives back `tmp_path`.

`tests/unit/interfaces/test_cli.py` lines 18 to 20:

```python
def test_check_passes(copy_of_repo, capsys):
    assert main(["check"]) == 0
    assert capsys.readouterr().out.splitlines()[-1] == "OK: 6 documents checked, 0 errors, 0 warnings"
```

> **In plain words.** `assert condition` checks that something is true. In a test, a false condition fails the test and pytest shows both sides of the comparison.
> **In plain words.** `==` tests equality, `is` tests that two names are the very same object (used for `None` and enum members), `in` tests membership.
> **In plain words.** `obj[key]` looks a value up by key or position.
> **In plain words.** A **test** is a function whose name starts with `test_`. pytest finds it, runs it, and reports a pass when no `assert` fails and nothing raises.
> **In plain words.** `capsys` is a built-in pytest fixture that captures what the program prints, so the test can read it with `capsys.readouterr()`.

**Test `test_check_passes`** checks: check passes.

It takes: `copy_of_repo`; `capsys`.

Step by step:

- Checks that `main(['check'])` equals `0`; if not, the test fails.
- Checks that `capsys.readouterr().out.splitlines()[-1]` equals `'OK: 6 documents checked, 0 errors, 0 warnings'`; if not, the test fails.

`tests/unit/interfaces/test_cli.py` lines 23 to 27:

```python
def test_check_fails_when_the_calculation_is_removed(copy_of_repo, capsys):
    review = copy_of_repo / "docs/reviews/review-2026-10-22-uploads-service.md"
    review.write_text(review.read_text().replace(" = ", " is "))
    assert main(["check"]) == 1
    assert "REV004" in capsys.readouterr().out
```

**Test `test_check_fails_when_the_calculation_is_removed`** checks: check fails when the calculation is removed.

It takes: `copy_of_repo`; `capsys`.

Step by step:

- Stores `copy_of_repo / 'docs/reviews/review-2026-10-22-uploads-service.md'` in `review`.
- Calls `review.write_text(review.read_text().replace(' = ', ' is '))`.
- Checks that `main(['check'])` equals `1`; if not, the test fails.
- Checks that `'REV004'` is in `capsys.readouterr().out`; if not, the test fails.

`tests/unit/interfaces/test_cli.py` lines 30 to 34:

```python
def test_fitness_prints_the_table(copy_of_repo, capsys):
    assert main(["fitness"]) == 0
    out = capsys.readouterr().out
    assert "ceiling" in out
    assert out.splitlines()[-1].startswith("OK:")
```

**Test `test_fitness_prints_the_table`** checks: fitness prints the table.

It takes: `copy_of_repo`; `capsys`.

Step by step:

- Checks that `main(['fitness'])` equals `0`; if not, the test fails.
- Stores `capsys.readouterr().out` in `out`.
- Checks that `'ceiling'` is in `out`; if not, the test fails.
- Checks that `out.splitlines()[-1].startswith('OK:')`; if not, the test fails.

`tests/unit/interfaces/test_cli.py` lines 37 to 41:

```python
def test_fitness_fails_when_a_scenario_surprises_the_review(copy_of_repo, capsys):
    model = copy_of_repo / "model/uploads.toml"
    model.write_text(model.read_text().replace("workers = 80", "workers = 9"))
    assert main(["fitness"]) == 1
    assert "UNEXPECTED" in capsys.readouterr().out
```

**Test `test_fitness_fails_when_a_scenario_surprises_the_review`** checks: fitness fails when a scenario surprises the review.

It takes: `copy_of_repo`; `capsys`.

Step by step:

- Stores `copy_of_repo / 'model/uploads.toml'` in `model`.
- Calls `model.write_text(model.read_text().replace('workers = 80', 'workers = 9'))`.
- Checks that `main(['fitness'])` equals `1`; if not, the test fails.
- Checks that `'UNEXPECTED'` is in `capsys.readouterr().out`; if not, the test fails.

`tests/unit/interfaces/test_cli.py` lines 44 to 46:

```python
def test_report_writes_markdown(copy_of_repo):
    assert main(["report"]) == 0
    assert "## Fitness functions" in (copy_of_repo / "build/report.md").read_text()
```

**Test `test_report_writes_markdown`** checks: report writes markdown.

It takes: `copy_of_repo`.

Step by step:

- Checks that `main(['report'])` equals `0`; if not, the test fails.
- Checks that `'## Fitness functions'` is in `(copy_of_repo / 'build/report.md').read_text()`; if not, the test fails.

`tests/unit/interfaces/test_cli.py` lines 49 to 52:

```python
def test_a_broken_model_exits_with_2(copy_of_repo, capsys):
    (copy_of_repo / "model/uploads.toml").write_text("[load]\n")
    assert main(["fitness"]) == 2
    assert "model error" in capsys.readouterr().err
```

**Test `test_a_broken_model_exits_with_2`** checks: a broken model exits with 2.

It takes: `copy_of_repo`; `capsys`.

Step by step:

- Calls `(copy_of_repo / 'model/uploads.toml').write_text('[load]\n')`.
- Checks that `main(['fitness'])` equals `2`; if not, the test fails.
- Checks that `'model error'` is in `capsys.readouterr().err`; if not, the test fails.

`tests/unit/interfaces/test_cli.py` lines 55 to 58:

```python
def test_a_bad_setting_exits_with_2(monkeypatch, capsys):
    monkeypatch.setenv("PROPOSAL_MAX_WORDS", "lots")
    assert main(["check"]) == 2
    assert "PROPOSAL_MAX_WORDS" in capsys.readouterr().err
```

**Test `test_a_bad_setting_exits_with_2`** checks: a bad setting exits with 2.

It takes: `monkeypatch`; `capsys`.

Step by step:

- Calls `monkeypatch.setenv('PROPOSAL_MAX_WORDS', 'lots')`.
- Checks that `main(['check'])` equals `2`; if not, the test fails.
- Checks that `'PROPOSAL_MAX_WORDS'` is in `capsys.readouterr().err`; if not, the test fails.

## Try it yourself

```bash
.venv/bin/pytest -q tests/unit/interfaces
```
Prints a row of dots, one per passing test, and a summary line such as `N passed in 0.5s` (skipped tests show as `s`).

```bash
.venv/bin/mypy
```
Checks the whole project (the `files` setting in `pyproject.toml`), these files included. Prints `Success: no issues found in 38 source files`.

```bash
.venv/bin/ruff check tests/unit/interfaces/test_cli.py
```
Prints `All checks passed!`.

## Mistakes people make

- Tests that depend on each other's order. Each test here builds its own data.
- Asserting only the happy path. These tests also break the input on purpose and check the exact rule that fails.
- Forgetting `test_` in a name, so the test never runs.

## Check yourself

1. What does the test `test_check_passes` check?
   **Answer:** it checks: check passes.
2. What does the test `test_check_fails_when_the_calculation_is_removed` check?
   **Answer:** it checks: check fails when the calculation is removed.
3. What does the test `test_fitness_prints_the_table` check?
   **Answer:** it checks: fitness prints the table.
4. What does the test `test_fitness_fails_when_a_scenario_surprises_the_review` check?
   **Answer:** it checks: fitness fails when a scenario surprises the review.
5. What does the test `test_report_writes_markdown` check?
   **Answer:** it checks: report writes markdown.

## Further reading

- pytest 9.1 documentation: <https://docs.pytest.org/en/stable/>
- How to use fixtures: <https://docs.pytest.org/en/stable/how-to/fixtures.html>
- `assert` rewriting: <https://docs.pytest.org/en/stable/how-to/assert.html>
