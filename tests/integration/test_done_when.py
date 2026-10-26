"""One test per 'Done when' line of the lesson, run over copies of the repository's own documents."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from design_review.application.check_documents import CheckSettings, check_documents
from design_review.infrastructure.filesystem import FileSystemStore
from design_review.infrastructure.markdown import MarkdownDocumentReader
from tests.conftest import REPOSITORY_ROOT

PROPOSAL = "docs/proposals/uploads-service-draft-1.md"
REQUIREMENTS = "docs/requirements/uploads-nfrs.md"
REVIEW = "docs/reviews/review-2026-10-22-uploads-service.md"


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    shutil.copytree(REPOSITORY_ROOT / "docs", tmp_path / "docs")
    shutil.copytree(REPOSITORY_ROOT / "model", tmp_path / "model")
    return tmp_path


def codes(root: Path) -> set[str]:
    store = FileSystemStore(root)
    return {f.code for f in check_documents(store, MarkdownDocumentReader(store), CheckSettings()).errors}


def edit(root: Path, path: str, old: str, new: str) -> None:
    text = (root / path).read_text()
    assert old in text, f"{old!r} not in {path}"
    (root / path).write_text(text.replace(old, new))


def test_the_repository_as_committed_passes(repo: Path) -> None:
    assert codes(repo) == set()


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


def test_done_when_2_a_requirement_with_no_check_is_rejected(repo: Path) -> None:
    edit(repo, REQUIREMENTS, "| 2,000 dollars a month | cloud bill |", "| 2,000 dollars a month | TBD |")
    assert "REQ002" in codes(repo)


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


def test_done_when_5_someone_not_in_the_room_can_tell_what_was_decided_and_what_is_open(repo: Path) -> None:
    review = MarkdownDocumentReader(FileSystemStore(repo)).read_review(REVIEW)
    assert review.decisions
    assert all(risk.owner and risk.look_again for risk in review.risks)
    assert all(action.owner and action.due for action in review.actions)
    edit(repo, REVIEW, "| Uploads team lead | 2026-10-29 |", "| the team | 2026-10-29 |")
    assert "REV011" in codes(repo)


def test_done_when_6_the_record_shows_the_author_changing_the_reviewers_position(repo: Path) -> None:
    review = MarkdownDocumentReader(FileSystemStore(repo)).read_review(REVIEW)
    contested = next(f for f in review.findings if f.number == review.disagreements[0].finding)
    assert contested.cls == "withdrawn"
    assert review.disagreements[0].outcome.startswith("accepted")
    edit(repo, REVIEW, "Outcome: accepted.", "Outcome: rejected.")
    assert "REV012" in codes(repo)


def test_the_stretch_checklist_covers_every_category_the_reviews_found_fault_in(repo: Path) -> None:
    edit(repo, "docs/checklists/design-checklist.md", "- [ ] CHK-06 [durability]", "- [ ] CHK-06 [cost]")
    assert "CHK002" in codes(repo)
