# The tests (domain)

## What it is

The pytest tests in `tests/unit/domain`. Each function whose name starts with `test_` is one check; pytest finds and runs them. (Every term is explained where it first appears in the walkthrough below.)

## Why this repository uses it

The tests turn every rule, adapter and command of this repository into something that can fail. A rule without a test is only a claim.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `tests/unit/domain/test_capacity_and_queue.py` | 53 lines.  |
| `tests/unit/domain/test_documents_rules.py` | 180 lines.  |
| `tests/unit/domain/test_durability_and_fitness.py` | 74 lines.  |

## How it works underneath

pytest imports each `test_*.py` file, builds the fixtures a test asks for by parameter name, runs the function, and counts it as passed when no `assert` fails and nothing raises. A fixture such as `tmp_path` or `monkeypatch` is prepared fresh for each test, so tests do not affect each other.

## Walkthrough of this repository's use

### `tests/unit/domain/test_capacity_and_queue.py`

`tests/unit/domain/test_capacity_and_queue.py` lines 1 to 4:

```python
import pytest

from design_review.domain.capacity import LoadModel, ModelError, Stage, workers_needed
from design_review.domain.queue_model import BurstProfile, percentile_wait, simulate_waits
```

> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.

Imports:

- It imports module `pytest`.
- From `design_review.domain.capacity` it takes `LoadModel, ModelError, Stage, workers_needed`.
- From `design_review.domain.queue_model` it takes `BurstProfile, percentile_wait, simulate_waits`.

`tests/unit/domain/test_capacity_and_queue.py` lines 6 to 6:

```python
LOAD = LoadModel(120_000, 10, 0.70, 2.5, 40)
```

> **In plain words.** A name written in CAPITAL letters is a **constant** by convention: a value set once, not changed later.

These module-level lines:

- Stores the result of calling `LoadModel(120000, 10, 0.7, 2.5, 40)` in `LOAD`.

`tests/unit/domain/test_capacity_and_queue.py` lines 9 to 13:

```python
def test_the_lessons_load_numbers():
    assert LOAD.photos_per_week == 1_200_000
    assert LOAD.weekend_seconds == 216_000
    assert LOAD.average_rate == pytest.approx(3.889, abs=0.001)
    assert LOAD.peak_ratio == pytest.approx(10.29, abs=0.01)
```

> **In plain words.** `assert condition` checks that something is true. In a test, a false condition fails the test and pytest shows both sides of the comparison.
> **In plain words.** `==` tests equality, `is` tests that two names are the very same object (used for `None` and enum members), `in` tests membership.
> **In plain words.** A call such as `f(a, key=value)` passes `a` by position and `key` by name (a **keyword argument**).
> **In plain words.** A **test** is a function whose name starts with `test_`. pytest finds it, runs it, and reports a pass when no `assert` fails and nothing raises.

**Test `test_the_lessons_load_numbers`** checks: the lessons load numbers.

Step by step:

- Checks that `LOAD.photos_per_week` equals `1200000`; if not, the test fails.
- Checks that `LOAD.weekend_seconds` equals `216000`; if not, the test fails.
- Checks that `LOAD.average_rate` equals `pytest.approx(3.889, abs=0.001)`; if not, the test fails.
- Checks that `LOAD.peak_ratio` equals `pytest.approx(10.29, abs=0.01)`; if not, the test fails.

`tests/unit/domain/test_capacity_and_queue.py` lines 16 to 18:

```python
def test_one_worker_does_half_a_photo_a_second():
    assert Stage(1, 2.0).capacity == 0.5
    assert Stage(80, 2.0).capacity == 40
```

**Test `test_one_worker_does_half_a_photo_a_second`** checks: one worker does half a photo a second.

Step by step:

- Checks that `Stage(1, 2.0).capacity` equals `0.5`; if not, the test fails.
- Checks that `Stage(80, 2.0).capacity` equals `40`; if not, the test fails.

`tests/unit/domain/test_capacity_and_queue.py` lines 21 to 23:

```python
def test_workers_needed_rounds_up():
    assert workers_needed(40, 2.0) == 80
    assert workers_needed(3.9, 2.0) == 8
```

**Test `test_workers_needed_rounds_up`** checks: workers needed rounds up.

Step by step:

- Checks that `workers_needed(40, 2.0)` equals `80`; if not, the test fails.
- Checks that `workers_needed(3.9, 2.0)` equals `8`; if not, the test fails.

`tests/unit/domain/test_capacity_and_queue.py` lines 26 to 39:

```python
@pytest.mark.parametrize(
    "build",
    [
        lambda: LoadModel(0, 10, 0.7, 2.5, 40),
        lambda: LoadModel(1, 1, 0.0, 2.5, 40),
        lambda: LoadModel(1, 1, 1.5, 2.5, 40),
        lambda: LoadModel(1, 1, 0.5, 2.5, 0),
        lambda: Stage(0, 2.0),
        lambda: Stage(1, 0.0),
    ],
)
def test_impossible_values_are_rejected(build):
    with pytest.raises(ModelError):
        build()
```

> **In plain words.** `@pytest.mark.parametrize` runs the same test function once for each row of data given; a failure names the row that broke.
> **In plain words.** `with pytest.raises(Error):` expects the code inside to raise that error; the test fails if it does not.
> **In plain words.** A **lambda** is a small function written in one line: `lambda x: x + 1`.

**Test `test_impossible_values_are_rejected`** checks: impossible values are rejected.

It takes: `build`.

Decorators: `@pytest.mark.parametrize('build', [lambda: LoadModel(0, 10, 0.7, 2.5, …`.

Step by step:

- Expects the steps inside to raise the error in `pytest.raises(ModelError)`:
  - Calls `build()`.

`tests/unit/domain/test_capacity_and_queue.py` lines 42 to 47:

```python
def test_the_burst_profile_keeps_the_mean_at_the_average():
    profile = BurstProfile(LOAD.average_rate, 40, 3600, 60)
    rates = list(profile.rates(3600))
    assert sum(rates) / len(rates) == pytest.approx(LOAD.average_rate)
    assert rates[0] == 40
    assert rates[100] == pytest.approx(profile.base_rate)
```

> **In plain words.** `obj[key]` looks a value up by key or position.

**Test `test_the_burst_profile_keeps_the_mean_at_the_average`** checks: the burst profile keeps the mean at the average.

Step by step:

