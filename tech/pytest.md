# pytest

## What it is

A **test** is a small function that runs part of the program and states what must be true afterwards, with the
word `assert`. **pytest** is a tool that finds the test functions in a folder, runs them, and reports which passed
and which failed. A **fixture** is a helper function that prepares something a test needs (a temporary folder, a
sample object) and is handed to the test by name.

## Why this repository uses it

The lesson's "Done when" lines are only claims until something checks them. The tests check them: the integration
test file has one test per line. The unit tests cover every rule in `domain/`, so changing a rule breaks a test.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `tests/unit/**` | Unit tests per layer: `domain`, `application`, `infrastructure`, `interfaces`. |
| `tests/integration/test_done_when.py` | One test per "Done when" line, run over a copy of the repository's documents. |
| `tests/conftest.py` | Shared helpers and the `repository_root` fixture. |
| `pyproject.toml` `[tool.pytest.ini_options]` | Where to look and which options to always use. |
| `Makefile` `test` | Runs pytest under coverage. |

## How it works underneath

1. pytest starts, reads `pyproject.toml`, and walks the folders in `testpaths`.
2. It imports each file named `test_*.py`. Each function whose name starts with `test_` is one test.
3. For each test it looks at the function's parameter names. A parameter named `tmp_path` or `capsys` is a built-in
   fixture; a name defined with `@pytest.fixture` in the file or in `conftest.py` is a custom one. pytest builds
   those values and passes them in.
4. It runs the function. If every `assert` holds and nothing is raised, the test passes. pytest rewrites `assert`
   lines when it imports a test file, so a failure shows both sides of the comparison.
5. After the run it prints one dot per passing test, then a summary line.

## Walkthrough of this repository's use

`pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers"
```

- `testpaths = ["tests"]`: when run with no arguments, look only in `tests/`.
- `addopts = "-ra --strict-markers"`: options added to every run. `-ra` prints a short reason line for every
  test that is not a plain pass (skipped, failed, error). `--strict-markers` turns an unknown `@pytest.mark.xyz`
  into an error instead of a silent typo.

`tests/conftest.py`:

```python
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
```

`__file__` is the path of this file. `.resolve()` makes it absolute. `.parents[1]` is two levels up (the folder
holding `tests/`), which is the repository root. Tests use it to find the real `docs/` folder.

`tests/conftest.py`:

```python
class MemoryStore:
    """A DocumentStore held in a dict, for tests that need no disk."""

    def __init__(self, files: dict[str, str] | None = None) -> None:
        self.files = dict(files or {})
```

A hand-written **test double**: a small in-memory stand-in for the real file store, so most tests touch no disk.

`tests/unit/domain/test_capacity_and_queue.py`:

```python
def test_the_lessons_load_numbers():
    assert LOAD.photos_per_week == 1_200_000
    assert LOAD.weekend_seconds == 216_000
    assert LOAD.average_rate == pytest.approx(3.889, abs=0.001)
    assert LOAD.peak_ratio == pytest.approx(10.29, abs=0.01)
```

The simplest kind of test: call a function, compare the result with the expected value using `assert`.

`tests/unit/interfaces/test_cli.py`:

```python
@pytest.fixture
def copy_of_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    shutil.copytree(REPOSITORY_ROOT / "docs", tmp_path / "docs")
    shutil.copytree(REPOSITORY_ROOT / "model", tmp_path / "model")
    monkeypatch.setenv("REVIEW_ROOT", str(tmp_path))
    return tmp_path
```

`@pytest.fixture` marks a function as a fixture: a test that has a parameter named `copy_of_repo` receives its return
value. This one copies the real `docs/` into a temporary folder and points the program at it with environment
variables. `tmp_path` is a fresh empty folder per test, deleted afterwards. `monkeypatch.setenv` changes an
environment variable for this test only and undoes it at the end. The type hints (`Path`, `pytest.MonkeyPatch`)
are optional for pytest, but help the reader.

`tests/unit/interfaces/test_cli.py`:

```python
def test_check_fails_when_the_calculation_is_removed(copy_of_repo, capsys):
    review = copy_of_repo / "docs/reviews/review-2026-10-22-uploads-service.md"
    review.write_text(review.read_text().replace(" = ", " is "))
    assert main(["check"]) == 1
    assert "REV004" in capsys.readouterr().out
```

This test damages one copied document, runs the real command, and checks the exit code (`== 1`) and the output
with `capsys`, the fixture that captures what the program prints. The tests prove each rule fails when the document
is damaged, not only that the good document passes.

`tests/unit/infrastructure/test_readers.py`:

```python
@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("not toml [", "not valid TOML"),
        (GOOD.replace("[burst]", "[burst_x]"), r"no \[burst\]"),
        (GOOD.replace("photos_per_listing = 10", ""), "missing"),
        (GOOD.replace('expect = "fail"', 'expect = "maybe"', 1), "expect must be"),
        (GOOD.replace("weekend_share = 0.70", "weekend_share = 7"), "weekend_share"),
    ],
)
def test_a_bad_model_file_is_rejected_with_a_reason(text, message):
    with pytest.raises(ModelError, match=message):
        TomlModelSource(MemoryStore({"m.toml": text})).load("m.toml")
```

`@pytest.mark.parametrize` runs the same test body once per row of data. A failure names the row that broke.

## Try it yourself

```bash
.venv/bin/pytest -q
```
Prints rows of dots and `95 passed in` some seconds.

```bash
.venv/bin/pytest --collect-only -q tests/unit/domain/test_capacity_and_queue.py
```
Lists the test names without running them, one `path::test_name` per line.

```bash
.venv/bin/pytest -q -k done_when
```
Runs only tests whose name contains `done_when`: the integration tests, one per lesson line.

```bash
.venv/bin/pytest -q tests/unit/domain/test_capacity_and_queue.py -x -vv
```
`-x` stops at the first failure; `-vv` shows each test name and result.

```bash
.venv/bin/pytest --fixtures -q | grep -E "tmp_path|capsys|monkeypatch" | head
```
Shows the built-in fixtures this repository uses.

## Mistakes people make

- **Tests that depend on each other's order.** Each test here builds its own data (a fresh `tmp_path`).
- **Asserting only the happy path.** The tests here also break a document on purpose and check the rule code.
- **Forgetting `test_` in a name**, so the test never runs. Check the count in the summary.
- **Editing the real `docs/` from a test.** The CLI tests copy `docs/` to a temporary folder first.

## Check yourself

1. How does pytest know which functions are tests?
   **Answer:** Files named `test_*.py`, functions named `test_*`.
2. What does `tmp_path` give a test?
   **Answer:** A fresh, empty temporary folder that is removed afterwards.
3. What does `-ra` print?
   **Answer:** A short summary line for every test that is not a plain pass.
4. Why does the CLI test copy `docs/` first?
   **Answer:** So the test can damage a document without changing the real repository.
5. What does `parametrize` do?
   **Answer:** It runs one test function several times with different data.

## Further reading

- pytest 9.1 documentation: <https://docs.pytest.org/en/stable/>
- How to use fixtures: <https://docs.pytest.org/en/stable/how-to/fixtures.html>
- Configuration (`pyproject.toml`): <https://docs.pytest.org/en/stable/reference/customize.html>
