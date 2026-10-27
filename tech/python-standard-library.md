# The Python standard library modules this repository imports

## What it is

The **standard library** is the set of modules that come with Python itself. You `import` them; nothing is downloaded.
This note covers the smaller modules together. The bigger ones have their own notes: `dataclasses.md`, `re.md`,
`argparse.md`, `pathlib.md`, `tomllib.md`.

## Why this repository uses it

The program has no runtime dependencies on purpose: a reader can see everything it does, and nothing can be broken by
an update of someone else's package. The standard library is enough.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `enum` | `Severity` (ERROR or WARNING) is an `Enum`. |
| `typing.Protocol` | The small interfaces in `application/ports.py`. |
| `collections.abc` | Type names for read-only collections. |
| `os and sys` | The environment, the error stream and exit codes. |
| `shutil` | Copying folders in tests. |
| `math` | Rounding up a worker count. |
| `datetime.date` | Dates in the review headers. |
| `collections.abc.Iterator and yield` | A generator that produces one rate per second. |

## How it works underneath

A standard-library module is a file (or folder) inside Python's own installation. `import enum` finds it the same way
as any module, through `sys.path`. Some (`hashlib`, `random`) are partly written in C for speed. Their behavior is
fixed by the Python version, which is why this repository pins 3.12 as the lowest version.

## Walkthrough of this repository's use

### `enum`

`Severity` (ERROR or WARNING) is an `Enum`.

`src/design_review/domain/findings.py`:

```python
class Severity(Enum):
    """ERROR fails the check; WARNING is reported and does not."""

    ERROR = "error"
    WARNING = "warning"
```

An `Enum` is a fixed set of named values. `Severity.ERROR is Severity.ERROR` is always true, and `Severity("error")` looks the member up by its value.

### `typing.Protocol`

The small interfaces in `application/ports.py`.

`src/design_review/application/ports.py`:

```python
class DocumentStore(Protocol):
    """Reads and writes the repository's files by path relative to its root."""

    def list_paths(self, folder: str) -> list[str]:
        """Markdown files directly inside the folder, sorted; empty when the folder is missing."""
        ...

    def read_text(self, path: str) -> str:
```

A `Protocol` says "anything that has these methods will do". `FileSystemStore` and the tests' `MemoryStore` both fit `DocumentStore` without inheriting from it. The `...` as the body means "no code here, this is only the shape". mypy checks that every object passed in has the methods. This is how the inner layers use the disk without importing the file code.

### `collections.abc`

Type names for read-only collections.

`src/design_review/infrastructure/settings.py`:

```python
from collections.abc import Mapping
```

`Mapping[str, str]` means "something you can look up by key, I will not change it"; `Sequence[str]` means a list-like of strings. Using these instead of `dict` and `list` lets callers pass any compatible object.

### `os and sys`

The environment, the error stream and exit codes.

`src/design_review/interfaces/cli.py`:

```python
import os
import sys
from collections.abc import Sequence
```

`os.environ` holds the environment variables; `sys.stderr` is the error output stream; `sys.exit`/`SystemExit` ends the program with a code.

### `shutil`

Copying folders in tests.

`tests/unit/interfaces/test_cli.py`:

```python
    shutil.copytree(REPOSITORY_ROOT / "docs", tmp_path / "docs")
```

`shutil.copytree(source, destination)` copies a whole folder. The tests use it to work on a copy of `docs/`.

### `math`

Rounding up a worker count.

`src/design_review/domain/capacity.py`:

```python
    return math.ceil(rate * seconds_per_photo)
```

`math.ceil(x)` rounds up to the next whole number: 3.1 workers means 4 workers.

### `datetime.date`

Dates in the review headers.

`src/design_review/domain/review.py`:

```python
        date.fromisoformat(text.strip())
```

`date` holds a calendar date; the rules check the dates are valid.

### `collections.abc.Iterator and yield`

A generator that produces one rate per second.

`src/design_review/domain/queue_model.py`:

```python
    def rates(self, seconds: int) -> Iterator[float]:
        """The arrival rate for each second of the horizon."""
        for second in range(seconds):
            yield self.peak_rate if second % self.every_seconds < self.length_seconds else self.base_rate
```

A function with `yield` is a **generator**: calling it returns an iterator that produces one value at a time and remembers where it was. The simulation consumes the rates one by one without building a long list first.

## Try it yourself

```bash
.venv/bin/python -c "import sys; print(sys.version_info[:2], sys.stdlib_module_names >= {'enum', 're', 'argparse', 'dataclasses', 'pathlib'})"
```
Prints the Python version pair and `True`: these modules ship with Python, nothing is installed for them.

```bash
.venv/bin/python -c "from enum import Enum; print(list(__import__('design_review.domain.findings', fromlist=['x']).Severity))"
```
Prints the two members of `Severity`.

```bash
.venv/bin/python -c "from collections.abc import Mapping; print(isinstance({'a': 1}, Mapping), isinstance([1], Mapping))"
```
Prints `True False`.

```bash
grep -rhE "^(import|from) [a-z_.]+" src --include='*.py' | grep -v "design_review" | sort | uniq -c | sort -rn
```
Lists every standard-library module the source imports, with how often. Nothing outside the standard library appears.

## Mistakes people make

- **Naming your own file like a standard module** (`random.py`, `enum.py`). It hides the real one.
- **Using floats for money.** The migration kit uses `Decimal` for exactly this reason.
- **Using `random` without a seed** in a test, which makes failures impossible to repeat.
- **Importing a module for one tiny function** that a built-in covers.

## Check yourself

1. Why does the project list no runtime dependencies?
   **Answer:** Everything it needs is in the standard library.
2. What does a `Protocol` describe?
   **Answer:** The methods an object must have, without requiring inheritance.
3. What is the difference between `Mapping` and `dict` in a type hint?
   **Answer:** `Mapping` promises read-only use and accepts any mapping type; `dict` is the concrete type.
4. What does `Enum` guarantee?
   **Answer:** Only the listed members exist, and each is a single shared object.
5. How do you find out which standard modules the code uses?
   **Answer:** Search the imports, as the last example command does.

## Further reading

- Python 3.12 standard library: <https://docs.python.org/3.12/library/index.html>
- `enum`: <https://docs.python.org/3.12/library/enum.html>; `typing.Protocol`: <https://docs.python.org/3.12/library/typing.html#typing.Protocol>; `collections.abc`: <https://docs.python.org/3.12/library/collections.abc.html>