- Stores the result of calling `BurstProfile(LOAD.average_rate, 40, 3600, 60)` in `profile`.
- Stores the result of calling `list(profile.rates(3600))` in `rates`.
- Checks that `sum(rates) / len(rates)` equals `pytest.approx(LOAD.average_rate)`; if not, the test fails.
- Checks that `rates[0]` equals `40`; if not, the test fails.
- Checks that `rates[100]` equals `pytest.approx(profile.base_rate)`; if not, the test fails.

`tests/unit/domain/test_capacity_and_queue.py` lines 50 to 53:

```python
@pytest.mark.parametrize("args", [(3.9, 40, 60, 60), (3.9, 40, 60, 0), (50, 40, 3600, 60)])
def test_bad_burst_profiles_are_rejected(args):
    with pytest.raises(ModelError):
        BurstProfile(*args)
```

> **In plain words.** A **tuple** `(a, b)` is a fixed list of values that cannot be changed.
> **In plain words.** `*items` **unpacks** a sequence into separate values; `**options` does the same for a dictionary's keys and values.

**Test `test_bad_burst_profiles_are_rejected`** checks: bad burst profiles are rejected.

It takes: `args`.

Decorators: `@pytest.mark.parametrize('args', [(3.9, 40, 60, 60), (3.9, 40, 60, 0),…`.

Step by step:

- Expects the steps inside to raise the error in `pytest.raises(ModelError)`:
  - Calls `BurstProfile(*args)`.

`tests/unit/domain/test_capacity_and_queue.py` lines 56 to 58:

```python
def test_a_pool_that_keeps_up_never_queues():
    samples = simulate_waits(iter([3.0] * 10), service_rate=4.0)
    assert all(wait == 0 for wait, _ in samples)
```

> **In plain words.** A **generator expression** `(x for x in items)` is like a list comprehension, but it hands out one value at a time instead of building the whole list; here it is passed straight to a function such as `tuple(...)` or `sum(...)`.

**Test `test_a_pool_that_keeps_up_never_queues`** checks: a pool that keeps up never queues.

Step by step:

- Stores the result of calling `simulate_waits(iter([3.0] * 10), service_rate=4.0)` in `samples`.
- Checks that `all((wait == 0 for wait, _ in samples))`; if not, the test fails.

`tests/unit/domain/test_capacity_and_queue.py` lines 61 to 63:

```python
def test_a_pool_that_falls_behind_queues_longer_each_second():
    samples = simulate_waits(iter([5.0] * 4), service_rate=4.0)
    assert [wait for wait, _ in samples] == [0.25, 0.5, 0.75, 1.0]
```

> **In plain words.** A **list comprehension** `[x for x in items if test]` is a loop written inside brackets: it builds a new list from the items that pass the test.

**Test `test_a_pool_that_falls_behind_queues_longer_each_second`** checks: a pool that falls behind queues longer each second.

Step by step:

- Stores the result of calling `simulate_waits(iter([5.0] * 4), service_rate=4.0)` in `samples`.
- Checks that `[wait for wait, _ in samples]` equals `[0.25, 0.5, 0.75, 1.0]`; if not, the test fails.

`tests/unit/domain/test_capacity_and_queue.py` lines 66 to 70:

```python
def test_the_percentile_weights_seconds_by_their_arrivals():
    samples = [(0.0, 90.0), (50.0, 10.0)]
    assert percentile_wait(samples, 90) == 0.0
    assert percentile_wait(samples, 95) == 50.0
    assert percentile_wait([], 95) == 0.0
```

**Test `test_the_percentile_weights_seconds_by_their_arrivals`** checks: the percentile weights seconds by their arrivals.

Step by step:

- Stores the list `[(0.0, 90.0), (50.0, 10.0)]` in `samples`.
- Checks that `percentile_wait(samples, 90)` equals `0.0`; if not, the test fails.
- Checks that `percentile_wait(samples, 95)` equals `50.0`; if not, the test fails.
- Checks that `percentile_wait([], 95)` equals `0.0`; if not, the test fails.

`tests/unit/domain/test_capacity_and_queue.py` lines 73 to 75:

```python
def test_a_percentile_outside_the_range_is_rejected():
    with pytest.raises(ModelError):
        percentile_wait([(1.0, 1.0)], 0)
```

**Test `test_a_percentile_outside_the_range_is_rejected`** checks: a percentile outside the range is rejected.

Step by step:

- Expects the steps inside to raise the error in `pytest.raises(ModelError)`:
  - Calls `percentile_wait([(1.0, 1.0)], 0)`.

### `tests/unit/domain/test_documents_rules.py`

`tests/unit/domain/test_documents_rules.py` lines 1 to 16:

```python
from dataclasses import replace

from design_review.domain.checklist import Checklist, ChecklistItem, check_checklist
from design_review.domain.proposal import Proposal, check_proposal
from design_review.domain.requirements import Requirement, RequirementSet, check_requirements
from design_review.domain.review import (
    AcceptedRisk,
    ActionItem,
    Assessment,
    Disagreement,
    ReviewFinding,
    ReviewRecord,
    UsedRequirement,
    check_review,
    warn_long_must_fix,
)
```

> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.

Imports:

- From `dataclasses` it takes `replace`.
- From `design_review.domain.checklist` it takes `Checklist, ChecklistItem, check_checklist`.
- From `design_review.domain.proposal` it takes `Proposal, check_proposal`.
- From `design_review.domain.requirements` it takes `Requirement, RequirementSet, check_requirements`.
- From `design_review.domain.review` it takes `AcceptedRisk, ActionItem, Assessment, Disagreement, ReviewFinding, ReviewRecord, UsedRequirement, check_review, warn_long_must_fix`.

`tests/unit/domain/test_documents_rules.py` lines 18 to 27:

```python
SET = RequirementSet(
    "docs/requirements/x.md",
    (
        Requirement("R1", "throughput", "Peak", "40 uploads a second", "load test"),
        Requirement("R2", "latency", "p99", "under 3 seconds", "dashboard"),
        Requirement("R3", "availability", "Uptime", "99.9 percent a month", "uptime check"),
        Requirement("R4", "durability", "Loss", "0 uploads lost", "restore test"),
        Requirement("R5", "cost", "Cost", "2,000 dollars a month", "cloud bill"),
    ),
)
```

