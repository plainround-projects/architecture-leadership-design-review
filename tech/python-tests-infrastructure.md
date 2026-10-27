# The tests (infrastructure)

## What it is

The pytest tests in `tests/unit/infrastructure`. Each function whose name starts with `test_` is one check; pytest finds and runs them. (Every term is explained where it first appears in the walkthrough below.)

## Why this repository uses it

The tests turn every rule, adapter and command of this repository into something that can fail. A rule without a test is only a claim.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `tests/unit/infrastructure/test_readers.py` | 89 lines.  |

## How it works underneath

pytest imports each `test_*.py` file, builds the fixtures a test asks for by parameter name, runs the function, and counts it as passed when no `assert` fails and nothing raises. A fixture such as `tmp_path` or `monkeypatch` is prepared fresh for each test, so tests do not affect each other.

## Walkthrough of this repository's use

### `tests/unit/infrastructure/test_readers.py`

`tests/unit/infrastructure/test_readers.py` lines 1 to 8:

```python
import pytest

from design_review.domain.capacity import ModelError
from design_review.infrastructure.filesystem import FileSystemStore
from design_review.infrastructure.markdown import MarkdownDocumentReader, table_rows
from design_review.infrastructure.model_toml import TomlModelSource
from design_review.infrastructure.settings import SettingsError, load_settings
from tests.conftest import MemoryStore, repository_files
```

> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.

Imports:

- It imports module `pytest`.
- From `design_review.domain.capacity` it takes `ModelError`.
- From `design_review.infrastructure.filesystem` it takes `FileSystemStore`.
- From `design_review.infrastructure.markdown` it takes `MarkdownDocumentReader, table_rows`.
- From `design_review.infrastructure.model_toml` it takes `TomlModelSource`.
- From `design_review.infrastructure.settings` it takes `SettingsError, load_settings`.
- From `tests.conftest` it takes `MemoryStore, repository_files`.

`tests/unit/infrastructure/test_readers.py` lines 11 to 12:

```python
def reader():
    return MarkdownDocumentReader(MemoryStore(repository_files()))
```

> **In plain words.** `return value` ends the function and gives the value back to whoever called it.

**Function `reader`.**

Step by step:

- Gives back the result of calling `MarkdownDocumentReader(MemoryStore(repository_files()))`.

`tests/unit/infrastructure/test_readers.py` lines 15 to 18:

```python
def test_table_rows_keys_cells_by_the_header_and_pads_short_rows():
    rows = table_rows(["| A | B |", "| --- | --- |", "| 1 | 2 |", "| 3 |", "", "| 9 | 9 |"])
    assert rows == [{"A": "1", "B": "2"}, {"A": "3", "B": ""}]
    assert table_rows(["no table here"]) == []
```

> **In plain words.** `assert condition` checks that something is true. In a test, a false condition fails the test and pytest shows both sides of the comparison.
> **In plain words.** `==` tests equality, `is` tests that two names are the very same object (used for `None` and enum members), `in` tests membership.
> **In plain words.** A **dictionary** `{key: value}` maps keys to values.
> **In plain words.** A **test** is a function whose name starts with `test_`. pytest finds it, runs it, and reports a pass when no `assert` fails and nothing raises.

**Test `test_table_rows_keys_cells_by_the_header_and_pads_short_rows`** checks: table rows keys cells by the header and pads short rows.

Step by step:

- Stores the result of calling `table_rows(['| A | B |', '| --- | --- |', '| 1 | 2 |', '| 3 |', '', '| 9 | 9 |'])` in `rows`.
- Checks that `rows` equals `[{'A': '1', 'B': '2'}, {'A': '3', 'B': ''}]`; if not, the test fails.
- Checks that `table_rows(['no table here'])` equals `[]`; if not, the test fails.

`tests/unit/infrastructure/test_readers.py` lines 21 to 25:

```python
def test_the_requirements_document_is_parsed():
    parsed = reader().read_requirements("docs/requirements/uploads-nfrs.md")
    assert [r.id for r in parsed.requirements] == ["R1", "R2", "R3", "R4", "R5", "R6"]
    assert parsed.requirements[2].target == "95 percent within 30 seconds of upload"
    assert "freshness" in parsed.required_categories
```

> **In plain words.** A **list comprehension** `[x for x in items if test]` is a loop written inside brackets: it builds a new list from the items that pass the test.
> **In plain words.** `obj[key]` looks a value up by key or position.

**Test `test_the_requirements_document_is_parsed`** checks: the requirements document is parsed.

Step by step:

- Stores the result of calling `reader().read_requirements('docs/requirements/uploads-nfrs.md')` in `parsed`.
- Checks that `[r.id for r in parsed.requirements]` equals `['R1', 'R2', 'R3', 'R4', 'R5', 'R6']`; if not, the test fails.
- Checks that `parsed.requirements[2].target` equals `'95 percent within 30 seconds of upload'`; if not, the test fails.
- Checks that `'freshness'` is in `parsed.required_categories`; if not, the test fails.

`tests/unit/infrastructure/test_readers.py` lines 28 to 30:

```python
def test_a_requirements_document_without_categories_uses_the_default_five():
    store = MemoryStore({"r.md": "# R\n\n## Requirements\n| ID | Category |\n| - | - |\n| R1 | throughput |\n"})
    assert MarkdownDocumentReader(store).read_requirements("r.md").required_categories[0] == "throughput"
```

**Test `test_a_requirements_document_without_categories_uses_the_default_five`** checks: a requirements document without categories uses the default five.

Step by step:

- Stores the result of calling `MemoryStore({'r.md': '# R\n\n## Requirements\n| ID | Category |\n| - | - |\n| R1 | throug…` in `store`.
- Checks that `MarkdownDocumentReader(store).read_requirements('…` equals `'throughput'`; if not, the test fails.

`tests/unit/infrastructure/test_readers.py` lines 33 to 38:

```python
def test_the_proposal_is_parsed_with_its_diagram():
    proposal = reader().read_proposal("docs/proposals/uploads-service-draft-1.md")
    assert proposal.author == "Uploads team lead"
    assert "thumbnail job (1 worker)" in proposal.diagram
    assert set(proposal.sections) >= {"Overview", "Datastore", "Unsure"}
    assert proposal.title.startswith("Proposal: photo uploads")
```

> **In plain words.** A **set** `{a, b}` holds items without duplicates; `frozenset` is a set that cannot be changed.

**Test `test_the_proposal_is_parsed_with_its_diagram`** checks: the proposal is parsed with its diagram.

Step by step:

- Stores the result of calling `reader().read_proposal('docs/proposals/uploads-service-draft-1.md')` in `proposal`.
- Checks that `proposal.author` equals `'Uploads team lead'`; if not, the test fails.
- Checks that `'thumbnail job (1 worker)'` is in `proposal.diagram`; if not, the test fails.
- Checks that `set(proposal.sections)` is at least `{'Overview', 'Datastore', 'Unsure'}`; if not, the test fails.
- Checks that `proposal.title.startswith('Proposal: photo uploads')`; if not, the test fails.

`tests/unit/infrastructure/test_readers.py` lines 41 to 54:

```python
def test_the_review_record_is_parsed():
    review = reader().read_review("docs/reviews/review-2026-10-22-uploads-service.md")
    assert (review.reviewers, review.author, review.date_text) == (
        "Platform architect",
        "Uploads team lead",
        "2026-10-22",
    )
    assert len(review.used) == 6
    assert [f.cls for f in review.findings][:5] == ["must-fix", "must-fix", "should-fix", "withdrawn", "taste"]
    assert review.findings[4].note == "dropped"
    assert review.disagreements[0].finding == "4"
    assert review.risks[0].owner == "Uploads team lead"
    assert len(review.decisions) == 3
    assert "Requirements used" in review.sections
```

> **In plain words.** A **tuple** `(a, b)` is a fixed list of values that cannot be changed.
> **In plain words.** A **slice** such as `text[:7]` or `items[1:]` takes part of a sequence: `[:7]` the first seven items, `[1:]` everything after the first.

**Test `test_the_review_record_is_parsed`** checks: the review record is parsed.

Step by step:

- Stores the result of calling `reader().read_review('docs/reviews/review-2026-10-22-uploads-service.md')` in `review`.
- Checks that `(review.reviewers, review.author, review.date_tex…` equals `('Platform architect', 'Uploads team lead', '2026…`; if not, the test fails.
- Checks that `len(review.used)` equals `6`; if not, the test fails.
- Checks that `[f.cls for f in review.findings][:5]` equals `['must-fix', 'must-fix', 'should-fix', 'withdrawn…`; if not, the test fails.
- Checks that `review.findings[4].note` equals `'dropped'`; if not, the test fails.
- Checks that `review.disagreements[0].finding` equals `'4'`; if not, the test fails.
- Checks that `review.risks[0].owner` equals `'Uploads team lead'`; if not, the test fails.
- Checks that `len(review.decisions)` equals `3`; if not, the test fails.
- Checks that `'Requirements used'` is in `review.sections`; if not, the test fails.

`tests/unit/infrastructure/test_readers.py` lines 57 to 59:

```python
def test_a_review_without_a_disagreement_has_none():
    store = MemoryStore({"r.md": "# Design review: x\n\n## Findings\n| # |\n| - |\n"})
    assert MarkdownDocumentReader(store).read_review("r.md").disagreements == ()
```

