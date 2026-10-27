# Domain layer code

## What it is

The rules and values: plain Python that decides things and never touches a file, a network or a database. (Every term is explained where it first appears in the walkthrough below.)

## Why this repository uses it

This is where the repository's domain work happens. Reading it file by file, with every line explained, is how a reader sees the work that was done.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `src/design_review/__init__.py` | 2 lines. Reviews a system proposal against quantified requirements and keeps the review honest. |
| `src/design_review/domain/__init__.py` | 1 lines. Pure rules and models. Depends on the standard library only. |
| `src/design_review/domain/capacity.py` | 52 lines. The arithmetic of the review: how much load arrives, and how much one stage can carry. |
| `src/design_review/domain/checklist.py` | 61 lines. The design checklist an author applies before the review, built from the findings reviews repeat. |
| `src/design_review/domain/durability.py` | 34 lines. Crash-point enumeration for the upload write order: can an accepted upload be lost? |
| `src/design_review/domain/findings.py` | 38 lines. The result of a rule: a finding with a code, a severity and the document it is about. |
| `src/design_review/domain/fitness.py` | 103 lines. Fitness functions: the requirements of the review, checked by arithmetic and simulation on every run. |
| `src/design_review/domain/proposal.py` | 31 lines. A design proposal: concrete enough to review. |
| `src/design_review/domain/queue_model.py` | 48 lines. A fluid queue in front of a worker pool: how long a photo waits when load comes in bursts. |
| `src/design_review/domain/requirements.py` | 52 lines. Quantified non-functional requirements: each one a number and a way to check it. |
| `src/design_review/domain/review.py` | 243 lines. The review record: findings tied to requirements, classified, with owners and dates. |
| `src/design_review/domain/text.py` | 10 lines. Small text helpers shared by the rules. |

## How it works underneath

The domain layer is the centre of the design. Because it imports nothing from the outer layers, every rule can be tested with plain values, fast, without setting anything up. import-linter fails the build if a domain file imports an outer layer.

## Walkthrough of this repository's use

### `src/design_review/__init__.py`

`src/design_review/__init__.py` lines 1 to 1:

```python
"""Reviews a system proposal against quantified requirements and keeps the review honest."""
```

> **In plain words.** A **docstring** is a text in triple quotes as the first thing in a module, class or function. Python keeps it as the thing's description, and ruff requires one on public code.

**Module description.** Reviews a system proposal against quantified requirements and keeps the review honest.

`src/design_review/__init__.py` lines 3 to 3:

```python
__version__ = "0.1.0"
```

These module-level lines:

- Stores the text `'0.1.0'` in `__version__`.

### `src/design_review/domain/__init__.py`

`src/design_review/domain/__init__.py` lines 1 to 1:

```python
"""Pure rules and models. Depends on the standard library only."""
```

> **In plain words.** A **docstring** is a text in triple quotes as the first thing in a module, class or function. Python keeps it as the thing's description, and ruff requires one on public code.

**Module description.** Pure rules and models. Depends on the standard library only.

### `src/design_review/domain/capacity.py`

`src/design_review/domain/capacity.py` lines 1 to 6:

```python
"""The arithmetic of the review: how much load arrives, and how much one stage can carry."""

from __future__ import annotations

import math
from dataclasses import dataclass
```

> **In plain words.** A **docstring** is a text in triple quotes as the first thing in a module, class or function. Python keeps it as the thing's description, and ruff requires one on public code.
> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.
> **In plain words.** `from __future__ import annotations` makes every type hint in the file lazy text. Python no longer evaluates a hint when the file loads, so a hint may name a class defined further down.

**Module description.** The arithmetic of the review: how much load arrives, and how much one stage can carry.

Imports:

- From `__future__` it takes `annotations`.
- It imports module `math`.
- From `dataclasses` it takes `dataclass`.

`src/design_review/domain/capacity.py` lines 9 to 10:

```python
class ModelError(ValueError):
    """A model value is out of range."""
```

> **In plain words.** A **class** is a blueprint for objects that bundle data with the functions that work on it. `class B(A)` means B is a kind of A and starts with everything A has.
> **In plain words.** A class that inherits from `Exception` is a new kind of **error**. `raise` stops the current function with it, and a `try ... except` further up decides what to do.

**Class `ModelError`**, a kind of `ValueError`. A model value is out of range.

`src/design_review/domain/capacity.py` lines 13 to 21:

```python
@dataclass(frozen=True)
class LoadModel:
    """The facts the lesson gives: listings a week, photos per listing, and when they arrive."""

    listings_per_week: int
    photos_per_listing: int
    weekend_share: float
    weekend_days: float
    peak_uploads_per_second: float
```

> **In plain words.** A **type hint** such as `x: int` or `-> str` says what kind of value a name holds or a function gives back. Python does not enforce hints when the program runs; the type checker mypy reads them before.
> **In plain words.** A **dataclass** is a class that mainly holds data. `@dataclass` writes `__init__`, `__repr__` and `__eq__` for you from the annotated fields; `frozen=True` forbids changing a field after the object is created.

**Class `LoadModel`**. The facts the lesson gives: listings a week, photos per listing, and when they arrive. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `listings_per_week`: a `int`.
- Field `photos_per_listing`: a `int`.
- Field `weekend_share`: a `float`.
- Field `weekend_days`: a `float`.
- Field `peak_uploads_per_second`: a `float`.

`src/design_review/domain/capacity.py` lines 23 to 29:

```python
    def __post_init__(self) -> None:
        if min(self.listings_per_week, self.photos_per_listing) <= 0 or self.weekend_days <= 0:
            raise ModelError("listings, photos and days must be positive")
        if not 0 < self.weekend_share <= 1:
            raise ModelError("weekend_share must be in (0, 1]")
        if self.peak_uploads_per_second <= 0:
            raise ModelError("the peak must be positive")
```

> **In plain words.** `raise Error(...)` stops the current function by signalling an error. `raise ... from None` hides the earlier error, so the user sees only the new, clearer message.
> **In plain words.** `==` tests equality, `is` tests that two names are the very same object (used for `None` and enum members), `in` tests membership.

**Method `__post_init__` of class `LoadModel`.**

It gives back a `None`.

Step by step:

- If `min(self.listings_per_week, self.photos_per_listi…` is at most `0` or `self.weekend_days` is at most `0`:
  - Stops here by raising `ModelError('listings, photos and days must be positive')`.
- If not (`0` is less than `self.weekend_share` is at most `1`):
  - Stops here by raising `ModelError('weekend_share must be in (0, 1]')`.
- If `self.peak_uploads_per_second` is at most `0`:
  - Stops here by raising `ModelError('the peak must be positive')`.

`src/design_review/domain/capacity.py` lines 31 to 34:

```python
    @property
    def photos_per_week(self) -> int:
        """Most photos a week: every listing with its maximum number of photos."""
        return self.listings_per_week * self.photos_per_listing
```

> **In plain words.** `return value` ends the function and gives the value back to whoever called it.

**Method `photos_per_week` of class `LoadModel`.** Most photos a week: every listing with its maximum number of photos.

It gives back a `int`.

Decorators: `@property`.

Step by step:

- Gives back `self.listings_per_week * self.photos_per_listing`.

`src/design_review/domain/capacity.py` lines 36 to 39:

```python
    @property
    def weekend_seconds(self) -> float:
        """The length of the busy window in seconds."""
        return self.weekend_days * 86_400
```

**Method `weekend_seconds` of class `LoadModel`.** The length of the busy window in seconds.

It gives back a `float`.

Decorators: `@property`.

Step by step:

- Gives back `self.weekend_days * 86400`.

`src/design_review/domain/capacity.py` lines 41 to 44:

```python
    @property
    def average_rate(self) -> float:
        """Photos a second, averaged over the busy window."""
        return self.photos_per_week * self.weekend_share / self.weekend_seconds
```

**Method `average_rate` of class `LoadModel`.** Photos a second, averaged over the busy window.

It gives back a `float`.

Decorators: `@property`.

Step by step:

- Gives back `self.photos_per_week * self.weekend_share / self.weekend_seconds`.

`src/design_review/domain/capacity.py` lines 46 to 49:

```python
    @property
    def peak_ratio(self) -> float:
        """How many times the average the requirement's peak is."""
        return self.peak_uploads_per_second / self.average_rate
```

**Method `peak_ratio` of class `LoadModel`.** How many times the average the requirement's peak is.

It gives back a `float`.

Decorators: `@property`.

Step by step:

- Gives back `self.peak_uploads_per_second / self.average_rate`.

`src/design_review/domain/capacity.py` lines 52 to 66:

```python
@dataclass(frozen=True)
class Stage:
    """A worker pool: how many workers and how long one worker takes for one photo (all sizes)."""

    workers: int
    seconds_per_photo: float

    def __post_init__(self) -> None:
        if self.workers <= 0 or self.seconds_per_photo <= 0:
            raise ModelError("workers and seconds per photo must be positive")

    @property
    def capacity(self) -> float:
        """Photos a second this pool can finish."""
        return self.workers / self.seconds_per_photo
```

> **In plain words.** A call such as `f(a, key=value)` passes `a` by position and `key` by name (a **keyword argument**).

**Class `Stage`**. A worker pool: how many workers and how long one worker takes for one photo (all sizes). Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `workers`: a `int`.
- Field `seconds_per_photo`: a `float`.

Its methods, in order:

**Method `__post_init__` of class `Stage`.**

It gives back a `None`.

Step by step:

- If `self.workers` is at most `0` or `self.seconds_per_photo` is at most `0`:
  - Stops here by raising `ModelError('workers and seconds per photo must be positive')`.

**Method `capacity` of class `Stage`.** Photos a second this pool can finish.

It gives back a `float`.

Decorators: `@property`.

Step by step:

- Gives back `self.workers / self.seconds_per_photo`.

`src/design_review/domain/capacity.py` lines 69 to 71:

```python
def workers_needed(rate: float, seconds_per_photo: float) -> int:
    """The smallest pool that keeps up with a rate of photos a second."""
    return math.ceil(rate * seconds_per_photo)
```

**Function `workers_needed`.** The smallest pool that keeps up with a rate of photos a second.

It takes: `rate` (a `float`); `seconds_per_photo` (a `float`).

It gives back a `int`.

Step by step:

- Gives back the result of calling `math.ceil(rate * seconds_per_photo)`.

### `src/design_review/domain/checklist.py`

`src/design_review/domain/checklist.py` lines 1 to 10:

```python
"""The design checklist an author applies before the review, built from the findings reviews repeat."""

from __future__ import annotations

import re
from dataclasses import dataclass

from design_review.domain.findings import Finding, error
from design_review.domain.requirements import RequirementSet
from design_review.domain.review import ReviewRecord, requirement_category
```

> **In plain words.** A **docstring** is a text in triple quotes as the first thing in a module, class or function. Python keeps it as the thing's description, and ruff requires one on public code.
> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.
> **In plain words.** `from __future__ import annotations` makes every type hint in the file lazy text. Python no longer evaluates a hint when the file loads, so a hint may name a class defined further down.

**Module description.** The design checklist an author applies before the review, built from the findings reviews repeat.

Imports:

- From `__future__` it takes `annotations`.
- It imports module `re`.
- From `dataclasses` it takes `dataclass`.
- From `design_review.domain.findings` it takes `Finding, error`.
- From `design_review.domain.requirements` it takes `RequirementSet`.
- From `design_review.domain.review` it takes `ReviewRecord, requirement_category`.

`src/design_review/domain/checklist.py` lines 12 to 12:

```python
ITEM = re.compile(r"^- \[ \] (CHK-\d+) \[([a-z-]+)\] (.+)$")
```

> **In plain words.** A **regular expression** is a short pattern for text, such as `^## (.+)$` for "a line starting with ## ". `re.compile` prepares it once; `.match` tries it at the start of a string and returns a match object or `None`.
> **In plain words.** A name written in CAPITAL letters is a **constant** by convention: a value set once, not changed later.

These module-level lines:

- Stores the result of calling `re.compile('^- \\[ \\] (CHK-\\d+) \\[([a-z-]+)\\] (.+)$')` in `ITEM`.

`src/design_review/domain/checklist.py` lines 15 to 21:

```python
@dataclass(frozen=True)
class ChecklistItem:
    """One question, tagged with the requirement category it protects."""

    id: str
    category: str
    question: str
```

> **In plain words.** A **class** is a blueprint for objects that bundle data with the functions that work on it. `class B(A)` means B is a kind of A and starts with everything A has.
> **In plain words.** A **type hint** such as `x: int` or `-> str` says what kind of value a name holds or a function gives back. Python does not enforce hints when the program runs; the type checker mypy reads them before.
> **In plain words.** A call such as `f(a, key=value)` passes `a` by position and `key` by name (a **keyword argument**).
> **In plain words.** A **dataclass** is a class that mainly holds data. `@dataclass` writes `__init__`, `__repr__` and `__eq__` for you from the annotated fields; `frozen=True` forbids changing a field after the object is created.

**Class `ChecklistItem`**. One question, tagged with the requirement category it protects. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `id`: a `str`.
- Field `category`: a `str`.
- Field `question`: a `str`.

`src/design_review/domain/checklist.py` lines 24 to 30:

```python
@dataclass(frozen=True)
class Checklist:
    """A parsed checklist. `malformed` holds the lines that look like items but do not parse."""

    path: str
    items: tuple[ChecklistItem, ...]
    malformed: tuple[str, ...]
```

> **In plain words.** `obj[key]` looks a value up by key or position.
> **In plain words.** A **tuple** `(a, b)` is a fixed list of values that cannot be changed.

**Class `Checklist`**. A parsed checklist. `malformed` holds the lines that look like items but do not parse. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `path`: a `str`.
- Field `items`: a `tuple[ChecklistItem, ...]`.
- Field `malformed`: a `tuple[str, ...]`.

`src/design_review/domain/checklist.py` lines 33 to 39:

```python
def check_checklist(
    checklist: Checklist,
    requirement_set: RequirementSet,
    reviews: list[ReviewRecord],
    max_items: int = 12,
) -> list[Finding]:
    """CHK001 to CHK003."""
```

**Function `check_checklist`.** CHK001 to CHK003.

It takes: `checklist` (a `Checklist`); `requirement_set` (a `RequirementSet`); `reviews` (a `list[ReviewRecord]`); `max_items` (a `int`), default `12`.

It gives back a `list[Finding]`.

`src/design_review/domain/checklist.py` lines 40 to 59:

```python
    found = [
        error("CHK001", checklist.path, f"not an item (- [ ] CHK-NN [category] question?): {line}")
        for line in checklist.malformed
    ]
    categories = {requirement.category for requirement in requirement_set.requirements}
    for item in checklist.items:
        if item.category not in categories:
            found.append(
                error("CHK001", checklist.path, f"{item.id}: category {item.category!r} is not a requirement category")
            )
        if not item.question.endswith("?"):
            found.append(error("CHK001", checklist.path, f"{item.id}: an item is a question"))
    if len(checklist.items) > max_items:
        found.append(
            error(
                "CHK003",
                checklist.path,
                f"{len(checklist.items)} items; a checklist people use is short ({max_items} at most)",
            )
        )
```

> **In plain words.** A **list comprehension** `[x for x in items if test]` is a loop written inside brackets: it builds a new list from the items that pass the test.
> **In plain words.** An **f-string** `f"...{value}..."` is text with Python expressions in braces; Python replaces each by its value. `{x!r}` shows the value the way Python would write it, with quotes.
> **In plain words.** A **set comprehension** `{x for ...}` builds a set (a collection with no duplicates) with a loop.
> **In plain words.** A **`for` loop** repeats its steps once for each item of a collection. `range(n)` counts from 0 to n-1.
> **In plain words.** `==` tests equality, `is` tests that two names are the very same object (used for `None` and enum members), `in` tests membership.

**`check_checklist`, part 1 of 2.**

Step by step:

- Stores a new list made by a loop (`[error('CHK001', checklist.path, f'not an item (- [ ] CHK-NN [categor…`) in `found`.
- Stores a new set made by a loop (`{requirement.category for requirement in requirement_set.requirements}`) in `categories`.
- For each `item` in `checklist.items`:
  - If `item.category` is not in `categories`:
    - Calls `found.append(error('CHK001', checklist.path, f'{item.id}: category {item.category!r} is not a requirement cat…`.
  - If not (`item.question.endswith('?')`):
    - Calls `found.append(error('CHK001', checklist.path, f'{item.id}: an item is a question'))`.
- If `len(checklist.items)` is more than `max_items`:
  - Calls `found.append(error('CHK003', checklist.path, f'{len(checklist.items)} items; a checklist people use is short …`.

`src/design_review/domain/checklist.py` lines 60 to 73:

```python
    covered = {item.category for item in checklist.items}
    for review in reviews:
        for finding in review.findings:
            if finding.cls in ("must-fix", "should-fix"):
                category = requirement_category(requirement_set, finding.requirement)
                if category is not None and category not in covered:
                    found.append(
                        error(
                            "CHK002",
                            checklist.path,
                            f"finding {finding.number} of {review.path} is in '{category}', which no item covers",
                        )
                    )
    return found
```

> **In plain words.** `return value` ends the function and gives the value back to whoever called it.

**`check_checklist`, part 2 of 2.**

Step by step:

- Stores a new set made by a loop (`{item.category for item in checklist.items}`) in `covered`.
- For each `review` in `reviews`:
  - For each `finding` in `review.findings`:
    - If `finding.cls` is in `('must-fix', 'should-fix')`:
      - Stores the result of calling `requirement_category(requirement_set, finding.requirement)` in `category`.
      - If `category` is not the same object as `None` and `category` is not in `covered`:
        - Calls `found.append(error('CHK002', checklist.path, f"finding {finding.number} of {review.path} is in '{category}', …`.
- Gives back `found`.

### `src/design_review/domain/durability.py`

`src/design_review/domain/durability.py` lines 1 to 5:

```python
"""Crash-point enumeration for the upload write order: can an accepted upload be lost?"""

from __future__ import annotations

from dataclasses import dataclass
```

> **In plain words.** A **docstring** is a text in triple quotes as the first thing in a module, class or function. Python keeps it as the thing's description, and ruff requires one on public code.
> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.
> **In plain words.** `from __future__ import annotations` makes every type hint in the file lazy text. Python no longer evaluates a hint when the file loads, so a hint may name a class defined further down.

**Module description.** Crash-point enumeration for the upload write order: can an accepted upload be lost?

Imports:

- From `__future__` it takes `annotations`.
- From `dataclasses` it takes `dataclass`.

`src/design_review/domain/durability.py` lines 7 to 7:

```python
STEPS = frozenset({"write_row", "write_row_pending", "put_object", "mark_stored", "respond"})
```

> **In plain words.** A **set** `{a, b}` holds items without duplicates; `frozenset` is a set that cannot be changed.
> **In plain words.** A name written in CAPITAL letters is a **constant** by convention: a value set once, not changed later.

These module-level lines:

- Stores the result of calling `frozenset({'write_row', 'write_row_pending', 'put_object', 'mark_stored', 'respond'})` in `STEPS`.

`src/design_review/domain/durability.py` lines 10 to 21:

```python
@dataclass(frozen=True)
class DurabilityResult:
    """The order tried and every crash point where an upload the seller was told about is missing a part."""

    order: tuple[str, ...]
    violations: tuple[str, ...]
    orphans: tuple[str, ...] = ()

    @property
    def holds(self) -> bool:
        """True when no crash point loses an accepted upload."""
        return not self.violations
```

> **In plain words.** A **class** is a blueprint for objects that bundle data with the functions that work on it. `class B(A)` means B is a kind of A and starts with everything A has.
> **In plain words.** A **type hint** such as `x: int` or `-> str` says what kind of value a name holds or a function gives back. Python does not enforce hints when the program runs; the type checker mypy reads them before.
> **In plain words.** A call such as `f(a, key=value)` passes `a` by position and `key` by name (a **keyword argument**).
> **In plain words.** `obj[key]` looks a value up by key or position.
> **In plain words.** A **tuple** `(a, b)` is a fixed list of values that cannot be changed.
> **In plain words.** `return value` ends the function and gives the value back to whoever called it.
> **In plain words.** A **dataclass** is a class that mainly holds data. `@dataclass` writes `__init__`, `__repr__` and `__eq__` for you from the annotated fields; `frozen=True` forbids changing a field after the object is created.

**Class `DurabilityResult`**. The order tried and every crash point where an upload the seller was told about is missing a part. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `order`: a `tuple[str, ...]`.
- Field `violations`: a `tuple[str, ...]`.
- Field `orphans`: a `tuple[str, ...]`, default `()`.

Its methods, in order:

**Method `holds` of class `DurabilityResult`.** True when no crash point loses an accepted upload.

It gives back a `bool`.

Decorators: `@property`.

Step by step:

- Gives back whether not (`self.violations`).

`src/design_review/domain/durability.py` lines 24 to 43:

```python
def check_write_order(order: tuple[str, ...]) -> DurabilityResult:
    """Crash after each prefix of the steps. Once `respond` has run the seller believes the upload is safe,
    so the row and the object must both exist. A half-written upload that was never acknowledged loses nothing,
    but an object with no row is an orphan nobody can find, so those crash points are reported too.
    """
    unknown = [step for step in order if step not in STEPS]
    if unknown:
        raise ValueError(f"unknown steps: {', '.join(unknown)}")
    violations: list[str] = []
    orphans: list[str] = []
    for crash_after in range(len(order) + 1):
        done = order[:crash_after]
        row = "write_row" in done or "write_row_pending" in done
        stored = "put_object" in done
        if "respond" in done and not (row and stored):
            missing = "the row" if stored else "the object" if row else "the row and the object"
            violations.append(f"crash after {', '.join(done)}: the seller was told yes, but {missing} is missing")
        if stored and not row:
            orphans.append(f"crash after {', '.join(done)}: an object with no row to find it by")
    return DurabilityResult(order, tuple(violations), tuple(orphans))
```

> **In plain words.** A **`for` loop** repeats its steps once for each item of a collection. `range(n)` counts from 0 to n-1.
> **In plain words.** A **list comprehension** `[x for x in items if test]` is a loop written inside brackets: it builds a new list from the items that pass the test.
> **In plain words.** `raise Error(...)` stops the current function by signalling an error. `raise ... from None` hides the earlier error, so the user sees only the new, clearer message.
> **In plain words.** `==` tests equality, `is` tests that two names are the very same object (used for `None` and enum members), `in` tests membership.
> **In plain words.** An **f-string** `f"...{value}..."` is text with Python expressions in braces; Python replaces each by its value. `{x!r}` shows the value the way Python would write it, with quotes.
> **In plain words.** A **slice** such as `text[:7]` or `items[1:]` takes part of a sequence: `[:7]` the first seven items, `[1:]` everything after the first.
> **In plain words.** `A if test else B` is a **conditional expression**: its value is A when the test is true, otherwise B.