> **In plain words.** A **tuple** `(a, b)` is a fixed list of values that cannot be changed.
> **In plain words.** A name written in CAPITAL letters is a **constant** by convention: a value set once, not changed later.

These module-level lines:

- Stores the result of calling `RequirementSet('docs/requirements/x.md', (Requirement('R1', 'throughput', 'Peak', '40 upl…` in `SET`.

`tests/unit/domain/test_documents_rules.py` lines 30 to 31:

```python
def req_codes(requirement_set):
    return {f.code for f in check_requirements(requirement_set)}
```

> **In plain words.** `return value` ends the function and gives the value back to whoever called it.
> **In plain words.** A **set comprehension** `{x for ...}` builds a set (a collection with no duplicates) with a loop.

**Function `req_codes`.**

It takes: `requirement_set`.

Step by step:

- Gives back a new set made by a loop (`{f.code for f in check_requirements(requirement_set)}`).

`tests/unit/domain/test_documents_rules.py` lines 34 to 35:

```python
def test_good_requirements_pass():
    assert check_requirements(SET) == []
```

> **In plain words.** `assert condition` checks that something is true. In a test, a false condition fails the test and pytest shows both sides of the comparison.
> **In plain words.** `==` tests equality, `is` tests that two names are the very same object (used for `None` and enum members), `in` tests membership.
> **In plain words.** A **test** is a function whose name starts with `test_`. pytest finds it, runs it, and reports a pass when no `assert` fails and nothing raises.

**Test `test_good_requirements_pass`** checks: good requirements pass.

Step by step:

- Checks that `check_requirements(SET)` equals `[]`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 38 to 40:

```python
def test_an_adjective_is_not_a_requirement():
    broken = replace(SET, requirements=(replace(SET.requirements[0], target="fast"), *SET.requirements[1:]))
    assert "REQ001" in req_codes(broken)
```

> **In plain words.** A call such as `f(a, key=value)` passes `a` by position and `key` by name (a **keyword argument**).
> **In plain words.** `*items` **unpacks** a sequence into separate values; `**options` does the same for a dictionary's keys and values.
> **In plain words.** `obj[key]` looks a value up by key or position.
> **In plain words.** A **slice** such as `text[:7]` or `items[1:]` takes part of a sequence: `[:7]` the first seven items, `[1:]` everything after the first.

**Test `test_an_adjective_is_not_a_requirement`** checks: an adjective is not a requirement.

Step by step:

- Stores the result of calling `replace(SET, requirements=(replace(SET.requirements[0], target='fast'), *SET.requirements…` in `broken`.
- Checks that `'REQ001'` is in `req_codes(broken)`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 43 to 45:

```python
def test_a_number_that_reads_as_an_adjective_is_caught():
    broken = replace(SET, requirements=(replace(SET.requirements[0], target="highly 1"), *SET.requirements[1:]))
    assert "REQ001" in req_codes(broken)
```

**Test `test_a_number_that_reads_as_an_adjective_is_caught`** checks: a number that reads as an adjective is caught.

Step by step:

- Stores the result of calling `replace(SET, requirements=(replace(SET.requirements[0], target='highly 1'), *SET.requirem…` in `broken`.
- Checks that `'REQ001'` is in `req_codes(broken)`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 48 to 50:

```python
def test_a_requirement_nobody_can_check_is_a_wish():
    broken = replace(SET, requirements=(replace(SET.requirements[0], verification="TBD"), *SET.requirements[1:]))
    assert "REQ002" in req_codes(broken)
```

**Test `test_a_requirement_nobody_can_check_is_a_wish`** checks: a requirement nobody can check is a wish.

Step by step:

- Stores the result of calling `replace(SET, requirements=(replace(SET.requirements[0], verification='TBD'), *SET.require…` in `broken`.
- Checks that `'REQ002'` is in `req_codes(broken)`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 53 to 54:

```python
def test_the_five_categories_must_be_covered():
    assert "REQ003" in req_codes(replace(SET, requirements=SET.requirements[:3]))
```

**Test `test_the_five_categories_must_be_covered`** checks: the five categories must be covered.

Step by step:

- Checks that `'REQ003'` is in `req_codes(replace(SET, requirements=SET.requireme…`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 57 to 60:

```python
def test_ids_must_be_unique():
    assert "REQ004" in req_codes(
        replace(SET, requirements=(SET.requirements[0], SET.requirements[0], *SET.requirements[1:]))
    )
```

**Test `test_ids_must_be_unique`** checks: ids must be unique.

Step by step:

- Checks that `'REQ004'` is in `req_codes(replace(SET, requirements=(SET.requirem…`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 63 to 65:

```python
NAMES = ("Overview", "Data flow", "Datastore", "External calls", "Scaling", "Failure handling", "Unsure")
SECTIONS = dict.fromkeys(NAMES, "enough words in this section")
PROPOSAL = Proposal("p.md", "T", "A", SECTIONS, "a --> b", 400)
```

These module-level lines:

- Stores the tuple `('Overview', 'Data flow', 'Datastore', 'External calls', 'Scaling', '…` in `NAMES`.
- Stores the result of calling `dict.fromkeys(NAMES, 'enough words in this section')` in `SECTIONS`.
- Stores the result of calling `Proposal('p.md', 'T', 'A', SECTIONS, 'a --> b', 400)` in `PROPOSAL`.

`tests/unit/domain/test_documents_rules.py` lines 68 to 69:

```python
def test_a_concrete_proposal_passes():
    assert check_proposal(PROPOSAL) == []
```

**Test `test_a_concrete_proposal_passes`** checks: a concrete proposal passes.

Step by step:

- Checks that `check_proposal(PROPOSAL)` equals `[]`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 72 to 74:

```python
def test_a_proposal_must_name_its_datastore_and_the_rest():
    sections = {**SECTIONS, "Datastore": ""}
    assert [f.code for f in check_proposal(replace(PROPOSAL, sections=sections))] == ["PRP001"]
```

> **In plain words.** A **dictionary** `{key: value}` maps keys to values.
> **In plain words.** A **list comprehension** `[x for x in items if test]` is a loop written inside brackets: it builds a new list from the items that pass the test.

**Test `test_a_proposal_must_name_its_datastore_and_the_rest`** checks: a proposal must name its datastore and the rest.

Step by step:

- Stores the dictionary `{**SECTIONS, 'Datastore': ''}` in `sections`.
- Checks that `[f.code for f in check_proposal(replace(PROPOSAL,…` equals `['PRP001']`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 77 to 78:

```python
def test_a_proposal_needs_a_diagram_with_arrows():
    assert [f.code for f in check_proposal(replace(PROPOSAL, diagram="boxes"))] == ["PRP002"]
```

**Test `test_a_proposal_needs_a_diagram_with_arrows`** checks: a proposal needs a diagram with arrows.

Step by step:

- Checks that `[f.code for f in check_proposal(replace(PROPOSAL,…` equals `['PRP002']`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 81 to 83:

```python
def test_a_proposal_longer_than_two_pages_is_reported():
    assert [f.code for f in check_proposal(replace(PROPOSAL, word_count=1001))] == ["PRP003"]
    assert check_proposal(replace(PROPOSAL, word_count=1001), max_words=2000) == []
```

**Test `test_a_proposal_longer_than_two_pages_is_reported`** checks: a proposal longer than two pages is reported.

Step by step:

- Checks that `[f.code for f in check_proposal(replace(PROPOSAL,…` equals `['PRP003']`; if not, the test fails.
- Checks that `check_proposal(replace(PROPOSAL, word_count=1001)…` equals `[]`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 86 to 87:

```python
def test_a_proposal_needs_an_author():
    assert [f.code for f in check_proposal(replace(PROPOSAL, author=""))] == ["PRP004"]
```

**Test `test_a_proposal_needs_an_author`** checks: a proposal needs an author.

Step by step:

- Checks that `[f.code for f in check_proposal(replace(PROPOSAL,…` equals `['PRP004']`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 90 to 125:

```python
def good_review() -> ReviewRecord:
    return ReviewRecord(
        path="docs/reviews/review-a.md",
        system="s",
        date_text="2026-10-22",
        reviewers="Reviewer",
        author="Author",
        requirements_path=SET.path,
        sections=(
            "Requirements used",
            "Assessment",
            "Findings",
            "Decisions",
            "Accepted risks",
            "Action items",
            "Disagreement",
        ),
        used=tuple(UsedRequirement(r.id, r.name, r.target, r.verification) for r in SET.requirements),
        assessments=(
            Assessment("R1", "doesn't", "1 / 2 s = 0.5 a second"),
            Assessment("R2", "meets", "fine"),
            Assessment("R3", "might not", "single points"),
            Assessment("R4", "meets", "fine"),
            Assessment("R5", "meets", "fine"),
        ),
        findings=(
            ReviewFinding("1", "one worker", "R1", "must-fix", ""),
            ReviewFinding("2", "single point", "R3", "should-fix", ""),
            ReviewFinding("3", "one retry", "R1", "withdrawn", ""),
            ReviewFinding("4", "another CDN", "none", "taste", "dropped"),
        ),
        decisions=("Workers will scale on queue age.",),
        risks=(AcceptedRisk("R3: one database", "Team lead", "2026-12-01"),),
        actions=(ActionItem("add a metric", "Team lead", "2026-10-29"),),
        disagreements=(Disagreement("3", "failures are rare", "accepted. I changed my position."),),
    )
```

> **In plain words.** A **type hint** such as `x: int` or `-> str` says what kind of value a name holds or a function gives back. Python does not enforce hints when the program runs; the type checker mypy reads them before.
> **In plain words.** A **generator expression** `(x for x in items)` is like a list comprehension, but it hands out one value at a time instead of building the whole list; here it is passed straight to a function such as `tuple(...)` or `sum(...)`.

**Function `good_review`.**

It gives back a `ReviewRecord`.

Step by step:

- Gives back the result of calling `ReviewRecord(path='docs/reviews/review-a.md', system='s', date_text='2026-10-22', reviewe…`.

`tests/unit/domain/test_documents_rules.py` lines 128 to 129:

```python
def rev_codes(review):
    return {f.code for f in check_review(review, SET)}
```

**Function `rev_codes`.**

It takes: `review`.

Step by step:

- Gives back a new set made by a loop (`{f.code for f in check_review(review, SET)}`).

`tests/unit/domain/test_documents_rules.py` lines 132 to 133:

```python
def test_a_good_review_passes():
    assert check_review(good_review(), SET) == []
```

**Test `test_a_good_review_passes`** checks: a good review passes.

Step by step:

- Checks that `check_review(good_review(), SET)` equals `[]`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 136 to 139:

```python
def test_a_review_needs_its_header_and_sections():
    assert "REV001" in rev_codes(replace(good_review(), date_text="soon"))
    assert "REV001" in rev_codes(replace(good_review(), author=""))
    assert "REV013" in rev_codes(replace(good_review(), sections=("Findings",)))
```

**Test `test_a_review_needs_its_header_and_sections`** checks: a review needs its header and sections.

Step by step:

- Checks that `'REV001'` is in `rev_codes(replace(good_review(), date_text='soon'…`; if not, the test fails.
- Checks that `'REV001'` is in `rev_codes(replace(good_review(), author=''))`; if not, the test fails.
- Checks that `'REV013'` is in `rev_codes(replace(good_review(), sections=('Findi…`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 142 to 147:

```python
def test_requirements_must_match_the_requirements_document():
    review = good_review()
    changed = replace(review, used=(replace(review.used[0], target="10 uploads a second"), *review.used[1:]))
    assert "REV002" in rev_codes(changed)
    assert "REV002" in rev_codes(replace(review, used=(*review.used[:4], replace(review.used[4], id="R9"))))
    assert "REV002" in rev_codes(replace(review, used=review.used[:4]))
```

**Test `test_requirements_must_match_the_requirements_document`** checks: requirements must match the requirements document.

Step by step:

- Stores the result of calling `good_review()` in `review`.
- Stores the result of calling `replace(review, used=(replace(review.used[0], target='10 uploads a second'), *review.used…` in `changed`.
- Checks that `'REV002'` is in `rev_codes(changed)`; if not, the test fails.
- Checks that `'REV002'` is in `rev_codes(replace(review, used=(*review.used[:4],…`; if not, the test fails.
- Checks that `'REV002'` is in `rev_codes(replace(review, used=review.used[:4]))`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 150 to 155:

```python
def test_every_requirement_needs_a_verdict_from_the_list():
    review = good_review()
    assert "REV003" in rev_codes(replace(review, assessments=review.assessments[:4]))
    assert "REV003" in rev_codes(
        replace(review, assessments=(replace(review.assessments[0], verdict="bad"), *review.assessments[1:]))
    )
```

