# architecture-leadership-design-review

A design review of a photo-uploads proposal, run the way the lesson asks: requirements first as numbers, every finding tied to one, findings sorted into must-fix, should-fix and taste, and a written record with owners and dates. A small toolkit lints the proposal, the requirements, the review records and the checklist, and three fitness functions turn the review's arithmetic into checks that run on every commit.

| | |
| --- | --- |
| **Lesson** | `/prep/architecture-leadership/project-design-review`, "A design review that improves without blocking" (`data-structure-explainer/src/content/tracks/architecture-leadership/14-project-design-review.md` in the Plainround app) |
| **Planned hours** | 8 |
| **Level** | Intermediate |
| **Architecture** | [ARCHITECTURE.md](ARCHITECTURE.md), the review: [docs/reviews](docs/reviews), the model: [model/uploads.toml](model/uploads.toml) |

The lesson's deliverables are documents, so they are here as documents. The code is the part the lesson's stretch asks for ("add a fitness function so it isn't reviewed by hand next time") and the part that makes each "Done when" line checkable.

## Prerequisites

| Tool | Version | Used for |
| --- | --- | --- |
| Python | 3.12 or 3.13 (tested with 3.13.12; the CI uses 3.12) | the toolkit and its tests |
| GNU Make | 3.81 or newer | every command below |
| Python packages | none at run time (standard library only, including `tomllib`); pytest, pytest-cov, ruff, mypy, import-linter and pip-audit for development, pinned with hashes in `requirements-dev.lock`; `make` installs them into `.venv/` | development |

No Docker, no cloud account. Settings are environment variables with defaults, listed in `.env.example`; `make up` copies it to `.env` the first time.

## Setup, run, test, stop

```bash
make up          # create .venv from the hash-pinned lock file and copy .env.example to .env
make run         # document checks, the fitness functions, then write build/report.md
make test        # unit and integration tests with coverage (domain and application at 95% or more)
make lint        # ruff, ruff format, mypy --strict, import-linter, then the document checks
make audit       # pip-audit over the locked dependencies
make check       # lint and test, what the CI runs first
make down        # remove build/ (nothing is running, so there is nothing to stop)
```

`make run` on a fresh clone prints:

```text
.venv/bin/design-review check
OK: 6 documents checked, 0 errors, 0 warnings
.venv/bin/design-review fitness
thumbnails (95% of uploads within the target; capacity must also cover the average rate)
  draft1     1 workers  capacity   0.5/s  average 3.89/s  peak needs 80 workers  wait at p95 1390800.0 s  FAIL  (as expected)
  floor      8 workers  capacity   4.0/s  average 3.89/s  peak needs 80 workers  wait at p95    510.2 s  FAIL  (as expected)
  ceiling   80 workers  capacity  40.0/s  average 3.89/s  peak needs 80 workers  wait at p95      0.0 s  PASS  (as expected)
write order (a crash at any point must not lose an upload the seller was told about)
  draft1   put_object > respond > write_row  FAIL  (as expected)
      lost: crash after put_object, respond: the seller was told yes, but the row is missing
      orphan: crash after put_object: an object with no row to find it by
      orphan: crash after put_object, respond: an object with no row to find it by
  sequential put_object > write_row > respond  PASS  (as expected)
      orphan: crash after put_object: an object with no row to find it by
  reviewed write_row_pending > put_object > mark_stored > respond  PASS  (as expected)
OK: every scenario gave the verdict the review expected
.venv/bin/design-review report
wrote build/report.md
```

`design-review fitness` exits 1 if any scenario gives a verdict other than the one `model/uploads.toml` records for it. The `FAIL (as expected)` rows are the point: they show the draft failing the requirement and the decided design passing it.

## The documents