**Function `check_write_order`.** Crash after each prefix of the steps. Once `respond` has run the seller believes the upload is safe, so the row and the object must both exist. A half-written upload that was never acknowledged loses nothing, but an object with no row is an orphan nobody can find, so those crash points are reported…

It takes: `order` (a `tuple[str, ...]`).

It gives back a `DurabilityResult`.

Step by step:

- Stores a new list made by a loop (`[step for step in order if step not in STEPS]`) in `unknown`.
- If `unknown`:
  - Stops here by raising `ValueError(f"unknown steps: {', '.join(unknown)}")`.
- Declares `violations` as a `list[str]` and stores the list `[]` in it.
- Declares `orphans` as a `list[str]` and stores the list `[]` in it.
- For each `crash_after` in the result of calling `range(len(order) + 1)`:
  - Stores `order[:crash_after]` in `done`.
  - Stores whether `'write_row'` is in `done` or `'write_row_pending'` is in `done` in `row`.
  - Stores whether `'put_object'` is in `done` in `stored`.
  - If `'respond'` is in `done` and not (`row` and `stored`):
    - Stores `'the row'` if `stored`, otherwise `'the object' if row else 'the row and t…` in `missing`.
    - Calls `violations.append(f"crash after {', '.join(done)}: the seller was told yes, but {missing} is missing")`.
  - If `stored` and not (`row`):
    - Calls `orphans.append(f"crash after {', '.join(done)}: an object with no row to find it by")`.
- Gives back the result of calling `DurabilityResult(order, tuple(violations), tuple(orphans))`.

### `src/design_review/domain/findings.py`

`src/design_review/domain/findings.py` lines 1 to 6:

```python
"""The result of a rule: a finding with a code, a severity and the document it is about."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
```

> **In plain words.** A **docstring** is a text in triple quotes as the first thing in a module, class or function. Python keeps it as the thing's description, and ruff requires one on public code.
> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.
> **In plain words.** `from __future__ import annotations` makes every type hint in the file lazy text. Python no longer evaluates a hint when the file loads, so a hint may name a class defined further down.

**Module description.** The result of a rule: a finding with a code, a severity and the document it is about.

Imports:

- From `__future__` it takes `annotations`.
- From `dataclasses` it takes `dataclass`.
- From `enum` it takes `Enum`.

`src/design_review/domain/findings.py` lines 9 to 13:

```python
class Severity(Enum):
    """ERROR fails the check; WARNING is reported and does not."""

    ERROR = "error"
    WARNING = "warning"
```

> **In plain words.** A **class** is a blueprint for objects that bundle data with the functions that work on it. `class B(A)` means B is a kind of A and starts with everything A has.
> **In plain words.** An **Enum** is a class whose members are the only allowed values of a fixed set, such as `Severity.ERROR` and `Severity.WARNING`.

**Class `Severity`**, a kind of `Enum`. ERROR fails the check; WARNING is reported and does not.

Its parts:

- Class value `ERROR` set to the text `'error'`.
- Class value `WARNING` set to the text `'warning'`.

`src/design_review/domain/findings.py` lines 16 to 23:

```python
@dataclass(frozen=True)
class Finding:
    """One rule violation. The code names the rule so a test and a reader can point at it."""

    code: str
    severity: Severity
    subject: str
    message: str
```

> **In plain words.** A **type hint** such as `x: int` or `-> str` says what kind of value a name holds or a function gives back. Python does not enforce hints when the program runs; the type checker mypy reads them before.
> **In plain words.** A call such as `f(a, key=value)` passes `a` by position and `key` by name (a **keyword argument**).
> **In plain words.** A **dataclass** is a class that mainly holds data. `@dataclass` writes `__init__`, `__repr__` and `__eq__` for you from the annotated fields; `frozen=True` forbids changing a field after the object is created.

**Class `Finding`**. One rule violation. The code names the rule so a test and a reader can point at it. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `code`: a `str`.
- Field `severity`: a `Severity`.
- Field `subject`: a `str`.
- Field `message`: a `str`.

`src/design_review/domain/findings.py` lines 26 to 28:

```python
def error(code: str, subject: str, message: str) -> Finding:
    """Build an ERROR finding."""
    return Finding(code, Severity.ERROR, subject, message)
```

> **In plain words.** `return value` ends the function and gives the value back to whoever called it.

**Function `error`.** Build an ERROR finding.

It takes: `code` (a `str`); `subject` (a `str`); `message` (a `str`).

It gives back a `Finding`.

Step by step:

- Gives back the result of calling `Finding(code, Severity.ERROR, subject, message)`.

`src/design_review/domain/findings.py` lines 31 to 33:

```python
def warning(code: str, subject: str, message: str) -> Finding:
    """Build a WARNING finding."""
    return Finding(code, Severity.WARNING, subject, message)
```

**Function `warning`.** Build a WARNING finding.

It takes: `code` (a `str`); `subject` (a `str`); `message` (a `str`).

It gives back a `Finding`.

Step by step:

- Gives back the result of calling `Finding(code, Severity.WARNING, subject, message)`.

`src/design_review/domain/findings.py` lines 36 to 56:

```python
@dataclass(frozen=True)
class Report:
    """Every finding from one run, plus the subjects that were checked."""

    subjects: tuple[str, ...]
    findings: tuple[Finding, ...]

    @property
    def errors(self) -> tuple[Finding, ...]:
        """The findings that fail the check."""
        return tuple(f for f in self.findings if f.severity is Severity.ERROR)

    @property
    def warnings(self) -> tuple[Finding, ...]:
        """The findings that are reported without failing the check."""
        return tuple(f for f in self.findings if f.severity is Severity.WARNING)

    @property
    def ok(self) -> bool:
        """True when no finding is an error."""
        return not self.errors
```

> **In plain words.** `obj[key]` looks a value up by key or position.
> **In plain words.** A **tuple** `(a, b)` is a fixed list of values that cannot be changed.
> **In plain words.** A **generator expression** `(x for x in items)` is like a list comprehension, but it hands out one value at a time instead of building the whole list; here it is passed straight to a function such as `tuple(...)` or `sum(...)`.
> **In plain words.** `==` tests equality, `is` tests that two names are the very same object (used for `None` and enum members), `in` tests membership.

**Class `Report`**. Every finding from one run, plus the subjects that were checked. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `subjects`: a `tuple[str, ...]`.
- Field `findings`: a `tuple[Finding, ...]`.

Its methods, in order:

**Method `errors` of class `Report`.** The findings that fail the check.

It gives back a `tuple[Finding, ...]`.

Decorators: `@property`.

Step by step:

- Gives back the result of calling `tuple((f for f in self.findings if f.severity is Severity.ERROR))`.

**Method `warnings` of class `Report`.** The findings that are reported without failing the check.

It gives back a `tuple[Finding, ...]`.

Decorators: `@property`.

Step by step:

- Gives back the result of calling `tuple((f for f in self.findings if f.severity is Severity.WARNING))`.

**Method `ok` of class `Report`.** True when no finding is an error.

It gives back a `bool`.

Decorators: `@property`.

Step by step:

- Gives back whether not (`self.errors`).

### `src/design_review/domain/fitness.py`

`src/design_review/domain/fitness.py` lines 1 to 9:

```python
"""Fitness functions: the requirements of the review, checked by arithmetic and simulation on every run."""

from __future__ import annotations

from dataclasses import dataclass

from design_review.domain.capacity import LoadModel, Stage, workers_needed
from design_review.domain.durability import DurabilityResult, check_write_order
from design_review.domain.queue_model import BurstProfile, percentile_wait, simulate_waits
```

> **In plain words.** A **docstring** is a text in triple quotes as the first thing in a module, class or function. Python keeps it as the thing's description, and ruff requires one on public code.
> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.
> **In plain words.** `from __future__ import annotations` makes every type hint in the file lazy text. Python no longer evaluates a hint when the file loads, so a hint may name a class defined further down.

**Module description.** Fitness functions: the requirements of the review, checked by arithmetic and simulation on every run.

Imports:

- From `__future__` it takes `annotations`.
- From `dataclasses` it takes `dataclass`.
- From `design_review.domain.capacity` it takes `LoadModel, Stage, workers_needed`.
- From `design_review.domain.durability` it takes `DurabilityResult, check_write_order`.
- From `design_review.domain.queue_model` it takes `BurstProfile, percentile_wait, simulate_waits`.

`src/design_review/domain/fitness.py` lines 12 to 17:

```python
@dataclass(frozen=True)
class ThumbnailRequirement:
    """Thumbnails ready within `seconds` for `percentile` percent of uploads."""

    percentile: float
    seconds: float
```

> **In plain words.** A **class** is a blueprint for objects that bundle data with the functions that work on it. `class B(A)` means B is a kind of A and starts with everything A has.
> **In plain words.** A **type hint** such as `x: int` or `-> str` says what kind of value a name holds or a function gives back. Python does not enforce hints when the program runs; the type checker mypy reads them before.
> **In plain words.** A call such as `f(a, key=value)` passes `a` by position and `key` by name (a **keyword argument**).
> **In plain words.** A **dataclass** is a class that mainly holds data. `@dataclass` writes `__init__`, `__repr__` and `__eq__` for you from the annotated fields; `frozen=True` forbids changing a field after the object is created.

**Class `ThumbnailRequirement`**. Thumbnails ready within `seconds` for `percentile` percent of uploads. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `percentile`: a `float`.
- Field `seconds`: a `float`.

`src/design_review/domain/fitness.py` lines 20 to 26:

```python
@dataclass(frozen=True)
class ThumbnailScenario:
    """One worker count to try, and the verdict the review expects for it."""

    name: str
    workers: int
    expect_pass: bool
```

**Class `ThumbnailScenario`**. One worker count to try, and the verdict the review expects for it. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `name`: a `str`.
- Field `workers`: a `int`.
- Field `expect_pass`: a `bool`.

`src/design_review/domain/fitness.py` lines 29 to 45:

```python
@dataclass(frozen=True)
class ThumbnailResult:
    """Capacity, the workers the peak needs, and the simulated wait."""

    scenario: ThumbnailScenario
    capacity: float
    average_rate: float
    peak_rate: float
    workers_for_peak: int
    percentile: float
    wait_at_percentile: float
    passed: bool

    @property
    def as_expected(self) -> bool:
        """True when the verdict is the one the review recorded for this scenario."""
        return self.passed is self.scenario.expect_pass
```

> **In plain words.** `return value` ends the function and gives the value back to whoever called it.
> **In plain words.** `==` tests equality, `is` tests that two names are the very same object (used for `None` and enum members), `in` tests membership.

**Class `ThumbnailResult`**. Capacity, the workers the peak needs, and the simulated wait. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `scenario`: a `ThumbnailScenario`.
- Field `capacity`: a `float`.
- Field `average_rate`: a `float`.
- Field `peak_rate`: a `float`.
- Field `workers_for_peak`: a `int`.
- Field `percentile`: a `float`.
- Field `wait_at_percentile`: a `float`.
- Field `passed`: a `bool`.

Its methods, in order:

**Method `as_expected` of class `ThumbnailResult`.** True when the verdict is the one the review recorded for this scenario.

It gives back a `bool`.

Decorators: `@property`.

Step by step:

- Gives back whether `self.passed` is the same object as `self.scenario.expect_pass`.

`src/design_review/domain/fitness.py` lines 48 to 71:

```python
def evaluate_thumbnails(
    load: LoadModel,
    seconds_per_photo: float,
    burst: BurstProfile,
    requirement: ThumbnailRequirement,
    scenario: ThumbnailScenario,
    horizon_seconds: int | None = None,
) -> ThumbnailResult:
    """Run one scenario: pass when the pool keeps up with the average and the burst wait is within the target."""
    stage = Stage(scenario.workers, seconds_per_photo)
    horizon = horizon_seconds if horizon_seconds is not None else int(load.weekend_seconds)
    samples = simulate_waits(burst.rates(horizon), stage.capacity)
    wait = percentile_wait(samples, requirement.percentile)
    passed = stage.capacity >= load.average_rate and wait <= requirement.seconds
    return ThumbnailResult(
        scenario=scenario,
        capacity=stage.capacity,
        average_rate=load.average_rate,
        peak_rate=burst.peak_rate,
        workers_for_peak=workers_needed(burst.peak_rate, seconds_per_photo),
        percentile=requirement.percentile,
        wait_at_percentile=wait,
        passed=passed,
    )
```

> **In plain words.** `A if test else B` is a **conditional expression**: its value is A when the test is true, otherwise B.
> **In plain words.** `A | B` in a type hint means "either A or B". `X | None` means a value that may be missing.

**Function `evaluate_thumbnails`.** Run one scenario: pass when the pool keeps up with the average and the burst wait is within the target.

It takes: `load` (a `LoadModel`); `seconds_per_photo` (a `float`); `burst` (a `BurstProfile`); `requirement` (a `ThumbnailRequirement`); `scenario` (a `ThumbnailScenario`); `horizon_seconds` (a `int | None`), default `None`.

It gives back a `ThumbnailResult`.

Step by step:

- Stores the result of calling `Stage(scenario.workers, seconds_per_photo)` in `stage`.
- Stores `horizon_seconds` if `horizon_seconds` is not the same object as `None`, otherwise `int(load.weekend_seconds)` in `horizon`.
- Stores the result of calling `simulate_waits(burst.rates(horizon), stage.capacity)` in `samples`.
- Stores the result of calling `percentile_wait(samples, requirement.percentile)` in `wait`.
- Stores whether `stage.capacity` is at least `load.average_rate` and `wait` is at most `requirement.seconds` in `passed`.
- Gives back the result of calling `ThumbnailResult(scenario=scenario, capacity=stage.capacity, average_rate=load.average_rat…`.

`src/design_review/domain/fitness.py` lines 74 to 80:

```python
@dataclass(frozen=True)
class DurabilityScenario:
    """One write order to try, and the verdict the review expects for it."""

    name: str
    order: tuple[str, ...]
    expect_pass: bool
```

> **In plain words.** `obj[key]` looks a value up by key or position.
> **In plain words.** A **tuple** `(a, b)` is a fixed list of values that cannot be changed.

**Class `DurabilityScenario`**. One write order to try, and the verdict the review expects for it. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `name`: a `str`.
- Field `order`: a `tuple[str, ...]`.
- Field `expect_pass`: a `bool`.

`src/design_review/domain/fitness.py` lines 83 to 93:

```python
@dataclass(frozen=True)
class DurabilityVerdict:
    """The crash-point result with the expectation."""

    scenario: DurabilityScenario
    result: DurabilityResult

    @property
    def as_expected(self) -> bool:
        """True when the verdict is the one the review recorded for this order."""
        return self.result.holds is self.scenario.expect_pass
```

**Class `DurabilityVerdict`**. The crash-point result with the expectation. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `scenario`: a `DurabilityScenario`.
- Field `result`: a `DurabilityResult`.

Its methods, in order:

**Method `as_expected` of class `DurabilityVerdict`.** True when the verdict is the one the review recorded for this order.

It gives back a `bool`.

Decorators: `@property`.

Step by step:

- Gives back whether `self.result.holds` is the same object as `self.scenario.expect_pass`.

`src/design_review/domain/fitness.py` lines 96 to 98:

```python
def evaluate_durability(scenario: DurabilityScenario) -> DurabilityVerdict:
    """Run one write order through the crash-point check."""
    return DurabilityVerdict(scenario, check_write_order(scenario.order))
```

**Function `evaluate_durability`.** Run one write order through the crash-point check.

It takes: `scenario` (a `DurabilityScenario`).

It gives back a `DurabilityVerdict`.

Step by step:

- Gives back the result of calling `DurabilityVerdict(scenario, check_write_order(scenario.order))`.

`src/design_review/domain/fitness.py` lines 101 to 110:

```python
@dataclass(frozen=True)
class FitnessModel:
    """Everything the fitness functions need, loaded from `model/uploads.toml`."""

    load: LoadModel
    seconds_per_photo: float
    burst: BurstProfile
    requirement: ThumbnailRequirement
    thumbnails: tuple[ThumbnailScenario, ...]
    durability: tuple[DurabilityScenario, ...]
```

**Class `FitnessModel`**. Everything the fitness functions need, loaded from `model/uploads.toml`. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `load`: a `LoadModel`.
- Field `seconds_per_photo`: a `float`.
- Field `burst`: a `BurstProfile`.
- Field `requirement`: a `ThumbnailRequirement`.
- Field `thumbnails`: a `tuple[ThumbnailScenario, ...]`.
- Field `durability`: a `tuple[DurabilityScenario, ...]`.

`src/design_review/domain/fitness.py` lines 113 to 123:

```python
@dataclass(frozen=True)
class FitnessReport:
    """Every scenario's result. The report is `ok` when each scenario gave the verdict the review expected."""

    thumbnails: tuple[ThumbnailResult, ...]
    durability: tuple[DurabilityVerdict, ...]

    @property
    def ok(self) -> bool:
        """True when no scenario surprised the review."""
        return all(item.as_expected for item in self.thumbnails) and all(item.as_expected for item in self.durability)
```

> **In plain words.** A **generator expression** `(x for x in items)` is like a list comprehension, but it hands out one value at a time instead of building the whole list; here it is passed straight to a function such as `tuple(...)` or `sum(...)`.

**Class `FitnessReport`**. Every scenario's result. The report is `ok` when each scenario gave the verdict the review expected. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `thumbnails`: a `tuple[ThumbnailResult, ...]`.
- Field `durability`: a `tuple[DurabilityVerdict, ...]`.

Its methods, in order:

**Method `ok` of class `FitnessReport`.** True when no scenario surprised the review.

It gives back a `bool`.

Decorators: `@property`.

Step by step:

- Gives back whether `all((item.as_expected for item in self.thumbnails))` and `all((item.as_expected for item in self.durability))`.

`src/design_review/domain/fitness.py` lines 126 to 136:

```python
def run_fitness(model: FitnessModel, horizon_seconds: int | None = None) -> FitnessReport:
    """Evaluate every scenario in the model."""
    return FitnessReport(
        thumbnails=tuple(
            evaluate_thumbnails(
                model.load, model.seconds_per_photo, model.burst, model.requirement, scenario, horizon_seconds
            )
            for scenario in model.thumbnails
        ),
        durability=tuple(evaluate_durability(scenario) for scenario in model.durability),
    )
```

**Function `run_fitness`.** Evaluate every scenario in the model.

It takes: `model` (a `FitnessModel`); `horizon_seconds` (a `int | None`), default `None`.

It gives back a `FitnessReport`.

Step by step:

- Gives back the result of calling `FitnessReport(thumbnails=tuple((evaluate_thumbnails(model.load, model.seconds_per_photo, …`.

### `src/design_review/domain/proposal.py`

`src/design_review/domain/proposal.py` lines 1 to 7:

```python
"""A design proposal: concrete enough to review."""

from __future__ import annotations

from dataclasses import dataclass

from design_review.domain.findings import Finding, error
```

> **In plain words.** A **docstring** is a text in triple quotes as the first thing in a module, class or function. Python keeps it as the thing's description, and ruff requires one on public code.
> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.
> **In plain words.** `from __future__ import annotations` makes every type hint in the file lazy text. Python no longer evaluates a hint when the file loads, so a hint may name a class defined further down.

**Module description.** A design proposal: concrete enough to review.

Imports:

- From `__future__` it takes `annotations`.
- From `dataclasses` it takes `dataclass`.
- From `design_review.domain.findings` it takes `Finding, error`.

`src/design_review/domain/proposal.py` lines 9 to 9:

```python
REQUIRED_SECTIONS = ("Overview", "Data flow", "Datastore", "External calls", "Scaling", "Failure handling", "Unsure")
```

> **In plain words.** A **tuple** `(a, b)` is a fixed list of values that cannot be changed.
> **In plain words.** A name written in CAPITAL letters is a **constant** by convention: a value set once, not changed later.

These module-level lines:

- Stores the tuple `('Overview', 'Data flow', 'Datastore', 'External calls', 'Scaling', '…` in `REQUIRED_SECTIONS`.

`src/design_review/domain/proposal.py` lines 12 to 21:

```python
@dataclass(frozen=True)
class Proposal:
    """A parsed proposal. `sections` maps a heading to its text; `diagram` is the first fenced block under Data flow."""

    path: str
    title: str
    author: str
    sections: dict[str, str]
    diagram: str
    word_count: int
```

> **In plain words.** A **class** is a blueprint for objects that bundle data with the functions that work on it. `class B(A)` means B is a kind of A and starts with everything A has.
> **In plain words.** A **type hint** such as `x: int` or `-> str` says what kind of value a name holds or a function gives back. Python does not enforce hints when the program runs; the type checker mypy reads them before.
> **In plain words.** A call such as `f(a, key=value)` passes `a` by position and `key` by name (a **keyword argument**).
> **In plain words.** `obj[key]` looks a value up by key or position.
> **In plain words.** A **dataclass** is a class that mainly holds data. `@dataclass` writes `__init__`, `__repr__` and `__eq__` for you from the annotated fields; `frozen=True` forbids changing a field after the object is created.

**Class `Proposal`**. A parsed proposal. `sections` maps a heading to its text; `diagram` is the first fenced block under Data flow. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `path`: a `str`.
- Field `title`: a `str`.
- Field `author`: a `str`.
- Field `sections`: a `dict[str, str]`.
- Field `diagram`: a `str`.
- Field `word_count`: a `int`.

`src/design_review/domain/proposal.py` lines 24 to 40:

```python
def check_proposal(proposal: Proposal, max_words: int = 1000) -> list[Finding]:
    """PRP001 to PRP004."""
    found: list[Finding] = []
    for name in REQUIRED_SECTIONS:
        if len(proposal.sections.get(name, "").split()) < 4:
            found.append(
                error("PRP001", proposal.path, f"the section '{name}' is missing or empty: a reviewer needs it")
            )
    if not any(arrow in proposal.diagram for arrow in ("-->", "->", "<--")):
        found.append(
            error("PRP002", proposal.path, "the data flow has no diagram with arrows: a review runs on a picture")
        )
    if proposal.word_count > max_words:
        found.append(error("PRP003", proposal.path, f"{proposal.word_count} words; two pages is about {max_words}"))
    if not proposal.author:
        found.append(error("PRP004", proposal.path, "name the author"))
    return found
```

> **In plain words.** A **`for` loop** repeats its steps once for each item of a collection. `range(n)` counts from 0 to n-1.
> **In plain words.** `return value` ends the function and gives the value back to whoever called it.
> **In plain words.** `==` tests equality, `is` tests that two names are the very same object (used for `None` and enum members), `in` tests membership.
> **In plain words.** A **generator expression** `(x for x in items)` is like a list comprehension, but it hands out one value at a time instead of building the whole list; here it is passed straight to a function such as `tuple(...)` or `sum(...)`.
> **In plain words.** An **f-string** `f"...{value}..."` is text with Python expressions in braces; Python replaces each by its value. `{x!r}` shows the value the way Python would write it, with quotes.