**Test `test_every_requirement_needs_a_verdict_from_the_list`** checks: every requirement needs a verdict from the list.

Step by step:

- Stores the result of calling `good_review()` in `review`.
- Checks that `'REV003'` is in `rev_codes(replace(review, assessments=review.asse…`; if not, the test fails.
- Checks that `'REV003'` is in `rev_codes(replace(review, assessments=(replace(re…`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 158 to 161:

```python
def test_the_review_must_show_a_calculation():
    review = good_review()
    no_math = replace(review, assessments=(replace(review.assessments[0], reason="too slow"), *review.assessments[1:]))
    assert "REV004" in rev_codes(no_math)
```

**Test `test_the_review_must_show_a_calculation`** checks: the review must show a calculation.

Step by step:

- Stores the result of calling `good_review()` in `review`.
- Stores the result of calling `replace(review, assessments=(replace(review.assessments[0], reason='too slow'), *review.a…` in `no_math`.
- Checks that `'REV004'` is in `rev_codes(no_math)`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 164 to 169:

```python
def test_a_concern_must_point_at_a_requirement():
    review = good_review()
    opinion = replace(review, findings=(replace(review.findings[0], requirement="R9"), *review.findings[1:]))
    assert "REV005" in rev_codes(opinion)
    bad_class = replace(review, findings=(replace(review.findings[0], cls="urgent"), *review.findings[1:]))
    assert "REV005" in rev_codes(bad_class)
```

**Test `test_a_concern_must_point_at_a_requirement`** checks: a concern must point at a requirement.

Step by step:

- Stores the result of calling `good_review()` in `review`.
- Stores the result of calling `replace(review, findings=(replace(review.findings[0], requirement='R9'), *review.findings…` in `opinion`.
- Checks that `'REV005'` is in `rev_codes(opinion)`; if not, the test fails.
- Stores the result of calling `replace(review, findings=(replace(review.findings[0], cls='urgent'), *review.findings[1:]…` in `bad_class`.
- Checks that `'REV005'` is in `rev_codes(bad_class)`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 172 to 177:

```python
def test_a_taste_finding_names_no_requirement_and_is_dropped_aloud():
    review = good_review()
    with_requirement = replace(review.findings[3], requirement="R1")
    assert "REV006" in rev_codes(replace(review, findings=(*review.findings[:3], with_requirement)))
    kept = replace(review.findings[3], note="")
    assert "REV006" in rev_codes(replace(review, findings=(*review.findings[:3], kept)))
```

**Test `test_a_taste_finding_names_no_requirement_and_is_dropped_aloud`** checks: a taste finding names no requirement and is dropped aloud.

Step by step:

- Stores the result of calling `good_review()` in `review`.
- Stores the result of calling `replace(review.findings[3], requirement='R1')` in `with_requirement`.
- Checks that `'REV006'` is in `rev_codes(replace(review, findings=(*review.findi…`; if not, the test fails.
- Stores the result of calling `replace(review.findings[3], note='')` in `kept`.
- Checks that `'REV006'` is in `rev_codes(replace(review, findings=(*review.findi…`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 180 to 185:

```python
def test_a_review_that_blocks_on_everything_is_a_bottleneck():
    review = good_review()
    all_must = tuple(replace(item, cls="must-fix", requirement="R1", note="") for item in review.findings)
    assert "REV008" in rev_codes(replace(review, findings=all_must))
    no_taste = replace(review, findings=review.findings[:3])
    assert "REV008" in rev_codes(no_taste)
```

**Test `test_a_review_that_blocks_on_everything_is_a_bottleneck`** checks: a review that blocks on everything is a bottleneck.

Step by step:

- Stores the result of calling `good_review()` in `review`.
- Stores the result of calling `tuple((replace(item, cls='must-fix', requirement='R1', note='') for item in review.findin…` in `all_must`.
- Checks that `'REV008'` is in `rev_codes(replace(review, findings=all_must))`; if not, the test fails.
- Stores the result of calling `replace(review, findings=review.findings[:3])` in `no_taste`.
- Checks that `'REV008'` is in `rev_codes(no_taste)`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 188 to 196:

```python
def test_decisions_risks_and_actions_need_owners_and_dates():
    review = good_review()
    assert "REV009" in rev_codes(replace(review, decisions=()))
    assert "REV009" in rev_codes(replace(review, decisions=("ok",)))
    assert "REV010" in rev_codes(replace(review, risks=(AcceptedRisk("R3: x", "the team", "2026-12-01"),)))
    assert "REV010" in rev_codes(replace(review, risks=(AcceptedRisk("R3: x", "Lead", "December"),)))
    assert "REV011" in rev_codes(replace(review, actions=()))
    assert "REV011" in rev_codes(replace(review, actions=(ActionItem("x", "everyone", "2026-10-29"),)))
    assert "REV011" in rev_codes(replace(review, actions=(ActionItem("x", "Lead", "soon"),)))
```

**Test `test_decisions_risks_and_actions_need_owners_and_dates`** checks: decisions risks and actions need owners and dates.

Step by step:

- Stores the result of calling `good_review()` in `review`.
- Checks that `'REV009'` is in `rev_codes(replace(review, decisions=()))`; if not, the test fails.
- Checks that `'REV009'` is in `rev_codes(replace(review, decisions=('ok',)))`; if not, the test fails.
- Checks that `'REV010'` is in `rev_codes(replace(review, risks=(AcceptedRisk('R3…`; if not, the test fails.
- Checks that `'REV010'` is in `rev_codes(replace(review, risks=(AcceptedRisk('R3…`; if not, the test fails.
- Checks that `'REV011'` is in `rev_codes(replace(review, actions=()))`; if not, the test fails.
- Checks that `'REV011'` is in `rev_codes(replace(review, actions=(ActionItem('x'…`; if not, the test fails.
- Checks that `'REV011'` is in `rev_codes(replace(review, actions=(ActionItem('x'…`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 199 to 202:

```python
def test_a_verdict_that_is_not_met_needs_a_finding_or_a_risk():
    review = good_review()
    orphan = replace(review, findings=review.findings[2:], risks=())
    assert "REV007" in rev_codes(orphan)
```

**Test `test_a_verdict_that_is_not_met_needs_a_finding_or_a_risk`** checks: a verdict that is not met needs a finding or a risk.