| Path | What it is | Lesson step |
| --- | --- | --- |
| [docs/proposals/uploads-service-draft-1.md](docs/proposals/uploads-service-draft-1.md) | The sample proposal, with its datastore, external calls, scaling, failure handling and the things its author is unsure about. | 1 |
| [docs/requirements/uploads-nfrs.md](docs/requirements/uploads-nfrs.md) | Six requirements (R1 to R6), each a number with a way to check it, and the derivation of the load. | 2 |
| [docs/reviews/review-2026-10-22-uploads-service.md](docs/reviews/review-2026-10-22-uploads-service.md) | The review record: verdict per requirement with arithmetic, eight findings, decisions, accepted risk, actions, the disagreement. | 3 to 6 |
| [docs/requirements/uploads-security.md](docs/requirements/uploads-security.md) and [docs/reviews/review-2026-10-22-uploads-service-security.md](docs/reviews/review-2026-10-22-uploads-service-security.md) | The same proposal through a security lens (stretch). | stretch |
| [docs/reviews/comparison.md](docs/reviews/comparison.md) | What the two lenses looked for, and what only one found (stretch). | stretch |
| [docs/checklists/design-checklist.md](docs/checklists/design-checklist.md) | Seven questions an author answers before asking for a review (stretch). | stretch |
| [model/uploads.toml](model/uploads.toml) | The proposal's facts and the scenarios the fitness functions try (stretch). | stretch |
| [templates/review-template.md](templates/review-template.md) | A blank review record in the format the linter checks. | |

## The checks

