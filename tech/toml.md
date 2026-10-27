# TOML

## What it is

TOML (Tom's Obvious, Minimal Language) is a text format for settings. It has `key = value` pairs, `[tables]`
(named groups), lists in square brackets and comments after `#`. Python's own packaging tools and most Python
tools read it.

## Why this repository uses it

`pyproject.toml` is where Python projects state their name, dependencies and tool settings, in TOML. This
repository keeps all tool settings there (ruff, mypy, pytest, coverage, import-linter), so there is one file to read.
It also keeps the review's numbers in a TOML model file so the code and the documents can be compared.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `pyproject.toml` | Project metadata and the settings of every tool. |
| `model/uploads.toml` | The numbers and scenarios the fitness code reads (see `tomllib.md`). |

## How it works underneath

A TOML reader turns the text into nested dictionaries. `[tool.ruff]` becomes the key `tool` holding the key `ruff`.
`[[tool.mypy.overrides]]` (double brackets) adds one more item to a **list of tables**. Values have types: text in
double quotes, integers, floats, booleans (`true`/`false`) and lists. Tools read only their own `tool.NAME` table and
ignore the rest.

## Walkthrough of this repository's use

`pyproject.toml`:

```toml
[project]
name = "architecture-leadership-design-review"
version = "0.1.0"
description = "Reviews a system proposal against quantified requirements: lints the proposal, requirements and review record, and runs fitness functions for capacity, queue age and write order."
readme = "README.md"
requires-python = ">=3.12"
license = { text = "MIT" }
authors = [{ name = "Sumit Srivastava" }]
dependencies = []

[project.optional-dependencies]
dev = [
```

- `[project]` is a table. Each line inside is a key and a value.
- `dependencies = []` is an empty list.
- `license = { text = "MIT" }` is an **inline table**: a small table on one line.
- `authors = [{ name = "Sumit Srivastava" }]` is a list holding one inline table.

`pyproject.toml`:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8,<10",
    "pytest-cov>=5",
    "ruff>=0.6",
    "mypy>=1.11",
    "import-linter>=2.0",
    "pip-audit>=2.7",
]
```

A list can span lines. Each string is a requirement with a version range: `pytest>=8,<10` means "at least 8 and
below 10". The group name `dev` is what `uv pip compile --extra dev` used (see `hash-pinned-lock-files.md`).

`pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.12"
strict = true
files = ["src", "tests"]
```

`[tool.mypy]` is for mypy only. `files = ["src", "tests"]` is a list of strings.

Other tables in the same file are covered in the notes for each tool: `setuptools.md`, `pytest.md`, `pytest-cov.md`,
`ruff.md`, `mypy.md` and `import-linter.md`.

### The complete file `model/uploads.toml`, line by line

`model/uploads.toml` lines 1 to 2:

```toml
# The facts of the uploads proposal and the scenarios the review tries. Read by `design-review fitness`.
# `expect` is the verdict the review recorded for the scenario; the command fails when a scenario gives another one.
```

> **In plain words.** TOML is a settings format. `key = value` sets a value; `[table]` starts a named group of settings; `[[table]]` adds one more item to a list of such groups; text is in double quotes, lists in square brackets; `#` starts a comment.

- These lines are comments written by the author; they are quoted above.

`model/uploads.toml` lines 4 to 8:

```toml
[load]
listings_per_week = 120000      # the setting: 120,000 listings a week
photos_per_listing = 10         # sellers upload up to 10 photos per listing
weekend_share = 0.70            # most of them between Friday evening and Sunday night
weekend_days = 2.5              # 216,000 seconds
```

- `[load]` starts the table `load`; the lines below belong to it.
- `listings_per_week` is set to the number `120000`.
- `photos_per_listing` is set to the number `10`.
- `weekend_share` is set to the number `0.70`.
- `weekend_days` is set to the number `2.5`.

`model/uploads.toml` lines 10 to 13:

```toml
[requirement]
peak_uploads_per_second = 40    # R1
thumbnail_percentile = 95       # R3: 95 percent ...
thumbnail_seconds = 30          # ... within 30 seconds of upload
```

- `[requirement]` starts the table `requirement`; the lines below belong to it.
- `peak_uploads_per_second` is set to the number `40`.
- `thumbnail_percentile` is set to the number `95`.
- `thumbnail_seconds` is set to the number `30`.

`model/uploads.toml` lines 15 to 16:

```toml
[service]
seconds_per_photo_per_worker = 2.0   # three sizes in about 2 seconds, so 0.5 photos a second per worker
```

- `[service]` starts the table `service`; the lines below belong to it.
- `seconds_per_photo_per_worker` is set to the number `2.0`.

`model/uploads.toml` lines 18 to 20:

```toml
[burst]
every_seconds = 3600            # a burst at the peak rate at the start of every hour ...
length_seconds = 60             # ... lasting a minute; the quiet rate is chosen so the mean stays at the average
```

- `[burst]` starts the table `burst`; the lines below belong to it.
- `every_seconds` is set to the number `3600`.
- `length_seconds` is set to the number `60`.

`model/uploads.toml` lines 22 to 24:

```toml
[thumbnails.draft1]             # the proposal: 1 worker
workers = 1
expect = "fail"
```

- `[thumbnails.draft1]` starts the table `thumbnails.draft1`; the lines below belong to it.
- `workers` is set to the number `1`: how many workers.
- `expect` is set to the text `"fail"`: the verdict the review recorded.

`model/uploads.toml` lines 26 to 28:

```toml
[thumbnails.floor]              # the sample record's "target 8 workers": covers the average, not the burst
workers = 8
expect = "fail"
```

- `[thumbnails.floor]` starts the table `thumbnails.floor`; the lines below belong to it.
- `workers` is set to the number `8`: how many workers.
- `expect` is set to the text `"fail"`: the verdict the review recorded.

`model/uploads.toml` lines 30 to 32:

```toml
[thumbnails.ceiling]            # the review's decision: autoscale on queue age, floor 8, ceiling 80
workers = 80
expect = "pass"
```

- `[thumbnails.ceiling]` starts the table `thumbnails.ceiling`; the lines below belong to it.
- `workers` is set to the number `80`: how many workers.
- `expect` is set to the text `"pass"`: the verdict the review recorded.

`model/uploads.toml` lines 34 to 36:

```toml
[durability.draft1]             # the response goes out once the file is stored, the row comes after
order = ["put_object", "respond", "write_row"]
expect = "fail"
```

- `[durability.draft1]` starts the table `durability.draft1`; the lines below belong to it.
- `order` is set to a list `["put_object", "respond", "write_row"]`: the order of the steps.
- `expect` is set to the text `"fail"`: the verdict the review recorded.

`model/uploads.toml` lines 38 to 40:

```toml
[durability.sequential]         # file, then row, then response: nothing accepted is lost, but a crash leaves an orphan
order = ["put_object", "write_row", "respond"]
expect = "pass"
```

- `[durability.sequential]` starts the table `durability.sequential`; the lines below belong to it.
- `order` is set to a list `["put_object", "write_row", "respond"]`: the order of the steps.
- `expect` is set to the text `"pass"`: the verdict the review recorded.

`model/uploads.toml` lines 42 to 44:

```toml
[durability.reviewed]           # the review's decision: the row first, as PENDING
order = ["write_row_pending", "put_object", "mark_stored", "respond"]
expect = "pass"
```

- `[durability.reviewed]` starts the table `durability.reviewed`; the lines below belong to it.
- `order` is set to a list `["write_row_pending", "put_object", "mark_stored", "respond"]`: the order of the steps.
- `expect` is set to the text `"pass"`: the verdict the review recorded.

### The complete file `pyproject.toml`, line by line

`pyproject.toml` lines 1 to 3:

```toml
[build-system]
requires = ["setuptools>=75"]
build-backend = "setuptools.build_meta"
```

> **In plain words.** TOML is a settings format. `key = value` sets a value; `[table]` starts a named group of settings; `[[table]]` adds one more item to a list of such groups; text is in double quotes, lists in square brackets; `#` starts a comment.

- `[build-system]` starts the table `build-system`; the lines below belong to it.
- `requires` is set to a list `["setuptools>=75"]`: what must be installed first (for a control: what it demands).
- `build-backend` is set to the text `"setuptools.build_meta"`: the program that builds the project.

`pyproject.toml` lines 5 to 13:

```toml
[project]
name = "architecture-leadership-design-review"
version = "0.1.0"
description = "Reviews a system proposal against quantified requirements: lints the proposal, requirements and review record, and runs fitness functions for capacity, queue age and write order."
readme = "README.md"
requires-python = ">=3.12"
license = { text = "MIT" }
authors = [{ name = "Sumit Srivastava" }]
dependencies = []
```