Step by step:

- Stores the result of calling `good_review()` in `review`.
- Stores the result of calling `replace(review, findings=review.findings[2:], risks=())` in `orphan`.
- Checks that `'REV007'` is in `rev_codes(orphan)`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 205 to 209:

```python
def test_a_review_where_the_reviewer_is_never_wrong_looks_like_a_rubber_stamp():
    review = good_review()
    assert "REV012" in rev_codes(replace(review, disagreements=()))
    assert "REV012" in rev_codes(replace(review, disagreements=(Disagreement("3", "x", "rejected."),)))
    assert "REV012" in rev_codes(replace(review, disagreements=(Disagreement("1", "x", "accepted."),)))
```

**Test `test_a_review_where_the_reviewer_is_never_wrong_looks_like_a_rubber_stamp`** checks: a review where the reviewer is never wrong looks like a rubber stamp.

Step by step:

- Stores the result of calling `good_review()` in `review`.
- Checks that `'REV012'` is in `rev_codes(replace(review, disagreements=()))`; if not, the test fails.
- Checks that `'REV012'` is in `rev_codes(replace(review, disagreements=(Disagree…`; if not, the test fails.
- Checks that `'REV012'` is in `rev_codes(replace(review, disagreements=(Disagree…`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 212 to 216:

```python
def test_a_long_must_fix_list_is_a_warning():
    review = good_review()
    many = tuple(replace(review.findings[0], number=str(n)) for n in range(5))
    assert [f.code for f in warn_long_must_fix(replace(review, findings=many))] == ["REV014"]
    assert warn_long_must_fix(review) == []
```

**Test `test_a_long_must_fix_list_is_a_warning`** checks: a long must fix list is a warning.

Step by step:

- Stores the result of calling `good_review()` in `review`.
- Stores the result of calling `tuple((replace(review.findings[0], number=str(n)) for n in range(5)))` in `many`.
- Checks that `[f.code for f in warn_long_must_fix(replace(revie…` equals `['REV014']`; if not, the test fails.
- Checks that `warn_long_must_fix(review)` equals `[]`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 219 to 226:

```python
CHECK = Checklist(
    "c.md",
    (
        ChecklistItem("CHK-01", "throughput", "Did you compute the peak?"),
        ChecklistItem("CHK-02", "availability", "Which parts are single points?"),
    ),
    (),
)
```

These module-level lines:

- Stores the result of calling `Checklist('c.md', (ChecklistItem('CHK-01', 'throughput', 'Did you compute the peak?'), Ch…` in `CHECK`.

`tests/unit/domain/test_documents_rules.py` lines 229 to 230:

```python
def test_a_checklist_that_covers_the_findings_passes():
    assert check_checklist(CHECK, SET, [good_review()]) == []
```

**Test `test_a_checklist_that_covers_the_findings_passes`** checks: a checklist that covers the findings passes.

Step by step:

- Checks that `check_checklist(CHECK, SET, [good_review()])` equals `[]`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 233 to 235:

```python
def test_a_checklist_item_is_a_question_in_a_known_category():
    items = (ChecklistItem("CHK-01", "throughput", "Compute the peak."), ChecklistItem("CHK-02", "mystery", "Why?"))
    assert [f.code for f in check_checklist(replace(CHECK, items=items), SET, [])] == ["CHK001", "CHK001"]
```

**Test `test_a_checklist_item_is_a_question_in_a_known_category`** checks: a checklist item is a question in a known category.

Step by step:

- Stores the tuple `(ChecklistItem('CHK-01', 'throughput', 'Compute the peak.'), Checklis…` in `items`.
- Checks that `[f.code for f in check_checklist(replace(CHECK, i…` equals `['CHK001', 'CHK001']`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 238 to 240:

```python
def test_malformed_lines_and_long_lists_are_reported():
    assert [f.code for f in check_checklist(replace(CHECK, malformed=("- [ ] bad",)), SET, [])] == ["CHK001"]
    assert [f.code for f in check_checklist(CHECK, SET, [], max_items=1)] == ["CHK003"]
```

**Test `test_malformed_lines_and_long_lists_are_reported`** checks: malformed lines and long lists are reported.

Step by step:

- Checks that `[f.code for f in check_checklist(replace(CHECK, m…` equals `['CHK001']`; if not, the test fails.
- Checks that `[f.code for f in check_checklist(CHECK, SET, [], …` equals `['CHK003']`; if not, the test fails.

`tests/unit/domain/test_documents_rules.py` lines 243 to 246:

```python
def test_a_finding_in_a_category_no_item_covers_is_reported():
    review = good_review()
    only_throughput = replace(CHECK, items=CHECK.items[:1])
    assert [f.code for f in check_checklist(only_throughput, SET, [review])] == ["CHK002"]
```

**Test `test_a_finding_in_a_category_no_item_covers_is_reported`** checks: a finding in a category no item covers is reported.

Step by step:

- Stores the result of calling `good_review()` in `review`.
- Stores the result of calling `replace(CHECK, items=CHECK.items[:1])` in `only_throughput`.
- Checks that `[f.code for f in check_checklist(only_throughput,…` equals `['CHK002']`; if not, the test fails.

### `tests/unit/domain/test_durability_and_fitness.py`

`tests/unit/domain/test_durability_and_fitness.py` lines 1 to 15:

```python
import pytest

from design_review.domain.capacity import LoadModel
from design_review.domain.durability import check_write_order
from design_review.domain.fitness import (
    DurabilityScenario,
    FitnessModel,
    FitnessReport,
    ThumbnailRequirement,
    ThumbnailScenario,
    evaluate_durability,
    evaluate_thumbnails,
    run_fitness,
)
from design_review.domain.queue_model import BurstProfile
```

> **In plain words.** An **import** brings a name from another file or from Python's standard library into this file, so this file can use it.

Imports:

- It imports module `pytest`.
- From `design_review.domain.capacity` it takes `LoadModel`.
- From `design_review.domain.durability` it takes `check_write_order`.
- From `design_review.domain.fitness` it takes `DurabilityScenario, FitnessModel, FitnessReport, ThumbnailRequirement, ThumbnailScenario, evaluate_durability, evaluate_thumbnails, run_fitness`.
- From `design_review.domain.queue_model` it takes `BurstProfile`.