**Test `test_a_review_without_a_disagreement_has_none`** checks: a review without a disagreement has none.

Step by step:

- Stores the result of calling `MemoryStore({'r.md': '# Design review: x\n\n## Findings\n| # |\n| - |\n'})` in `store`.
- Checks that `MarkdownDocumentReader(store).read_review('r.md')…` equals `()`; if not, the test fails.

`tests/unit/infrastructure/test_readers.py` lines 62 to 64:

```python
def test_a_bullet_that_wraps_onto_the_next_line_is_one_decision():
    store = MemoryStore({"r.md": "# Design review: x\n\n## Decisions\n- first line\n  continues here\n- second\n"})
    assert MarkdownDocumentReader(store).read_review("r.md").decisions == ("first line continues here", "second")
```

**Test `test_a_bullet_that_wraps_onto_the_next_line_is_one_decision`** checks: a bullet that wraps onto the next line is one decision.

Step by step:

- Stores the result of calling `MemoryStore({'r.md': '# Design review: x\n\n## Decisions\n- first line\n continues here\n…` in `store`.
- Checks that `MarkdownDocumentReader(store).read_review('r.md')…` equals `('first line continues here', 'second')`; if not, the test fails.

`tests/unit/infrastructure/test_readers.py` lines 67 to 71:

```python
def test_the_checklist_is_parsed_and_malformed_lines_are_kept():
    store = MemoryStore({"c.md": "- [ ] CHK-01 [cost] Is there an estimate?\n- [ ] nope\ntext\n"})
    parsed = MarkdownDocumentReader(store).read_checklist("c.md")
    assert [(i.id, i.category) for i in parsed.items] == [("CHK-01", "cost")]
    assert parsed.malformed == ("- [ ] nope",)
```

**Test `test_the_checklist_is_parsed_and_malformed_lines_are_kept`** checks: the checklist is parsed and malformed lines are kept.

Step by step:

- Stores the result of calling `MemoryStore({'c.md': '- [ ] CHK-01 [cost] Is there an estimate?\n- [ ] nope\ntext\n'})` in `store`.
- Stores the result of calling `MarkdownDocumentReader(store).read_checklist('c.md')` in `parsed`.
- Checks that `[(i.id, i.category) for i in parsed.items]` equals `[('CHK-01', 'cost')]`; if not, the test fails.
- Checks that `parsed.malformed` equals `('- [ ] nope',)`; if not, the test fails.

`tests/unit/infrastructure/test_readers.py` lines 74 to 79:

```python
def test_the_model_file_is_loaded_and_validated():
    model = TomlModelSource(MemoryStore(repository_files())).load("model/uploads.toml")
    assert model.load.average_rate == pytest.approx(3.889, abs=0.001)
    assert [s.workers for s in model.thumbnails] == [1, 8, 80]
    assert [s.expect_pass for s in model.durability] == [False, True, True]
    assert model.burst.peak_rate == 40
```

> **In plain words.** A call such as `f(a, key=value)` passes `a` by position and `key` by name (a **keyword argument**).

**Test `test_the_model_file_is_loaded_and_validated`** checks: the model file is loaded and validated.

Step by step:

- Stores the result of calling `TomlModelSource(MemoryStore(repository_files())).load('model/uploads.toml')` in `model`.
- Checks that `model.load.average_rate` equals `pytest.approx(3.889, abs=0.001)`; if not, the test fails.
- Checks that `[s.workers for s in model.thumbnails]` equals `[1, 8, 80]`; if not, the test fails.
- Checks that `[s.expect_pass for s in model.durability]` equals `[False, True, True]`; if not, the test fails.
- Checks that `model.burst.peak_rate` equals `40`; if not, the test fails.

`tests/unit/infrastructure/test_readers.py` lines 82 to 82:

```python
GOOD = repository_files()["model/uploads.toml"]
```

> **In plain words.** A name written in CAPITAL letters is a **constant** by convention: a value set once, not changed later.

These module-level lines:

- Stores `repository_files()['model/uploads.toml']` in `GOOD`.

`tests/unit/infrastructure/test_readers.py` lines 85 to 97:

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

> **In plain words.** `@pytest.mark.parametrize` runs the same test function once for each row of data given; a failure names the row that broke.
> **In plain words.** `with pytest.raises(Error):` expects the code inside to raise that error; the test fails if it does not.

**Test `test_a_bad_model_file_is_rejected_with_a_reason`** checks: a bad model file is rejected with a reason.

It takes: `text`; `message`.

Decorators: `@pytest.mark.parametrize(('text', 'message'), [('not toml [', 'not val…`.

Step by step:

- Expects the steps inside to raise the error in `pytest.raises(ModelError, match=message)`:
  - Calls `TomlModelSource(MemoryStore({'m.toml': text})).load('m.toml')`.

`tests/unit/infrastructure/test_readers.py` lines 100 to 110:

```python
def test_the_file_system_store_reads_lists_and_writes(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.md").write_text("a")
    (tmp_path / "docs" / "b.txt").write_text("b")
    store = FileSystemStore(tmp_path)
    assert store.list_paths("docs") == ["docs/a.md"]
    assert store.list_paths("nope") == []
    store.write_text("build/r.md", "x")
    assert (store.exists("build/r.md"), store.read_text("build/r.md")) == (True, "x")
    with pytest.raises(ValueError, match="escapes"):
        store.read_text("../x")
```

> **In plain words.** `tmp_path` is a built-in pytest fixture: a fresh, empty temporary folder (a `Path`) that is removed after the test.

**Test `test_the_file_system_store_reads_lists_and_writes`** checks: the file system store reads lists and writes.

It takes: `tmp_path`.

Step by step:

- Calls `(tmp_path / 'docs').mkdir()`.
- Calls `(tmp_path / 'docs' / 'a.md').write_text('a')`.
- Calls `(tmp_path / 'docs' / 'b.txt').write_text('b')`.
- Stores the result of calling `FileSystemStore(tmp_path)` in `store`.
- Checks that `store.list_paths('docs')` equals `['docs/a.md']`; if not, the test fails.
- Checks that `store.list_paths('nope')` equals `[]`; if not, the test fails.
- Calls `store.write_text('build/r.md', 'x')`.
- Checks that `(store.exists('build/r.md'), store.read_text('bui…` equals `(True, 'x')`; if not, the test fails.
- Expects the steps inside to raise the error in `pytest.raises(ValueError, match='escapes')`:
  - Calls `store.read_text('../x')`.

`tests/unit/infrastructure/test_readers.py` lines 113 to 118:

```python
def test_settings_default_and_validate():
    assert load_settings({}).check.proposal_max_words == 1000
    assert load_settings({"PROPOSAL_MAX_WORDS": "500", "REVIEW_ROOT": "r"}).check.proposal_max_words == 500
    for bad in ("many", "0"):
        with pytest.raises(SettingsError):
            load_settings({"PROPOSAL_MAX_WORDS": bad})
```

> **In plain words.** A **`for` loop** repeats its steps once for each item of a collection. `range(n)` counts from 0 to n-1.

**Test `test_settings_default_and_validate`** checks: settings default and validate.

Step by step:

- Checks that `load_settings({}).check.proposal_max_words` equals `1000`; if not, the test fails.
- Checks that `load_settings({'PROPOSAL_MAX_WORDS': '500', 'REVI…` equals `500`; if not, the test fails.
- For each `bad` in the tuple `('many', '0')`:
  - Expects the steps inside to raise the error in `pytest.raises(SettingsError)`:
    - Calls `load_settings({'PROPOSAL_MAX_WORDS': bad})`.

## Try it yourself

```bash
.venv/bin/pytest -q tests/unit/infrastructure
```
Prints a row of dots, one per passing test, and a summary line such as `N passed in 0.5s` (skipped tests show as `s`).

```bash
.venv/bin/mypy
```
Checks the whole project (the `files` setting in `pyproject.toml`), these files included. Prints `Success: no issues found in 38 source files`.

```bash
.venv/bin/ruff check tests/unit/infrastructure/test_readers.py
```
Prints `All checks passed!`.

## Mistakes people make

- Tests that depend on each other's order. Each test here builds its own data.
- Asserting only the happy path. These tests also break the input on purpose and check the exact rule that fails.
- Forgetting `test_` in a name, so the test never runs.

## Check yourself

1. What does the test `test_table_rows_keys_cells_by_the_header_and_pads_short_rows` check?
   **Answer:** it checks: table rows keys cells by the header and pads short rows.
2. What does the test `test_the_requirements_document_is_parsed` check?
   **Answer:** it checks: the requirements document is parsed.
3. What does the test `test_a_requirements_document_without_categories_uses_the_default_five` check?
   **Answer:** it checks: a requirements document without categories uses the default five.
4. What does the test `test_the_proposal_is_parsed_with_its_diagram` check?
   **Answer:** it checks: the proposal is parsed with its diagram.
5. What does the test `test_the_review_record_is_parsed` check?
   **Answer:** it checks: the review record is parsed.

## Further reading

- pytest 9.1 documentation: <https://docs.pytest.org/en/stable/>
- How to use fixtures: <https://docs.pytest.org/en/stable/how-to/fixtures.html>
- `assert` rewriting: <https://docs.pytest.org/en/stable/how-to/assert.html>