- `[project]` starts the table `project`; the lines below belong to it.
- `name` is set to the text `"architecture-leadership-design-review"`: the project's or item's name.
- `version` is set to the text `"0.1.0"`: the version number.
- `description` is set to the text `"Reviews a system proposal against quantified requirements: lints the…`: a description.
- `readme` is set to the text `"README.md"`: the file used as the long description.
- `requires-python` is set to the text `">=3.12"`: the oldest Python version allowed.
- `license` is set to a small table `{ text = "MIT" }`: the license.
- `authors` is set to a list `[{ name = "Sumit Srivastava" }]`: the authors.
- `dependencies` is set to a list `[]`: the packages needed to run.

`pyproject.toml` lines 15 to 23:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8,<10",
    "pytest-cov>=5",
    "ruff>=0.6",
    "mypy>=1.11",
    "import-linter>=2.0",
    "pip-audit>=2.7",
]
```

- `[project.optional-dependencies]` starts the table `project.optional-dependencies`; the lines below belong to it.
- `dev` is set to a list `[ "pytest>=8,<10", "pytest-cov>=5", "ruff>=0.6", "mypy>=1.11", "import-linter>=…`.

`pyproject.toml` lines 25 to 26:

```toml
[project.scripts]
design-review = "design_review.interfaces.cli:main"
```

- `[project.scripts]` starts the table `project.scripts`; the lines below belong to it.
- `design-review` is set to the text `"design_review.interfaces.cli:main"`.

`pyproject.toml` lines 28 to 29:

```toml
[tool.setuptools.packages.find]
where = ["src"]
```

- `[tool.setuptools.packages.find]` starts the table `tool.setuptools.packages.find`; the lines below belong to it.
- `where` is set to a list `["src"]`: the folder to search for packages.

`pyproject.toml` lines 31 to 35:

```toml
[tool.ruff]
line-length = 120
target-version = "py312"
src = ["src", "tests"]
extend-exclude = ["tech"]  # tech/ quotes fragments of code inside Markdown; ruff 0.17 would try to format them
```

- `[tool.ruff]` starts the table `tool.ruff`; the lines below belong to it.
- `line-length` is set to the number `120`: the longest allowed line, in characters.
- `target-version` is set to the text `"py312"`: the Python version to write for.
- `src` is set to a list `["src", "tests"]`: where first-party code lives.
- `extend-exclude` is set to a list `["tech"]`: extra folders the tool skips.

`pyproject.toml` lines 37 to 38:

```toml
[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM", "N", "C4", "RUF", "PT", "D100", "D101", "D103", "D104"]
```

- `[tool.ruff.lint]` starts the table `tool.ruff.lint`; the lines below belong to it.
- `select` is set to a list `["E", "F", "I", "B", "UP", "SIM", "N", "C4", "RUF", "PT", "D100", "D101", "D103…`: the rule groups switched on.

`pyproject.toml` lines 40 to 41:

```toml
[tool.ruff.lint.per-file-ignores]
"tests/**" = ["D"]
```

- `[tool.ruff.lint.per-file-ignores]` starts the table `tool.ruff.lint.per-file-ignores`; the lines below belong to it.
- `"tests/**"` is set to a list `["D"]`.

`pyproject.toml` lines 43 to 46:

```toml
[tool.mypy]
python_version = "3.12"
strict = true
files = ["src", "tests"]
```

- `[tool.mypy]` starts the table `tool.mypy`; the lines below belong to it.
- `python_version` is set to the text `"3.12"`: the Python version to check as.
- `strict` is set to `true`: switch on all the strict checks.
- `files` is set to a list `["src", "tests"]`: the files or folders to check.

`pyproject.toml` lines 48 to 52:

```toml
[[tool.mypy.overrides]]
module = ["tests.*"]
disallow_untyped_defs = false
disallow_incomplete_defs = false
disallow_untyped_calls = false
```

- `[[tool.mypy.overrides]]` starts a new item in the list of tables named `tool.mypy.overrides`.
- `module` is set to a list `["tests.*"]`.
- `disallow_untyped_defs` is set to `false`.
- `disallow_incomplete_defs` is set to `false`.
- `disallow_untyped_calls` is set to `false`.

`pyproject.toml` lines 54 to 56:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers"
```

- `[tool.pytest.ini_options]` starts the table `tool.pytest.ini_options`; the lines below belong to it.
- `testpaths` is set to a list `["tests"]`: where to look for tests.
- `addopts` is set to the text `"-ra --strict-markers"`: options always added to a run.

`pyproject.toml` lines 58 to 60:

```toml
[tool.coverage.run]
source = ["design_review"]
branch = true
```

- `[tool.coverage.run]` starts the table `tool.coverage.run`; the lines below belong to it.
- `source` is set to a list `["design_review"]`: the package to measure.
- `branch` is set to `true`: also measure each branch of an if.

`pyproject.toml` lines 62 to 64:

```toml
[tool.coverage.report]
show_missing = true
skip_covered = false
```

- `[tool.coverage.report]` starts the table `tool.coverage.report`; the lines below belong to it.
- `show_missing` is set to `true`: list the missed line numbers.
- `skip_covered` is set to `false`: leave fully covered files out of the table.

`pyproject.toml` lines 66 to 67:

```toml
[tool.importlinter]
root_package = "design_review"
```

- `[tool.importlinter]` starts the table `tool.importlinter`; the lines below belong to it.
- `root_package` is set to the text `"design_review"`: the package to analyse.

`pyproject.toml` lines 69 to 77:

```toml
[[tool.importlinter.contracts]]
name = "Layers: interfaces -> infrastructure -> application -> domain, never upward"
type = "layers"
layers = [
    "design_review.interfaces",
    "design_review.infrastructure",
    "design_review.application",
    "design_review.domain",
]
```

- `[[tool.importlinter.contracts]]` starts a new item in the list of tables named `tool.importlinter.contracts`.
- `name` is set to the text `"Layers: interfaces -> infrastructure -> application -> domain, never…`: the project's or item's name.
- `type` is set to the text `"layers"`: the kind of contract.
- `layers` is set to a list `[ "design_review.interfaces", "design_review.infrastructure", "design_review.ap…`: the modules from highest to lowest.

`pyproject.toml` lines 79 to 83:

```toml
[[tool.importlinter.contracts]]
name = "Domain and application use only the standard library and each other"
type = "forbidden"
source_modules = ["design_review.domain", "design_review.application"]
forbidden_modules = ["design_review.infrastructure", "design_review.interfaces"]
```

- `[[tool.importlinter.contracts]]` starts a new item in the list of tables named `tool.importlinter.contracts`.
- `name` is set to the text `"Domain and application use only the standard library and each other"`: the project's or item's name.
- `type` is set to the text `"forbidden"`: the kind of contract.
- `source_modules` is set to a list `["design_review.domain", "design_review.application"]`: the modules the rule applies to.
- `forbidden_modules` is set to a list `["design_review.infrastructure", "design_review.interfaces"]`: the modules they must not import.

## Try it yourself

```bash
.venv/bin/python -c "import tomllib, pprint; pprint.pprint(tomllib.load(open('pyproject.toml','rb'))['project'])"
```
Prints the `[project]` table as a Python dictionary (name, version, `requires-python`, ...).

```bash
.venv/bin/python -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); print(list(d['tool']))"
```
Prints `['ruff', 'mypy', 'pytest', 'coverage', 'importlinter', 'setuptools']` (the tables under `tool`).

```bash
.venv/bin/python -c "import tomllib; print(tomllib.loads('a = [1, 2]\nb = {c = true}'))"
```
Prints `{'a': [1, 2], 'b': {'c': True}}`.

## Mistakes people make

- **Quoting numbers** (`"120"`) so the value is text, not a number.
- **Mixing up `[table]` and `[[list of tables]]`.**
- **Forgetting commas** between list items.
- **Expecting comments to be kept** when a program rewrites the file.

## Check yourself

1. What does `[tool.ruff]` define?
   **Answer:** A table named `ruff` inside the table `tool`, holding ruff's settings.
2. What is the difference between `[x]` and `[[x]]`?
   **Answer:** `[x]` is one table; `[[x]]` adds an item to a list of tables.
3. How do you write a list?
   **Answer:** In square brackets, separated by commas.
4. Which Python module reads TOML?
   **Answer:** `tomllib`, in the standard library since 3.11.
5. What does `pytest>=8,<10` accept?
   **Answer:** Versions 8.x and 9.x.

## Further reading

- TOML 1.0.0 specification: <https://toml.io/en/v1.0.0>
- `pyproject.toml` specification: <https://packaging.python.org/en/latest/specifications/pyproject-toml/>
- Python `tomllib` (3.12): <https://docs.python.org/3.12/library/tomllib.html>