`tests/unit/domain/test_durability_and_fitness.py` lines 17 to 20:

```python
LOAD = LoadModel(120_000, 10, 0.70, 2.5, 40)
BURST = BurstProfile(LOAD.average_rate, 40, 3600, 60)
REQUIREMENT = ThumbnailRequirement(95, 30)
ONE_DAY = 86_400
```

> **In plain words.** A name written in CAPITAL letters is a **constant** by convention: a value set once, not changed later.

These module-level lines:

- Stores the result of calling `LoadModel(120000, 10, 0.7, 2.5, 40)` in `LOAD`.
- Stores the result of calling `BurstProfile(LOAD.average_rate, 40, 3600, 60)` in `BURST`.
- Stores the result of calling `ThumbnailRequirement(95, 30)` in `REQUIREMENT`.
- Stores the number `86400` in `ONE_DAY`.

`tests/unit/domain/test_durability_and_fitness.py` lines 23 to 24:

```python
def thumbnails(workers: int, expect_pass: bool = True):
    return evaluate_thumbnails(LOAD, 2.0, BURST, REQUIREMENT, ThumbnailScenario("x", workers, expect_pass), ONE_DAY)
```

> **In plain words.** `return value` ends the function and gives the value back to whoever called it.
> **In plain words.** A **type hint** such as `x: int` or `-> str` says what kind of value a name holds or a function gives back. Python does not enforce hints when the program runs; the type checker mypy reads them before.

**Function `thumbnails`.**

It takes: `workers` (a `int`); `expect_pass` (a `bool`), default `True`.

Step by step:

- Gives back the result of calling `evaluate_thumbnails(LOAD, 2.0, BURST, REQUIREMENT, ThumbnailScenario('x', workers, expect…`.

`tests/unit/domain/test_durability_and_fitness.py` lines 27 to 31:

```python
def test_one_worker_cannot_keep_up_with_the_average():
    result = thumbnails(1, expect_pass=False)
    assert not result.passed
    assert result.as_expected
    assert result.capacity == 0.5
```

> **In plain words.** `assert condition` checks that something is true. In a test, a false condition fails the test and pytest shows both sides of the comparison.
> **In plain words.** A call such as `f(a, key=value)` passes `a` by position and `key` by name (a **keyword argument**).
> **In plain words.** `==` tests equality, `is` tests that two names are the very same object (used for `None` and enum members), `in` tests membership.
> **In plain words.** A **test** is a function whose name starts with `test_`. pytest finds it, runs it, and reports a pass when no `assert` fails and nothing raises.

**Test `test_one_worker_cannot_keep_up_with_the_average`** checks: one worker cannot keep up with the average.

Step by step:

- Stores the result of calling `thumbnails(1, expect_pass=False)` in `result`.
- Checks that not (`result.passed`); if not, the test fails.
- Checks that `result.as_expected`; if not, the test fails.
- Checks that `result.capacity` equals `0.5`; if not, the test fails.

`tests/unit/domain/test_durability_and_fitness.py` lines 34 to 38:

```python
def test_eight_workers_cover_the_average_but_not_the_burst():
    result = thumbnails(8, expect_pass=False)
    assert result.capacity >= result.average_rate
    assert result.wait_at_percentile > 30
    assert not result.passed
```

**Test `test_eight_workers_cover_the_average_but_not_the_burst`** checks: eight workers cover the average but not the burst.

Step by step:

- Stores the result of calling `thumbnails(8, expect_pass=False)` in `result`.
- Checks that `result.capacity` is at least `result.average_rate`; if not, the test fails.
- Checks that `result.wait_at_percentile` is more than `30`; if not, the test fails.
- Checks that not (`result.passed`); if not, the test fails.

`tests/unit/domain/test_durability_and_fitness.py` lines 41 to 45:

```python
def test_eighty_workers_cover_the_burst():
    result = thumbnails(80)
    assert result.passed
    assert result.workers_for_peak == 80
    assert result.wait_at_percentile == 0
```

**Test `test_eighty_workers_cover_the_burst`** checks: eighty workers cover the burst.

Step by step:

- Stores the result of calling `thumbnails(80)` in `result`.
- Checks that `result.passed`; if not, the test fails.
- Checks that `result.workers_for_peak` equals `80`; if not, the test fails.
- Checks that `result.wait_at_percentile` equals `0`; if not, the test fails.

`tests/unit/domain/test_durability_and_fitness.py` lines 48 to 49:

```python
def test_a_surprising_verdict_is_flagged():
    assert not thumbnails(80, expect_pass=False).as_expected
```

**Test `test_a_surprising_verdict_is_flagged`** checks: a surprising verdict is flagged.

Step by step:

- Checks that not (`thumbnails(80, expect_pass=False).as_expected`); if not, the test fails.

`tests/unit/domain/test_durability_and_fitness.py` lines 52 to 55:

```python
def test_the_drafts_write_order_loses_an_accepted_upload():
    result = check_write_order(("put_object", "respond", "write_row"))
    assert not result.holds
    assert "the row is missing" in result.violations[0]
```

> **In plain words.** A **tuple** `(a, b)` is a fixed list of values that cannot be changed.
> **In plain words.** `obj[key]` looks a value up by key or position.

**Test `test_the_drafts_write_order_loses_an_accepted_upload`** checks: the drafts write order loses an accepted upload.

Step by step:

- Stores the result of calling `check_write_order(('put_object', 'respond', 'write_row'))` in `result`.
- Checks that not (`result.holds`); if not, the test fails.
- Checks that `'the row is missing'` is in `result.violations[0]`; if not, the test fails.

`tests/unit/domain/test_durability_and_fitness.py` lines 58 to 61:

```python
def test_file_then_row_then_response_loses_nothing_but_leaves_an_orphan():
    result = check_write_order(("put_object", "write_row", "respond"))
    assert result.holds
    assert result.orphans
```

**Test `test_file_then_row_then_response_loses_nothing_but_leaves_an_orphan`** checks: file then row then response loses nothing but leaves an orphan.

Step by step:

- Stores the result of calling `check_write_order(('put_object', 'write_row', 'respond'))` in `result`.
- Checks that `result.holds`; if not, the test fails.
- Checks that `result.orphans`; if not, the test fails.

`tests/unit/domain/test_durability_and_fitness.py` lines 64 to 67:

```python
def test_the_row_first_order_loses_nothing_and_leaves_no_orphan():
    result = check_write_order(("write_row_pending", "put_object", "mark_stored", "respond"))
    assert result.holds
    assert result.orphans == ()
```

**Test `test_the_row_first_order_loses_nothing_and_leaves_no_orphan`** checks: the row first order loses nothing and leaves no orphan.

Step by step:

- Stores the result of calling `check_write_order(('write_row_pending', 'put_object', 'mark_stored', 'respond'))` in `result`.
- Checks that `result.holds`; if not, the test fails.
- Checks that `result.orphans` equals `()`; if not, the test fails.

`tests/unit/domain/test_durability_and_fitness.py` lines 70 to 72:

```python
def test_responding_first_loses_both_parts():
    result = check_write_order(("respond", "write_row", "put_object"))
    assert "the row and the object" in result.violations[0]
```

**Test `test_responding_first_loses_both_parts`** checks: responding first loses both parts.

Step by step:

- Stores the result of calling `check_write_order(('respond', 'write_row', 'put_object'))` in `result`.
- Checks that `'the row and the object'` is in `result.violations[0]`; if not, the test fails.

`tests/unit/domain/test_durability_and_fitness.py` lines 75 to 77:

```python
def test_responding_after_the_row_only_loses_the_object():
    result = check_write_order(("write_row", "respond", "put_object"))
    assert "the object is missing" in result.violations[0]
```

**Test `test_responding_after_the_row_only_loses_the_object`** checks: responding after the row only loses the object.

Step by step:

- Stores the result of calling `check_write_order(('write_row', 'respond', 'put_object'))` in `result`.
- Checks that `'the object is missing'` is in `result.violations[0]`; if not, the test fails.

`tests/unit/domain/test_durability_and_fitness.py` lines 80 to 82:

```python
def test_an_unknown_step_is_rejected():
    with pytest.raises(ValueError, match="unknown"):
        check_write_order(("teleport",))
```

> **In plain words.** `with pytest.raises(Error):` expects the code inside to raise that error; the test fails if it does not.

**Test `test_an_unknown_step_is_rejected`** checks: an unknown step is rejected.

Step by step:

- Expects the steps inside to raise the error in `pytest.raises(ValueError, match='unknown')`:
  - Calls `check_write_order(('teleport',))`.

`tests/unit/domain/test_durability_and_fitness.py` lines 85 to 87:

```python
def test_a_durability_verdict_compares_with_the_expectation():
    assert evaluate_durability(DurabilityScenario("d", ("put_object", "respond", "write_row"), False)).as_expected
    assert not evaluate_durability(DurabilityScenario("d", ("put_object", "respond", "write_row"), True)).as_expected
```

**Test `test_a_durability_verdict_compares_with_the_expectation`** checks: a durability verdict compares with the expectation.

Step by step:

- Checks that `evaluate_durability(DurabilityScenario('d', ('put_object', 'respond',…`; if not, the test fails.
- Checks that not (`evaluate_durability(DurabilityScenario('d', ('put_object', 'respond',…`); if not, the test fails.

`tests/unit/domain/test_durability_and_fitness.py` lines 90 to 102:

```python
def test_the_report_is_ok_only_when_every_scenario_is_as_expected():
    model = FitnessModel(
        LOAD,
        2.0,
        BURST,
        REQUIREMENT,
        (ThumbnailScenario("ceiling", 80, True),),
        (DurabilityScenario("reviewed", ("write_row_pending", "put_object", "mark_stored", "respond"), True),),
    )
    assert run_fitness(model, ONE_DAY).ok
    wrong = FitnessModel(LOAD, 2.0, BURST, REQUIREMENT, (ThumbnailScenario("ceiling", 80, False),), ())
    assert not run_fitness(wrong, ONE_DAY).ok
    assert isinstance(run_fitness(wrong, ONE_DAY), FitnessReport)
```

**Test `test_the_report_is_ok_only_when_every_scenario_is_as_expected`** checks: the report is ok only when every scenario is as expected.

Step by step:

- Stores the result of calling `FitnessModel(LOAD, 2.0, BURST, REQUIREMENT, (ThumbnailScenario('ceiling', 80, True),), (D…` in `model`.
- Checks that `run_fitness(model, ONE_DAY).ok`; if not, the test fails.
- Stores the result of calling `FitnessModel(LOAD, 2.0, BURST, REQUIREMENT, (ThumbnailScenario('ceiling', 80, False),), (…` in `wrong`.
- Checks that not (`run_fitness(wrong, ONE_DAY).ok`); if not, the test fails.
- Checks that `isinstance(run_fitness(wrong, ONE_DAY), FitnessReport)`; if not, the test fails.

## Try it yourself

```bash
.venv/bin/pytest -q tests/unit/domain
```
Prints a row of dots, one per passing test, and a summary line such as `N passed in 0.5s` (skipped tests show as `s`).

```bash
.venv/bin/mypy
```
Checks the whole project (the `files` setting in `pyproject.toml`), these files included. Prints `Success: no issues found in 38 source files`.

```bash
.venv/bin/ruff check tests/unit/domain/test_capacity_and_queue.py tests/unit/domain/test_documents_rules.py tests/unit/domain/test_durability_and_fitness.py
```
Prints `All checks passed!`.

## Mistakes people make

- Tests that depend on each other's order. Each test here builds its own data.
- Asserting only the happy path. These tests also break the input on purpose and check the exact rule that fails.
- Forgetting `test_` in a name, so the test never runs.

## Check yourself

1. What does the test `test_the_lessons_load_numbers` check?
   **Answer:** it checks: the lessons load numbers.
2. What does the test `test_one_worker_does_half_a_photo_a_second` check?
   **Answer:** it checks: one worker does half a photo a second.
3. What does the test `test_workers_needed_rounds_up` check?
   **Answer:** it checks: workers needed rounds up.
4. What does the test `test_impossible_values_are_rejected` check?
   **Answer:** it checks: impossible values are rejected.
5. What does the test `test_the_burst_profile_keeps_the_mean_at_the_average` check?
   **Answer:** it checks: the burst profile keeps the mean at the average.

## Further reading

- pytest 9.1 documentation: <https://docs.pytest.org/en/stable/>
- How to use fixtures: <https://docs.pytest.org/en/stable/how-to/fixtures.html>
- `assert` rewriting: <https://docs.pytest.org/en/stable/how-to/assert.html>