| Codes | What they check |
| --- | --- |
| PRP001 to PRP004 | The proposal has an overview, a data flow with a diagram that has arrows, a datastore, external calls, scaling, failure handling and what its author is unsure about; it is under two pages (`PROPOSAL_MAX_WORDS`); it names its author. |
| REQ001 to REQ004 | Every requirement target holds a number and is not an adjective; every one has a way to be checked; the required categories (throughput, latency, availability, durability, cost, or the ones the document declares) are all present; ids are unique. |
| REV001 to REV004 | The review has a date, reviewers, author and the seven sections; its requirements match the requirements document word for word; every requirement has a verdict (meets, might not, doesn't); at least one reason shows its arithmetic. |
| REV005 to REV008 | Every finding names a requirement of this review, or is `none` and classed taste with "dropped" said aloud; the class is one of must-fix, should-fix, taste, withdrawn; not everything is must-fix and at least one preference was dropped; every requirement that is not met has a finding or an accepted risk. |
| REV009 to REV013 | Decisions are sentences; accepted risks and action items have one named owner (not "the team") and an ISO date; there is a disagreement where the author won, on a finding classed withdrawn. |
| REV014 (warning) | More than three must-fix findings. |
| CHK001 to CHK003 | Checklist items are questions in a requirement category; every category of a must-fix or should-fix finding is covered; at most 12 items. |
| DOC001 | The checklist and the primary requirements document exist. |

The fitness functions (`design-review fitness`):

| Function | What it computes | Source |
| --- | --- | --- |
| Capacity | Average rate = 1,200,000 photos x 0.70 / 216,000 s = 3.89 a second; one worker = 1 / 2 s = 0.5 a second; workers for the 40 a second peak = 80. | `domain/capacity.py` |
| Queue wait | A fluid queue fed by the average rate with a one-minute burst at the peak every hour (the quiet rate keeps the mean at the average); the wait that 95 percent of photos stay within, for 1, 8 and 80 workers. | `domain/queue_model.py` |
| Write order | Crashes after every prefix of the steps and asks whether a seller who was told yes can lose the row or the file; also reports orphan files. | `domain/durability.py` |

## Done when: the lesson's checklist and the proof for each line

| # | Done when (from the lesson) | Command | What proves it |
| --- | --- | --- | --- |
| 1 | The proposal is concrete enough to review: it names its datastore, its external calls and its scaling approach. | `make run`; `pytest tests/integration/test_done_when.py -k done_when_1` | [The proposal](docs/proposals/uploads-service-draft-1.md) has the sections Datastore (PostgreSQL and object storage), External calls (object storage, the CDN) and Scaling (2 instances, 1 worker); PRP001 fails when one is emptied. |
| 2 | Each requirement is a number with a way to verify it, not an adjective. | `make run`; `pytest ... -k done_when_2` | [Six requirements](docs/requirements/uploads-nfrs.md) from 40 uploads a second to 2,000 dollars a month, each with a verification column. REQ001 fails on "fast"; REQ002 fails on "TBD". |
| 3 | Every concern you raise points to a requirement, and you have not raised a concern that no requirement supports. | `make run`; `pytest ... -k done_when_3` | In [the review](docs/reviews/review-2026-10-22-uploads-service.md) every finding has an R-number or is taste with `none`; REV005 fails on a finding that cites nothing real. Each non-met verdict has a finding or an accepted risk (REV007). |
| 4 | The must-fix list contains only things that would violate a requirement or a real risk, and you have consciously dropped at least one preference. | `make run`; `pytest ... -k done_when_4` | Two must-fix findings (one worker; the order of writes), two taste findings both "taste, dropped" (another CDN; a table name). REV006 and REV008 enforce it; the two must-fix findings are also what the fitness functions fail on. |
| 5 | Someone who wasn't in the review can tell what was decided and what is still open. | `make run`; `pytest ... -k done_when_5` | Three decisions, one accepted risk with owner and date (2026-12-01), three action items with one named owner and an ISO date each (REV009 to REV011, REV013). |
| 6 | The record shows one place where the author's argument changed your position, and the reasoning. | `make run`; `pytest ... -k done_when_6` | Finding 4 (one retry) is classed `withdrawn`; the Disagreement section quotes the author's argument and the outcome "accepted ... I changed my position on finding 4" (REV012). |

### Where this repository departs from the lesson's sample

The lesson's sample record decides "thumbnail workers scale on queue age, target 8 workers". The arithmetic does not support 8 for the stated requirement: 8 workers do 8 / 2 s = 4 photos a second, which covers the 3.89 average but not the 40 a second peak, and `design-review fitness` shows the 8-worker pool with a wait of about 510 seconds at the 95th percentile when the peak arrives. The review record here decides a floor of 8 and a ceiling of 80 (80 / 2 s = 40 a second), and the fitness table's `floor` row is the proof. The autoscaler's reaction time is not simulated (see below); the load test in the action items is what covers it.

## Stretch goals

| Stretch (from the lesson) | Built? |
| --- | --- |
| Turn your repeated findings into a short design checklist the team can self-apply before review. | Yes. [The checklist](docs/checklists/design-checklist.md) has seven questions; CHK002 fails if a finding's category has no question. |
| Add a fitness function (an automated check) for one requirement so it isn't reviewed by hand next time. | Yes, for two: the thumbnail requirement (R3) and the durability requirement (R5). `make run` and the CI run them. |
| Review the same proposal as a security reviewer and compare what you look for. | Yes. [Five security requirements](docs/requirements/uploads-security.md), [a second review record](docs/reviews/review-2026-10-22-uploads-service-security.md) that passes the same linter, and [the comparison](docs/reviews/comparison.md). |

## What is simplified for teaching

- The reviewers, the author and their names are roles; the review date is the lesson's.
- The queue model is a fluid approximation: arrivals are a base rate plus a fixed hourly burst, not random; there is no autoscaler delay, no retry traffic and no variation in photo size. It answers "can this many workers keep the wait under 30 seconds in a burst of this size", not "what will production do".
- The cost requirement has no model: the lesson's solution says "meets on the evidence so far, ask for an estimate", and the action items ask for one.
- Verdicts and classes are written by the reviewer; the toolkit checks that they are consistent and complete, not that they are right.

## Project structure

```text
src/design_review/
  domain/            requirements, proposal, review record and checklist rules (REQ, PRP, REV, CHK);
                     capacity, queue_model, durability and fitness (the fitness functions).
                     Depends on the standard library only.
  application/       the check and fitness use cases, report formatting, and the ports
                     (DocumentStore, DocumentReader, ModelSource). Depends on domain only.
  infrastructure/    the file-system store, the Markdown parsers, the TOML model loader, settings.
                     Depends on application and domain.
  interfaces/        the design-review command line (check, fitness, report). Nothing depends on it.
docs/
  proposals/         the proposal under review.
  requirements/      the quantified requirements (performance and security).
  reviews/           the review records, and the comparison of the two lenses.
  checklists/        the author's checklist.
model/uploads.toml   the proposal's facts and the fitness scenarios.
templates/           a blank review record.
tests/
  unit/              domain, application (in-memory store), infrastructure, command line.
  integration/       one test per "Done when" line, over copies of the real documents.
tech/                25 beginner notes, one per technology; start at tech/README.md.
pyproject.toml       metadata and every tool's configuration.   requirements*.lock  hash-pinned dependencies.
Makefile             the only commands a reader needs.          .github/workflows/ci.yml  the same checks on push.
```

The dependency rule (domain depends on nothing; application on domain; infrastructure and interfaces on both; nothing on interfaces) is enforced by `make lint` through import-linter.

## Author and license

Written by Sumit Srivastava. Released under the MIT License, see [LICENSE](LICENSE). Changes are in [CHANGELOG.md](CHANGELOG.md).