**Function `check_proposal`.** PRP001 to PRP004.

It takes: `proposal` (a `Proposal`); `max_words` (a `int`), default `1000`.

It gives back a `list[Finding]`.

Step by step:

- Declares `found` as a `list[Finding]` and stores the list `[]` in it.
- For each `name` in `REQUIRED_SECTIONS`:
  - If `len(proposal.sections.get(name, '').split())` is less than `4`:
    - Calls `found.append(error('PRP001', proposal.path, f"the section '{name}' is missing or empty: a reviewer needs it"))`.
- If not (`any((arrow in proposal.diagram for arrow in ('-->', '->', '<--')))`):
  - Calls `found.append(error('PRP002', proposal.path, 'the data flow has no diagram with arrows: a review runs on a pic…`.
- If `proposal.word_count` is more than `max_words`:
  - Calls `found.append(error('PRP003', proposal.path, f'{proposal.word_count} words; two pages is about {max_words}'))`.
- If not (`proposal.author`):
  - Calls `found.append(error('PRP004', proposal.path, 'name the author'))`.
- Gives back `found`.

### `src/design_review/domain/queue_model.py`

`src/design_review/domain/queue_model.py` lines 1 to 8:

```python
"""A fluid queue in front of a worker pool: how long a photo waits when load comes in bursts."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from design_review.domain.capacity import ModelError
```

> **In plain words.** A **docstring** is a text in triple quotes as the first thing in a module, class or function. Python keeps it as the thing's description, and ruff requires one on public code.
> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.
> **In plain words.** `from __future__ import annotations` makes every type hint in the file lazy text. Python no longer evaluates a hint when the file loads, so a hint may name a class defined further down.

**Module description.** A fluid queue in front of a worker pool: how long a photo waits when load comes in bursts.

Imports:

- From `__future__` it takes `annotations`.
- From `collections.abc` it takes `Iterator`.
- From `dataclasses` it takes `dataclass`.
- From `design_review.domain.capacity` it takes `ModelError`.

`src/design_review/domain/queue_model.py` lines 11 to 38:

```python
@dataclass(frozen=True)
class BurstProfile:
    """A steady base rate with a burst at the peak rate at the start of every window.

    The base is chosen so the long-run mean equals the average rate, so bursts do not add load on top of the facts.
    """

    average_rate: float
    peak_rate: float
    every_seconds: int
    length_seconds: int

    def __post_init__(self) -> None:
        if not 0 < self.length_seconds < self.every_seconds:
            raise ModelError("the burst must be shorter than its window")
        if self.peak_rate < self.average_rate:
            raise ModelError("the peak cannot be below the average")

    @property
    def base_rate(self) -> float:
        """Photos a second between bursts."""
        quiet = self.every_seconds - self.length_seconds
        return (self.average_rate * self.every_seconds - self.peak_rate * self.length_seconds) / quiet

    def rates(self, seconds: int) -> Iterator[float]:
        """The arrival rate for each second of the horizon."""
        for second in range(seconds):
            yield self.peak_rate if second % self.every_seconds < self.length_seconds else self.base_rate
```

> **In plain words.** A **class** is a blueprint for objects that bundle data with the functions that work on it. `class B(A)` means B is a kind of A and starts with everything A has.
> **In plain words.** A **type hint** such as `x: int` or `-> str` says what kind of value a name holds or a function gives back. Python does not enforce hints when the program runs; the type checker mypy reads them before.
> **In plain words.** A call such as `f(a, key=value)` passes `a` by position and `key` by name (a **keyword argument**).
> **In plain words.** `return value` ends the function and gives the value back to whoever called it.
> **In plain words.** A **`for` loop** repeats its steps once for each item of a collection. `range(n)` counts from 0 to n-1.
> **In plain words.** `obj[key]` looks a value up by key or position.
> **In plain words.** `raise Error(...)` stops the current function by signalling an error. `raise ... from None` hides the earlier error, so the user sees only the new, clearer message.
> **In plain words.** `==` tests equality, `is` tests that two names are the very same object (used for `None` and enum members), `in` tests membership.
> **In plain words.** `yield` makes a function a **generator**: calling it returns an iterator that hands out one value at a time and remembers where it stopped.
> **In plain words.** `A if test else B` is a **conditional expression**: its value is A when the test is true, otherwise B.
> **In plain words.** A **dataclass** is a class that mainly holds data. `@dataclass` writes `__init__`, `__repr__` and `__eq__` for you from the annotated fields; `frozen=True` forbids changing a field after the object is created.

**Class `BurstProfile`**. A steady base rate with a burst at the peak rate at the start of every window. The base is chosen so the long-run mean equals the average rate, so bursts do not add load on top of the facts. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `average_rate`: a `float`.
- Field `peak_rate`: a `float`.
- Field `every_seconds`: a `int`.
- Field `length_seconds`: a `int`.

Its methods, in order:

**Method `__post_init__` of class `BurstProfile`.**

It gives back a `None`.

Step by step:

- If not (`0` is less than `self.length_seconds` is less than `self.every_seconds`):
  - Stops here by raising `ModelError('the burst must be shorter than its window')`.
- If `self.peak_rate` is less than `self.average_rate`:
  - Stops here by raising `ModelError('the peak cannot be below the average')`.

**Method `base_rate` of class `BurstProfile`.** Photos a second between bursts.

It gives back a `float`.

Decorators: `@property`.

Step by step:

- Stores `self.every_seconds - self.length_seconds` in `quiet`.
- Gives back `(self.average_rate * self.every_seconds - self.peak_rate * self.length_seconds)…`.

**Method `rates` of class `BurstProfile`.** The arrival rate for each second of the horizon.

It takes: `seconds` (a `int`).

It gives back a `Iterator[float]`.

Step by step:

- For each `second` in the result of calling `range(seconds)`:
  - Hands out `self.peak_rate` if `second % self.every_seconds` is less than `self.length_seconds`, otherwise `self.base_rate` to the caller (`yield`).

`src/design_review/domain/queue_model.py` lines 41 to 48:

```python
def simulate_waits(rates: Iterator[float], service_rate: float) -> list[tuple[float, float]]:
    """For each second, (seconds a photo arriving then waits, photos arriving). Backlog never goes below zero."""
    backlog = 0.0
    samples: list[tuple[float, float]] = []
    for rate in rates:
        backlog = max(0.0, backlog + rate - service_rate)
        samples.append((backlog / service_rate, rate))
    return samples
```

> **In plain words.** A **tuple** `(a, b)` is a fixed list of values that cannot be changed.

**Function `simulate_waits`.** For each second, (seconds a photo arriving then waits, photos arriving). Backlog never goes below zero.

It takes: `rates` (a `Iterator[float]`); `service_rate` (a `float`).

It gives back a `list[tuple[float, float]]`.

Step by step:

- Stores the number `0.0` in `backlog`.
- Declares `samples` as a `list[tuple[float, float]]` and stores the list `[]` in it.
- For each `rate` in `rates`:
  - Stores the result of calling `max(0.0, backlog + rate - service_rate)` in `backlog`.
  - Calls `samples.append((backlog / service_rate, rate))`.
- Gives back `samples`.

`src/design_review/domain/queue_model.py` lines 51 to 62:

```python
def percentile_wait(samples: list[tuple[float, float]], percentile: float) -> float:
    """The wait that `percentile` percent of photos stay within, weighting each second by its arrivals."""
    if not 0 < percentile <= 100:
        raise ModelError("percentile must be in (0, 100]")
    total = sum(weight for _, weight in samples)
    threshold = total * percentile / 100
    seen = 0.0
    for wait, weight in sorted(samples):
        seen += weight
        if seen >= threshold:
            return wait
    return 0.0
```

> **In plain words.** A **generator expression** `(x for x in items)` is like a list comprehension, but it hands out one value at a time instead of building the whole list; here it is passed straight to a function such as `tuple(...)` or `sum(...)`.

**Function `percentile_wait`.** The wait that `percentile` percent of photos stay within, weighting each second by its arrivals.

It takes: `samples` (a `list[tuple[float, float]]`); `percentile` (a `float`).

It gives back a `float`.

Step by step:

- If not (`0` is less than `percentile` is at most `100`):
  - Stops here by raising `ModelError('percentile must be in (0, 100]')`.
- Stores the result of calling `sum((weight for _, weight in samples))` in `total`.
- Stores `total * percentile / 100` in `threshold`.
- Stores the number `0.0` in `seen`.
- For each `(wait, weight)` in the result of calling `sorted(samples)`:
  - Adds `weight` to `seen`.
  - If `seen` is at least `threshold`:
    - Gives back `wait`.
- Gives back the number `0.0`.

### `src/design_review/domain/requirements.py`

`src/design_review/domain/requirements.py` lines 1 to 8:

```python
"""Quantified non-functional requirements: each one a number and a way to check it."""

from __future__ import annotations

from dataclasses import dataclass

from design_review.domain.findings import Finding, error
from design_review.domain.text import has_figure, words
```

> **In plain words.** A **docstring** is a text in triple quotes as the first thing in a module, class or function. Python keeps it as the thing's description, and ruff requires one on public code.
> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.
> **In plain words.** `from __future__ import annotations` makes every type hint in the file lazy text. Python no longer evaluates a hint when the file loads, so a hint may name a class defined further down.

**Module description.** Quantified non-functional requirements: each one a number and a way to check it.

Imports:

- From `__future__` it takes `annotations`.
- From `dataclasses` it takes `dataclass`.
- From `design_review.domain.findings` it takes `Finding, error`.
- From `design_review.domain.text` it takes `has_figure, words`.

`src/design_review/domain/requirements.py` lines 10 to 12:

```python
ADJECTIVES = frozenset({"fast", "reliable", "scalable", "robust", "secure", "cheap", "highly", "available", "quick"})
NO_VERIFICATION = frozenset({"", "n/a", "na", "none", "tbd", "-"})
REQUIRED_CATEGORIES = ("throughput", "latency", "availability", "durability", "cost")
```

> **In plain words.** A **set** `{a, b}` holds items without duplicates; `frozenset` is a set that cannot be changed.
> **In plain words.** A **tuple** `(a, b)` is a fixed list of values that cannot be changed.
> **In plain words.** A name written in CAPITAL letters is a **constant** by convention: a value set once, not changed later.

These module-level lines:

- Stores the result of calling `frozenset({'fast', 'reliable', 'scalable', 'robust', 'secure', 'cheap', 'highly', 'availa…` in `ADJECTIVES`.
- Stores the result of calling `frozenset({'', 'n/a', 'na', 'none', 'tbd', '-'})` in `NO_VERIFICATION`.
- Stores the tuple `('throughput', 'latency', 'availability', 'durability', 'cost')` in `REQUIRED_CATEGORIES`.

`src/design_review/domain/requirements.py` lines 15 to 23:

```python
@dataclass(frozen=True)
class Requirement:
    """One requirement. `target` holds the number and its unit; `verification` says how it will be checked."""

    id: str
    category: str
    name: str
    target: str
    verification: str
```

> **In plain words.** A **class** is a blueprint for objects that bundle data with the functions that work on it. `class B(A)` means B is a kind of A and starts with everything A has.
> **In plain words.** A **type hint** such as `x: int` or `-> str` says what kind of value a name holds or a function gives back. Python does not enforce hints when the program runs; the type checker mypy reads them before.
> **In plain words.** A call such as `f(a, key=value)` passes `a` by position and `key` by name (a **keyword argument**).
> **In plain words.** A **dataclass** is a class that mainly holds data. `@dataclass` writes `__init__`, `__repr__` and `__eq__` for you from the annotated fields; `frozen=True` forbids changing a field after the object is created.

