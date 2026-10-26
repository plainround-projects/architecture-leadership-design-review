"""The review record: findings tied to requirements, classified, with owners and dates."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from design_review.domain.findings import Finding, error, warning
from design_review.domain.requirements import RequirementSet
from design_review.domain.text import has_figure, words

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


@dataclass(frozen=True)
class UsedRequirement:
    """A requirement as the review cites it."""

    id: str
    name: str
    target: str
    verification: str


@dataclass(frozen=True)
class Assessment:
    """A verdict on one requirement, with the reason and any calculation."""

    requirement: str
    verdict: str
    reason: str


@dataclass(frozen=True)
class ReviewFinding:
    """One finding: which requirement it breaks and its class."""

    number: str
    text: str
    requirement: str
    cls: str
    note: str


@dataclass(frozen=True)
class AcceptedRisk:
    """A risk the room accepts, with who watches it and when to look again."""

    risk: str
    owner: str
    look_again: str


@dataclass(frozen=True)
class ActionItem:
    """Something to do, with one named owner and one date."""

    text: str
    owner: str
    due: str


@dataclass(frozen=True)
class Disagreement:
    """A finding the author contested, the argument and how it was resolved."""

    finding: str
    author_argument: str
    outcome: str


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


def _is_date(text: str) -> bool:
    try:
        date.fromisoformat(text.strip())
    except ValueError:
        return False
    return True


def check_review(review: ReviewRecord, requirement_set: RequirementSet) -> list[Finding]:
    """REV001 to REV013."""
    found: list[Finding] = []
    for rule in (_header, _requirements, _assessments, _findings, _record_parts, _disagreement):
        found.extend(rule(review, requirement_set))
    return found


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


def requirement_category(requirement_set: RequirementSet, requirement_id: str) -> str | None:
    """The category of a requirement cited by a finding, if the id is known."""
    known = requirement_set.by_id().get(requirement_id)
    return known.category if known else None


def warn_long_must_fix(review: ReviewRecord, limit: int = 3) -> list[Finding]:
    """REV014 (warning): a long must-fix list is a sign the review is blocking on too much."""
    count = sum(1 for item in review.findings if item.cls == "must-fix")
    if count > limit:
        return [warning("REV014", review.path, f"{count} must-fix findings; a good review's list is short")]
    return []
