"""Quantified non-functional requirements: each one a number and a way to check it."""

from __future__ import annotations

from dataclasses import dataclass

from design_review.domain.findings import Finding, error
from design_review.domain.text import has_figure, words

ADJECTIVES = frozenset({"fast", "reliable", "scalable", "robust", "secure", "cheap", "highly", "available", "quick"})
NO_VERIFICATION = frozenset({"", "n/a", "na", "none", "tbd", "-"})
REQUIRED_CATEGORIES = ("throughput", "latency", "availability", "durability", "cost")


@dataclass(frozen=True)
class Requirement:
    """One requirement. `target` holds the number and its unit; `verification` says how it will be checked."""

    id: str
    category: str
    name: str
    target: str
    verification: str


@dataclass(frozen=True)
class RequirementSet:
    """The requirements of one system, from one document."""

    path: str
    requirements: tuple[Requirement, ...]
    required_categories: tuple[str, ...] = REQUIRED_CATEGORIES

    def by_id(self) -> dict[str, Requirement]:
        """Requirements keyed by id."""
        return {requirement.id: requirement for requirement in self.requirements}


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