**Class `Requirement`**. One requirement. `target` holds the number and its unit; `verification` says how it will be checked. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `id`: a `str`.
- Field `category`: a `str`.
- Field `name`: a `str`.
- Field `target`: a `str`.
- Field `verification`: a `str`.

`src/design_review/domain/requirements.py` lines 26 to 36:

```python
@dataclass(frozen=True)
class RequirementSet:
    """The requirements of one system, from one document."""

    path: str
    requirements: tuple[Requirement, ...]
    required_categories: tuple[str, ...] = REQUIRED_CATEGORIES

    def by_id(self) -> dict[str, Requirement]:
        """Requirements keyed by id."""
        return {requirement.id: requirement for requirement in self.requirements}
```

> **In plain words.** `obj[key]` looks a value up by key or position.
> **In plain words.** `return value` ends the function and gives the value back to whoever called it.
> **In plain words.** A **dictionary comprehension** `{k: v for ...}` builds a dictionary with a loop written inside braces.

**Class `RequirementSet`**. The requirements of one system, from one document. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `path`: a `str`.
- Field `requirements`: a `tuple[Requirement, ...]`.
- Field `required_categories`: a `tuple[str, ...]`, default `REQUIRED_CATEGORIES`.

Its methods, in order:

**Method `by_id` of class `RequirementSet`.** Requirements keyed by id.

It gives back a `dict[str, Requirement]`.

Step by step:

- Gives back a new dictionary made by a loop (`{requirement.id: requirement for requirement in self.requirements}`).

`src/design_review/domain/requirements.py` lines 39 to 65:

```python
def check_requirements(requirement_set: RequirementSet) -> list[Finding]:
    """REQ001 to REQ004."""
    found: list[Finding] = []
    ids = [requirement.id for requirement in requirement_set.requirements]
    if len(set(ids)) != len(ids):
        found.append(error("REQ004", requirement_set.path, "two requirements share an id"))
    for requirement in requirement_set.requirements:
        subject = f"{requirement_set.path} {requirement.id}"
        if not has_figure(requirement.target):
            found.append(
                error("REQ001", subject, f"'{requirement.name}' is an adjective, not a number: {requirement.target!r}")
            )
        elif ADJECTIVES & set(words(requirement.target)) and len(words(requirement.target)) < 3:
            found.append(error("REQ001", subject, f"'{requirement.name}' has a number but reads as an adjective"))
        if requirement.verification.strip().lower() in NO_VERIFICATION:
            found.append(
                error(
                    "REQ002",
                    subject,
                    f"'{requirement.name}' has no way to be checked: a number you cannot check is a wish",
                )
            )
    present = {requirement.category for requirement in requirement_set.requirements}
    missing = [name for name in requirement_set.required_categories if name not in present]
    if missing:
        found.append(error("REQ003", requirement_set.path, f"no requirement for: {', '.join(missing)}"))
    return found
```

> **In plain words.** A **`for` loop** repeats its steps once for each item of a collection. `range(n)` counts from 0 to n-1.
> **In plain words.** A **list comprehension** `[x for x in items if test]` is a loop written inside brackets: it builds a new list from the items that pass the test.
> **In plain words.** `==` tests equality, `is` tests that two names are the very same object (used for `None` and enum members), `in` tests membership.
> **In plain words.** A **set comprehension** `{x for ...}` builds a set (a collection with no duplicates) with a loop.
> **In plain words.** An **f-string** `f"...{value}..."` is text with Python expressions in braces; Python replaces each by its value. `{x!r}` shows the value the way Python would write it, with quotes.
> **In plain words.** On sets, `a | b` is the union (everything in either) and `a & b` the intersection (what both have).

**Function `check_requirements`.** REQ001 to REQ004.

It takes: `requirement_set` (a `RequirementSet`).

It gives back a `list[Finding]`.

Step by step:

- Declares `found` as a `list[Finding]` and stores the list `[]` in it.
- Stores a new list made by a loop (`[requirement.id for requirement in requirement_set.requirements]`) in `ids`.
- If `len(set(ids))` is different from `len(ids)`:
  - Calls `found.append(error('REQ004', requirement_set.path, 'two requirements share an id'))`.
- For each `requirement` in `requirement_set.requirements`:
  - Stores a text built with values filled in (`f'{requirement_set.path} {requirement.id}'`) in `subject`.
  - If not (`has_figure(requirement.target)`):
    - Calls `found.append(error('REQ001', subject, f"'{requirement.name}' is an adjective, not a number: {requirement.targ…`.
  - Otherwise, if `ADJECTIVES & set(words(requirement.target))` and `len(words(requirement.target))` is less than `3`:
    - Calls `found.append(error('REQ001', subject, f"'{requirement.name}' has a number but reads as an adjective"))`.
  - If `requirement.verification.strip().lower()` is in `NO_VERIFICATION`:
    - Calls `found.append(error('REQ002', subject, f"'{requirement.name}' has no way to be checked: a number you cannot ch…`.
- Stores a new set made by a loop (`{requirement.category for requirement in requirement_set.requirements}`) in `present`.
- Stores a new list made by a loop (`[name for name in requirement_set.required_categories if name not in …`) in `missing`.
- If `missing`:
  - Calls `found.append(error('REQ003', requirement_set.path, f"no requirement for: {', '.join(missing)}"))`.
- Gives back `found`.

### `src/design_review/domain/review.py`

`src/design_review/domain/review.py` lines 1 to 10:

```python
"""The review record: findings tied to requirements, classified, with owners and dates."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from design_review.domain.findings import Finding, error, warning
from design_review.domain.requirements import RequirementSet
from design_review.domain.text import has_figure, words
```

> **In plain words.** A **docstring** is a text in triple quotes as the first thing in a module, class or function. Python keeps it as the thing's description, and ruff requires one on public code.
> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.
> **In plain words.** `from __future__ import annotations` makes every type hint in the file lazy text. Python no longer evaluates a hint when the file loads, so a hint may name a class defined further down.

**Module description.** The review record: findings tied to requirements, classified, with owners and dates.

Imports:

- From `__future__` it takes `annotations`.
- From `dataclasses` it takes `dataclass`.
- From `datetime` it takes `date`.
- From `design_review.domain.findings` it takes `Finding, error, warning`.
- From `design_review.domain.requirements` it takes `RequirementSet`.
- From `design_review.domain.text` it takes `has_figure, words`.

`src/design_review/domain/review.py` lines 12 to 23:

```python
CLASSES = ("must-fix", "should-fix", "taste", "withdrawn")
VERDICTS = ("meets", "might not", "doesn't")
NOT_AN_OWNER = frozenset({"", "team", "the team", "everyone", "tbd", "all", "someone"})
SECTIONS = (
    "Requirements used",
    "Assessment",
    "Findings",
    "Decisions",
    "Accepted risks",
    "Action items",
    "Disagreement",
)
```

> **In plain words.** A **tuple** `(a, b)` is a fixed list of values that cannot be changed.
> **In plain words.** A **set** `{a, b}` holds items without duplicates; `frozenset` is a set that cannot be changed.
> **In plain words.** A name written in CAPITAL letters is a **constant** by convention: a value set once, not changed later.

These module-level lines:

- Stores the tuple `('must-fix', 'should-fix', 'taste', 'withdrawn')` in `CLASSES`.
- Stores the tuple `('meets', 'might not', "doesn't")` in `VERDICTS`.
- Stores the result of calling `frozenset({'', 'team', 'the team', 'everyone', 'tbd', 'all', 'someone'})` in `NOT_AN_OWNER`.
- Stores the tuple `('Requirements used', 'Assessment', 'Findings', 'Decisions', 'Accepte…` in `SECTIONS`.

`src/design_review/domain/review.py` lines 26 to 33:

```python
@dataclass(frozen=True)
class UsedRequirement:
    """A requirement as the review cites it."""

    id: str
    name: str
    target: str
    verification: str
```

> **In plain words.** A **class** is a blueprint for objects that bundle data with the functions that work on it. `class B(A)` means B is a kind of A and starts with everything A has.
> **In plain words.** A **type hint** such as `x: int` or `-> str` says what kind of value a name holds or a function gives back. Python does not enforce hints when the program runs; the type checker mypy reads them before.
> **In plain words.** A call such as `f(a, key=value)` passes `a` by position and `key` by name (a **keyword argument**).
> **In plain words.** A **dataclass** is a class that mainly holds data. `@dataclass` writes `__init__`, `__repr__` and `__eq__` for you from the annotated fields; `frozen=True` forbids changing a field after the object is created.

**Class `UsedRequirement`**. A requirement as the review cites it. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `id`: a `str`.
- Field `name`: a `str`.
- Field `target`: a `str`.
- Field `verification`: a `str`.

`src/design_review/domain/review.py` lines 36 to 42:

```python
@dataclass(frozen=True)
class Assessment:
    """A verdict on one requirement, with the reason and any calculation."""

    requirement: str
    verdict: str
    reason: str
```

**Class `Assessment`**. A verdict on one requirement, with the reason and any calculation. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `requirement`: a `str`.
- Field `verdict`: a `str`.
- Field `reason`: a `str`.

`src/design_review/domain/review.py` lines 45 to 53:

```python
@dataclass(frozen=True)
class ReviewFinding:
    """One finding: which requirement it breaks and its class."""

    number: str
    text: str
    requirement: str
    cls: str
    note: str
```

**Class `ReviewFinding`**. One finding: which requirement it breaks and its class. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `number`: a `str`.
- Field `text`: a `str`.
- Field `requirement`: a `str`.
- Field `cls`: a `str`.
- Field `note`: a `str`.

`src/design_review/domain/review.py` lines 56 to 62:

```python
@dataclass(frozen=True)
class AcceptedRisk:
    """A risk the room accepts, with who watches it and when to look again."""

    risk: str
    owner: str
    look_again: str
```

**Class `AcceptedRisk`**. A risk the room accepts, with who watches it and when to look again. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `risk`: a `str`.
- Field `owner`: a `str`.
- Field `look_again`: a `str`.

`src/design_review/domain/review.py` lines 65 to 71:

```python
@dataclass(frozen=True)
class ActionItem:
    """Something to do, with one named owner and one date."""

    text: str
    owner: str
    due: str
```

**Class `ActionItem`**. Something to do, with one named owner and one date. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `text`: a `str`.
- Field `owner`: a `str`.
- Field `due`: a `str`.

`src/design_review/domain/review.py` lines 74 to 80:

```python
@dataclass(frozen=True)
class Disagreement:
    """A finding the author contested, the argument and how it was resolved."""

    finding: str
    author_argument: str
    outcome: str
```

**Class `Disagreement`**. A finding the author contested, the argument and how it was resolved. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `finding`: a `str`.
- Field `author_argument`: a `str`.
- Field `outcome`: a `str`.

`src/design_review/domain/review.py` lines 83 to 100:

```python
@dataclass(frozen=True)
class ReviewRecord:
    """A parsed review record."""

    path: str
    system: str
    date_text: str
    reviewers: str
    author: str
    requirements_path: str
    sections: tuple[str, ...]
    used: tuple[UsedRequirement, ...]
    assessments: tuple[Assessment, ...]
    findings: tuple[ReviewFinding, ...]
    decisions: tuple[str, ...]
    risks: tuple[AcceptedRisk, ...]
    actions: tuple[ActionItem, ...]
    disagreements: tuple[Disagreement, ...]
```

> **In plain words.** `obj[key]` looks a value up by key or position.

