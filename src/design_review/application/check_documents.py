"""The use case behind `design-review check`, and the one behind `design-review fitness`."""

from __future__ import annotations

from dataclasses import dataclass

from design_review.application.ports import DocumentReader, DocumentStore, ModelSource
from design_review.domain.checklist import check_checklist
from design_review.domain.findings import Finding, Report, error
from design_review.domain.fitness import FitnessReport, run_fitness
from design_review.domain.proposal import check_proposal
from design_review.domain.requirements import RequirementSet, check_requirements
from design_review.domain.review import ReviewRecord, check_review, warn_long_must_fix

PROPOSAL_FOLDER = "docs/proposals"
REQUIREMENTS_FOLDER = "docs/requirements"
REVIEW_FOLDER = "docs/reviews"
CHECKLIST_PATH = "docs/checklists/design-checklist.md"
MODEL_PATH = "model/uploads.toml"
PRIMARY_REQUIREMENTS = "docs/requirements/uploads-nfrs.md"


@dataclass(frozen=True)
class CheckSettings:
    """The size of two pages."""

    proposal_max_words: int = 1000


def check_documents(store: DocumentStore, reader: DocumentReader, settings: CheckSettings) -> Report:
    """Proposals, requirements, review records and the checklist: every rule, every file."""
    findings: list[Finding] = []
    subjects: list[str] = []
    requirement_sets: dict[str, RequirementSet] = {}
    for path in store.list_paths(REQUIREMENTS_FOLDER):
        requirement_sets[path] = reader.read_requirements(path)
        subjects.append(path)
        findings.extend(check_requirements(requirement_sets[path]))
    for path in store.list_paths(PROPOSAL_FOLDER):
        subjects.append(path)
        findings.extend(check_proposal(reader.read_proposal(path), settings.proposal_max_words))
    reviews: list[ReviewRecord] = []
    for path in store.list_paths(REVIEW_FOLDER):
        if not path.rsplit("/", 1)[1].startswith("review-"):
            continue
        review = reader.read_review(path)
        if review.requirements_path == PRIMARY_REQUIREMENTS:
            reviews.append(review)
        subjects.append(path)
        requirement_set = requirement_sets.get(review.requirements_path)
        if requirement_set is None:
            findings.append(
                error(
                    "REV002",
                    path,
                    f"'Requirements file' {review.requirements_path!r} is not a requirements document here",
                )
            )
            continue
        findings.extend(check_review(review, requirement_set))
        findings.extend(warn_long_must_fix(review))
    if store.exists(CHECKLIST_PATH) and PRIMARY_REQUIREMENTS in requirement_sets:
        subjects.append(CHECKLIST_PATH)
        findings.extend(
            check_checklist(reader.read_checklist(CHECKLIST_PATH), requirement_sets[PRIMARY_REQUIREMENTS], reviews)
        )
    else:
        findings.append(
            error("DOC001", CHECKLIST_PATH, "the design checklist or the primary requirements document is missing")
        )
    return Report(tuple(subjects), tuple(findings))


def run_fitness_functions(
    models: ModelSource, path: str = MODEL_PATH, horizon_seconds: int | None = None
) -> FitnessReport:
    """Load the model and evaluate every scenario."""
    return run_fitness(models.load(path), horizon_seconds)
