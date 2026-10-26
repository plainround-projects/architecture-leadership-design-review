"""A design proposal: concrete enough to review."""

from __future__ import annotations

from dataclasses import dataclass

from design_review.domain.findings import Finding, error

REQUIRED_SECTIONS = ("Overview", "Data flow", "Datastore", "External calls", "Scaling", "Failure handling", "Unsure")


@dataclass(frozen=True)
class Proposal:
    """A parsed proposal. `sections` maps a heading to its text; `diagram` is the first fenced block under Data flow."""

    path: str
    title: str
    author: str
    sections: dict[str, str]
    diagram: str
    word_count: int


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