**Class `ReviewRecord`**. A parsed review record. Decorators: `@dataclass(frozen=True)`.

Its parts:

- Field `path`: a `str`.
- Field `system`: a `str`.
- Field `date_text`: a `str`.
- Field `reviewers`: a `str`.
- Field `author`: a `str`.
- Field `requirements_path`: a `str`.
- Field `sections`: a `tuple[str, ...]`.
- Field `used`: a `tuple[UsedRequirement, ...]`.
- Field `assessments`: a `tuple[Assessment, ...]`.
- Field `findings`: a `tuple[ReviewFinding, ...]`.
- Field `decisions`: a `tuple[str, ...]`.
- Field `risks`: a `tuple[AcceptedRisk, ...]`.
- Field `actions`: a `tuple[ActionItem, ...]`.
- Field `disagreements`: a `tuple[Disagreement, ...]`.

`src/design_review/domain/review.py` lines 103 to 108:

```python
def _is_date(text: str) -> bool:
    try:
        date.fromisoformat(text.strip())
    except ValueError:
        return False
    return True
```

> **In plain words.** A **`try` / `except` block** runs the steps under `try`. If an error of the named kind happens, Python jumps to the matching `except` steps instead of stopping the program. `finally` steps always run.
> **In plain words.** `return value` ends the function and gives the value back to whoever called it.

**Function `_is_date`.**

It takes: `text` (a `str`).

It gives back a `bool`.

Step by step:

- Tries:
  - Calls `date.fromisoformat(text.strip())`.
- If `ValueError` happens:
  - Gives back `False`.
- Gives back `True`.

`src/design_review/domain/review.py` lines 111 to 116:

```python
def check_review(review: ReviewRecord, requirement_set: RequirementSet) -> list[Finding]:
    """REV001 to REV013."""
    found: list[Finding] = []
    for rule in (_header, _requirements, _assessments, _findings, _record_parts, _disagreement):
        found.extend(rule(review, requirement_set))
    return found
```

> **In plain words.** A **`for` loop** repeats its steps once for each item of a collection. `range(n)` counts from 0 to n-1.

**Function `check_review`.** REV001 to REV013.

It takes: `review` (a `ReviewRecord`); `requirement_set` (a `RequirementSet`).

It gives back a `list[Finding]`.

Step by step:

- Declares `found` as a `list[Finding]` and stores the list `[]` in it.
- For each `rule` in the tuple `(_header, _requirements, _assessments, _findings, _record_parts, _dis…`:
  - Calls `found.extend(rule(review, requirement_set))`.
- Gives back `found`.

`src/design_review/domain/review.py` lines 119 to 135:

```python
def _header(review: ReviewRecord, _: RequirementSet) -> list[Finding]:
    found: list[Finding] = []
    if not _is_date(review.date_text):
        found.append(error("REV001", review.path, f"date must be ISO (YYYY-MM-DD), got {review.date_text!r}"))
    for label, value in (("Reviewers", review.reviewers), ("Author", review.author), ("System", review.system)):
        if not value.strip():
            found.append(error("REV001", review.path, f"'{label}' is missing"))
    missing = [name for name in SECTIONS if name not in review.sections]
    if missing:
        found.append(
            error(
                "REV013",
                review.path,
                f"sections missing: {', '.join(missing)}; someone who was not there cannot tell what was decided",
            )
        )
    return found
```

> **In plain words.** A **list comprehension** `[x for x in items if test]` is a loop written inside brackets: it builds a new list from the items that pass the test.
> **In plain words.** `==` tests equality, `is` tests that two names are the very same object (used for `None` and enum members), `in` tests membership.
> **In plain words.** An **f-string** `f"...{value}..."` is text with Python expressions in braces; Python replaces each by its value. `{x!r}` shows the value the way Python would write it, with quotes.

**Function `_header`.**

It takes: `review` (a `ReviewRecord`); `_` (a `RequirementSet`).

It gives back a `list[Finding]`.

Step by step:

- Declares `found` as a `list[Finding]` and stores the list `[]` in it.
- If not (`_is_date(review.date_text)`):
  - Calls `found.append(error('REV001', review.path, f'date must be ISO (YYYY-MM-DD), got {review.date_text!r}'))`.
- For each `(label, value)` in the tuple `(('Reviewers', review.reviewers), ('Author', review.author), ('System…`:
  - If not (`value.strip()`):
    - Calls `found.append(error('REV001', review.path, f"'{label}' is missing"))`.
- Stores a new list made by a loop (`[name for name in SECTIONS if name not in review.sections]`) in `missing`.
- If `missing`:
  - Calls `found.append(error('REV013', review.path, f"sections missing: {', '.join(missing)}; someone who was not there…`.
- Gives back `found`.

`src/design_review/domain/review.py` lines 138 to 157:

```python
def _requirements(review: ReviewRecord, requirement_set: RequirementSet) -> list[Finding]:
    found: list[Finding] = []
    known = requirement_set.by_id()
    for used in review.used:
        source = known.get(used.id)
        if source is None:
            found.append(error("REV002", review.path, f"{used.id} is not in {requirement_set.path}"))
        elif source.target.strip() != used.target.strip():
            found.append(
                error(
                    "REV002",
                    review.path,
                    f"{used.id} is {used.target!r} here but {source.target!r} in {requirement_set.path}",
                )
            )
    cited = {used.id for used in review.used}
    unused = [requirement.id for requirement in requirement_set.requirements if requirement.id not in cited]
    if unused:
        found.append(error("REV002", review.path, f"requirements not used by the review: {', '.join(unused)}"))
    return found
```

> **In plain words.** A **set comprehension** `{x for ...}` builds a set (a collection with no duplicates) with a loop.

**Function `_requirements`.**

It takes: `review` (a `ReviewRecord`); `requirement_set` (a `RequirementSet`).

It gives back a `list[Finding]`.

Step by step:

- Declares `found` as a `list[Finding]` and stores the list `[]` in it.
- Stores the result of calling `requirement_set.by_id()` in `known`.
- For each `used` in `review.used`:
  - Stores the result of calling `known.get(used.id)` in `source`.
  - If `source` is the same object as `None`:
    - Calls `found.append(error('REV002', review.path, f'{used.id} is not in {requirement_set.path}'))`.
  - Otherwise, if `source.target.strip()` is different from `used.target.strip()`:
    - Calls `found.append(error('REV002', review.path, f'{used.id} is {used.target!r} here but {source.target!r} in {requi…`.
- Stores a new set made by a loop (`{used.id for used in review.used}`) in `cited`.
- Stores a new list made by a loop (`[requirement.id for requirement in requirement_set.requirements if re…`) in `unused`.
- If `unused`:
  - Calls `found.append(error('REV002', review.path, f"requirements not used by the review: {', '.join(unused)}"))`.
- Gives back `found`.

`src/design_review/domain/review.py` lines 160 to 191:

```python
def _assessments(review: ReviewRecord, _: RequirementSet) -> list[Finding]:
    found: list[Finding] = []
    assessed = {assessment.requirement for assessment in review.assessments}
    for used in review.used:
        if used.id not in assessed:
            found.append(error("REV003", review.path, f"{used.id} has no verdict: meets, might not or doesn't"))
    for assessment in review.assessments:
        if assessment.verdict not in VERDICTS:
            found.append(
                error("REV003", review.path, f"{assessment.requirement}: verdict must be one of {', '.join(VERDICTS)}")
            )
    if not any("=" in item.reason and has_figure(item.reason) for item in review.assessments):
        found.append(
            error(
                "REV004",
                review.path,
                "no calculation shown: do at least one yourself, with the arithmetic in the reason",
            )
        )
    pointed_at = {finding.requirement for finding in review.findings} | {
        risk.risk.split(":")[0] for risk in review.risks
    }
    for assessment in review.assessments:
        if assessment.verdict != "meets" and assessment.requirement not in pointed_at:
            found.append(
                error(
                    "REV007",
                    review.path,
                    f"{assessment.requirement} {assessment.verdict}, yet no finding or accepted risk names it",
                )
            )
    return found
```

> **In plain words.** On sets, `a | b` is the union (everything in either) and `a & b` the intersection (what both have).
> **In plain words.** A **generator expression** `(x for x in items)` is like a list comprehension, but it hands out one value at a time instead of building the whole list; here it is passed straight to a function such as `tuple(...)` or `sum(...)`.

**Function `_assessments`.**

It takes: `review` (a `ReviewRecord`); `_` (a `RequirementSet`).

It gives back a `list[Finding]`.

Step by step:

- Declares `found` as a `list[Finding]` and stores the list `[]` in it.
- Stores a new set made by a loop (`{assessment.requirement for assessment in review.assessments}`) in `assessed`.
- For each `used` in `review.used`:
  - If `used.id` is not in `assessed`:
    - Calls `found.append(error('REV003', review.path, f"{used.id} has no verdict: meets, might not or doesn't"))`.
- For each `assessment` in `review.assessments`:
  - If `assessment.verdict` is not in `VERDICTS`:
    - Calls `found.append(error('REV003', review.path, f"{assessment.requirement}: verdict must be one of {', '.join(VERDI…`.
- If not (`any(('=' in item.reason and has_figure(item.reason) for item in revie…`):
  - Calls `found.append(error('REV004', review.path, 'no calculation shown: do at least one yourself, with the arithmeti…`.
- Stores `{finding.requirement for finding in review.findings} | {risk.risk.split(':')[0]…` in `pointed_at`.
- For each `assessment` in `review.assessments`:
  - If `assessment.verdict` is different from `'meets'` and `assessment.requirement` is not in `pointed_at`:
    - Calls `found.append(error('REV007', review.path, f'{assessment.requirement} {assessment.verdict}, yet no finding or …`.
- Gives back `found`.

`src/design_review/domain/review.py` lines 194 to 229:

```python
def _findings(review: ReviewRecord, _: RequirementSet) -> list[Finding]:
    found: list[Finding] = []
    cited = {used.id for used in review.used}
    for item in review.findings:
        subject = f"{review.path} finding {item.number}"
        if item.cls not in CLASSES:
            found.append(error("REV005", subject, f"class must be one of {', '.join(CLASSES)}, got {item.cls!r}"))
        if item.cls == "taste":
            if item.requirement.lower() != "none":
                found.append(
                    error("REV006", subject, "a taste finding names a requirement; if it breaks one it is not taste")
                )
            if "dropped" not in item.note.lower():
                found.append(error("REV006", subject, "say it out loud: 'taste, dropped'"))
        elif item.requirement not in cited:
            found.append(
                error(
                    "REV005",
                    subject,
                    f"points at {item.requirement!r}, which is not a requirement of this review: it is an opinion",
                )
            )
    classes = [item.cls for item in review.findings]
    if classes and all(cls == "must-fix" for cls in classes):
        found.append(
            error("REV008", review.path, "everything is must-fix: the author cannot tell the real risks from taste")
        )
    if classes and "taste" not in classes:
        found.append(
            error(
                "REV008",
                review.path,
                "no taste finding was dropped: a review with no preference given up is a bottleneck",
            )
        )
    return found
```

**Function `_findings`.**

It takes: `review` (a `ReviewRecord`); `_` (a `RequirementSet`).

It gives back a `list[Finding]`.

Step by step:

