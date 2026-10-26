"""The design checklist an author applies before the review, built from the findings reviews repeat."""

from __future__ import annotations

import re
from dataclasses import dataclass

from design_review.domain.findings import Finding, error
from design_review.domain.requirements import RequirementSet
from design_review.domain.review import ReviewRecord, requirement_category

ITEM = re.compile(r"^- \[ \] (CHK-\d+) \[([a-z-]+)\] (.+)$")


@dataclass(frozen=True)
class ChecklistItem:
    """One question, tagged with the requirement category it protects."""

    id: str
    category: str
    question: str


@dataclass(frozen=True)
class Checklist:
    """A parsed checklist. `malformed` holds the lines that look like items but do not parse."""

    path: str
    items: tuple[ChecklistItem, ...]
    malformed: tuple[str, ...]


def check_checklist(
    checklist: Checklist,
    requirement_set: RequirementSet,
    reviews: list[ReviewRecord],
    max_items: int = 12,
) -> list[Finding]:
    """CHK001 to CHK003."""
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