- Declares `found` as a `list[Finding]` and stores the list `[]` in it.
- Stores a new set made by a loop (`{used.id for used in review.used}`) in `cited`.
- For each `item` in `review.findings`:
  - Stores a text built with values filled in (`f'{review.path} finding {item.number}'`) in `subject`.
  - If `item.cls` is not in `CLASSES`:
    - Calls `found.append(error('REV005', subject, f"class must be one of {', '.join(CLASSES)}, got {item.cls!r}"))`.
  - If `item.cls` equals `'taste'`:
    - If `item.requirement.lower()` is different from `'none'`:
      - Calls `found.append(error('REV006', subject, 'a taste finding names a requirement; if it breaks one it is not taste'…`.
    - If `'dropped'` is not in `item.note.lower()`:
      - Calls `found.append(error('REV006', subject, "say it out loud: 'taste, dropped'"))`.
  - Otherwise, if `item.requirement` is not in `cited`:
    - Calls `found.append(error('REV005', subject, f'points at {item.requirement!r}, which is not a requirement of this re…`.
- Stores a new list made by a loop (`[item.cls for item in review.findings]`) in `classes`.
- If `classes` and `all((cls == 'must-fix' for cls in classes))`:
  - Calls `found.append(error('REV008', review.path, 'everything is must-fix: the author cannot tell the real risks from…`.
- If `classes` and `'taste'` is not in `classes`:
  - Calls `found.append(error('REV008', review.path, 'no taste finding was dropped: a review with no preference given up…`.
- Gives back `found`.

`src/design_review/domain/review.py` lines 232 to 253:

```python
def _record_parts(review: ReviewRecord, _: RequirementSet) -> list[Finding]:
    found: list[Finding] = []
    if not review.decisions:
        found.append(error("REV009", review.path, "no decisions recorded"))
    for decision in review.decisions:
        if len(words(decision)) < 4:
            found.append(error("REV009", review.path, f"a decision is a sentence with a verb, not {decision!r}"))
    for risk in review.risks:
        if risk.owner.strip().lower() in NOT_AN_OWNER or not _is_date(risk.look_again):
            found.append(
                error(
                    "REV010",
                    review.path,
                    f"accepted risk {risk.risk!r} needs a named owner and an ISO date to look again",
                )
            )
    if not review.actions:
        found.append(error("REV011", review.path, "no action items"))
    for action in review.actions:
        if action.owner.strip().lower() in NOT_AN_OWNER or not _is_date(action.due) or not action.text.strip():
            found.append(error("REV011", review.path, f"action {action.text!r} needs one named owner and one ISO date"))
    return found
```

**Function `_record_parts`.**

It takes: `review` (a `ReviewRecord`); `_` (a `RequirementSet`).

It gives back a `list[Finding]`.

Step by step:

- Declares `found` as a `list[Finding]` and stores the list `[]` in it.
- If not (`review.decisions`):
  - Calls `found.append(error('REV009', review.path, 'no decisions recorded'))`.
- For each `decision` in `review.decisions`:
  - If `len(words(decision))` is less than `4`:
    - Calls `found.append(error('REV009', review.path, f'a decision is a sentence with a verb, not {decision!r}'))`.
- For each `risk` in `review.risks`:
  - If `risk.owner.strip().lower()` is in `NOT_AN_OWNER` or not (`_is_date(risk.look_again)`):
    - Calls `found.append(error('REV010', review.path, f'accepted risk {risk.risk!r} needs a named owner and an ISO date t…`.
- If not (`review.actions`):
  - Calls `found.append(error('REV011', review.path, 'no action items'))`.
- For each `action` in `review.actions`:
  - If `action.owner.strip().lower()` is in `NOT_AN_OWNER` or not (`_is_date(action.due)`) or not (`action.text.strip()`):
    - Calls `found.append(error('REV011', review.path, f'action {action.text!r} needs one named owner and one ISO date'))`.
- Gives back `found`.

`src/design_review/domain/review.py` lines 256 to 274:

```python
def _disagreement(review: ReviewRecord, _: RequirementSet) -> list[Finding]:
    by_number = {item.number: item for item in review.findings}
    for item in review.disagreements:
        target = by_number.get(item.finding)
        if (
            target is not None
            and target.cls == "withdrawn"
            and item.outcome.lower().startswith("accepted")
            and item.author_argument.strip()
        ):
            return []
    return [
        error(
            "REV012",
            review.path,
            "no disagreement where the author's argument changed the reviewer's position "
            "(Outcome: accepted, on a finding classed 'withdrawn')",
        )
    ]
```

> **In plain words.** A **dictionary comprehension** `{k: v for ...}` builds a dictionary with a loop written inside braces.

**Function `_disagreement`.**

It takes: `review` (a `ReviewRecord`); `_` (a `RequirementSet`).

It gives back a `list[Finding]`.

Step by step:

- Stores a new dictionary made by a loop (`{item.number: item for item in review.findings}`) in `by_number`.
- For each `item` in `review.disagreements`:
  - Stores the result of calling `by_number.get(item.finding)` in `target`.
  - If `target` is not the same object as `None` and `target.cls` equals `'withdrawn'` and `item.outcome.lower().startswith('accepted')` and `item.author_argument.strip()`:
    - Gives back the list `[]`.
- Gives back the list `[error('REV012', review.path, "no disagreement where the author's arg…`.

`src/design_review/domain/review.py` lines 277 to 280:

```python
def requirement_category(requirement_set: RequirementSet, requirement_id: str) -> str | None:
    """The category of a requirement cited by a finding, if the id is known."""
    known = requirement_set.by_id().get(requirement_id)
    return known.category if known else None
```

> **In plain words.** `A | B` in a type hint means "either A or B". `X | None` means a value that may be missing.
> **In plain words.** `A if test else B` is a **conditional expression**: its value is A when the test is true, otherwise B.

**Function `requirement_category`.** The category of a requirement cited by a finding, if the id is known.

It takes: `requirement_set` (a `RequirementSet`); `requirement_id` (a `str`).

It gives back a `str | None`.

Step by step:

- Stores the result of calling `requirement_set.by_id().get(requirement_id)` in `known`.
- Gives back `known.category` if `known`, otherwise `None`.

`src/design_review/domain/review.py` lines 283 to 288:

```python
def warn_long_must_fix(review: ReviewRecord, limit: int = 3) -> list[Finding]:
    """REV014 (warning): a long must-fix list is a sign the review is blocking on too much."""
    count = sum(1 for item in review.findings if item.cls == "must-fix")
    if count > limit:
        return [warning("REV014", review.path, f"{count} must-fix findings; a good review's list is short")]
    return []
```

**Function `warn_long_must_fix`.** REV014 (warning): a long must-fix list is a sign the review is blocking on too much.

It takes: `review` (a `ReviewRecord`); `limit` (a `int`), default `3`.

It gives back a `list[Finding]`.

Step by step:

- Stores the result of calling `sum((1 for item in review.findings if item.cls == 'must-fix'))` in `count`.
- If `count` is more than `limit`:
  - Gives back the list `[warning('REV014', review.path, f"{count} must-fix findings; a good r…`.
- Gives back the list `[]`.

### `src/design_review/domain/text.py`

`src/design_review/domain/text.py` lines 1 to 5:

```python
"""Small text helpers shared by the rules."""

from __future__ import annotations

import re
```

> **In plain words.** A **docstring** is a text in triple quotes as the first thing in a module, class or function. Python keeps it as the thing's description, and ruff requires one on public code.
> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.
> **In plain words.** `from __future__ import annotations` makes every type hint in the file lazy text. Python no longer evaluates a hint when the file loads, so a hint may name a class defined further down.

**Module description.** Small text helpers shared by the rules.

Imports:

- From `__future__` it takes `annotations`.
- It imports module `re`.

`src/design_review/domain/text.py` lines 7 to 7:

```python
_WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9'-]*")
```

> **In plain words.** A **regular expression** is a short pattern for text, such as `^## (.+)$` for "a line starting with ## ". `re.compile` prepares it once; `.match` tries it at the start of a string and returns a match object or `None`.
> **In plain words.** A name written in CAPITAL letters is a **constant** by convention: a value set once, not changed later.

These module-level lines:

- Stores the result of calling `re.compile("[A-Za-z0-9][A-Za-z0-9'-]*")` in `_WORD`.

`src/design_review/domain/text.py` lines 10 to 12:

```python
def words(text: str) -> list[str]:
    """The words of a text, lower-cased."""
    return [match.lower() for match in _WORD.findall(text)]
```

> **In plain words.** A **type hint** such as `x: int` or `-> str` says what kind of value a name holds or a function gives back. Python does not enforce hints when the program runs; the type checker mypy reads them before.
> **In plain words.** `return value` ends the function and gives the value back to whoever called it.
> **In plain words.** `obj[key]` looks a value up by key or position.
> **In plain words.** A **list comprehension** `[x for x in items if test]` is a loop written inside brackets: it builds a new list from the items that pass the test.

**Function `words`.** The words of a text, lower-cased.

It takes: `text` (a `str`).

It gives back a `list[str]`.

Step by step:

- Gives back a new list made by a loop (`[match.lower() for match in _WORD.findall(text)]`).

`src/design_review/domain/text.py` lines 15 to 17:

```python
def has_figure(text: str) -> bool:
    """True when the text holds at least one digit: a number, a date or a count."""
    return any(character.isdigit() for character in text)
```

> **In plain words.** A **generator expression** `(x for x in items)` is like a list comprehension, but it hands out one value at a time instead of building the whole list; here it is passed straight to a function such as `tuple(...)` or `sum(...)`.

**Function `has_figure`.** True when the text holds at least one digit: a number, a date or a count.

It takes: `text` (a `str`).

It gives back a `bool`.

Step by step:

- Gives back the result of calling `any((character.isdigit() for character in text))`.

## Try it yourself

```bash
.venv/bin/python -c "import design_review.domain.capacity; print(design_review.domain.capacity.__doc__)"
```
Prints the module's description: `The arithmetic of the review: how much load arrives, and how much one stage can carry.`

```bash
.venv/bin/python -c "import design_review.domain.checklist; print(design_review.domain.checklist.__doc__)"
```
Prints the module's description: `The design checklist an author applies before the review, built from the findings reviews repeat.`

```bash
.venv/bin/mypy
```
Checks the whole project (the `files` setting in `pyproject.toml`), these files included. Prints `Success: no issues found in 38 source files`.

```bash
.venv/bin/ruff check src/design_review/__init__.py src/design_review/domain/__init__.py src/design_review/domain/capacity.py src/design_review/domain/checklist.py src/design_review/domain/durability.py src/design_review/domain/findings.py
```
Prints `All checks passed!`.

```bash
grep -c "^def \|^class \|    def " src/design_review/domain/capacity.py
```
Counts the functions, methods and classes in `src/design_review/domain/capacity.py`.

## Mistakes people make

- Reading a file or printing from a domain function. Input and output belong to the outer layers.
- Importing a framework (Flask, psycopg) here; the contract in `pyproject.toml` forbids it.
- Changing a value in place. The domain uses frozen values, so a change makes a new value.

## Check yourself

1. What is `ModelError` for?
   **Answer:** A model value is out of range.
2. What is `LoadModel` for?
   **Answer:** The facts the lesson gives: listings a week, photos per listing, and when they arrive.
3. What is `Stage` for?
   **Answer:** A worker pool: how many workers and how long one worker takes for one photo (all sizes).
4. What is `workers_needed` for?
   **Answer:** The smallest pool that keeps up with a rate of photos a second.
5. What is `ChecklistItem` for?
   **Answer:** One question, tagged with the requirement category it protects.

## Further reading

- Python 3.12 tutorial, classes: <https://docs.python.org/3.12/tutorial/classes.html>
- Python 3.12 language reference: <https://docs.python.org/3.12/reference/>
- Type hints: <https://docs.python.org/3.12/library/typing.html>
