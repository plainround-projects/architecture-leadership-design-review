"""Parse the Markdown of each document type into the domain's values."""

from __future__ import annotations

import re

from design_review.application.ports import DocumentStore
from design_review.domain.checklist import ITEM, Checklist, ChecklistItem
from design_review.domain.proposal import Proposal
from design_review.domain.requirements import REQUIRED_CATEGORIES, Requirement, RequirementSet
from design_review.domain.review import (
    AcceptedRisk,
    ActionItem,
    Assessment,
    Disagreement,
    ReviewFinding,
    ReviewRecord,
    UsedRequirement,
)

_HEADING2 = re.compile(r"^## (.+?)\s*$")
_FENCE = re.compile(r"^```")
_FIELD = re.compile(r"^(Author|Date|Reviewers|System|Requirements file):\s*(.*?)\s*$")


def _sections(lines: list[str]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {"": []}
    current = ""
    for line in lines:
        match = _HEADING2.match(line)
        if match:
            current = match.group(1)
            grouped[current] = []
        else:
            grouped[current].append(line)
    return grouped


def _header_fields(sections: dict[str, list[str]]) -> dict[str, str]:
    """`Author:`, `Date:` and the other header fields, read only from the lines before the first heading."""
    return {m.group(1): m.group(2) for line in sections[""] if (m := _FIELD.match(line))}


def _section(sections: dict[str, list[str]], prefix: str) -> list[str]:
    """The lines of the first section whose heading starts with the prefix (headings may carry a parenthetical)."""
    for name, lines in sections.items():
        if name.startswith(prefix):
            return lines
    return []


def table_rows(lines: list[str]) -> list[dict[str, str]]:
    """The rows of the first Markdown table in the lines, keyed by the header cells."""
    rows: list[list[str]] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|"):
            rows.append([cell.strip() for cell in stripped.strip("|").split("|")])
        elif rows:
            break
    if len(rows) < 3:
        return []
    header, body = rows[0], rows[2:]
    return [dict(zip(header, row, strict=False)) | dict.fromkeys(header[len(row) :], "") for row in body]


def _bullets(lines: list[str]) -> tuple[str, ...]:
    items: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("- ", "* ")):
            items.append(stripped[2:].strip())
        elif stripped and items and not stripped.startswith("|"):
            items[-1] += " " + stripped
    return tuple(items)


def _paragraph(lines: list[str]) -> str:
    return " ".join(line.strip() for line in lines if line.strip())


class MarkdownDocumentReader:
    """Reads the repository's four document types from a store."""

    def __init__(self, store: DocumentStore) -> None:
        self._store = store

    def read_requirements(self, path: str) -> RequirementSet:
        """The `## Requirements` table: ID, Category, Requirement, Target, How to verify."""
        lines = self._store.read_text(path).splitlines()
        rows = table_rows(_section(_sections(lines), "Requirements"))
        declared = next((line.partition(":")[2] for line in lines if line.startswith("Categories:")), "")
        categories = tuple(part.strip() for part in declared.split(",") if part.strip()) or REQUIRED_CATEGORIES
        return RequirementSet(
            path=path,
            required_categories=categories,
            requirements=tuple(
                Requirement(
                    id=row.get("ID", ""),
                    category=row.get("Category", ""),
                    name=row.get("Requirement", ""),
                    target=row.get("Target", ""),
                    verification=row.get("How to verify", ""),
                )
                for row in rows
            ),
        )

    def read_proposal(self, path: str) -> Proposal:
        """A proposal: the title, the author, the sections, and the fenced diagram under `Data flow`."""
        text = self._store.read_text(path)
        lines = text.splitlines()
        sections = _sections(lines)
        flow = sections.get("Data flow", [])
        diagram: list[str] = []
        inside = False
        for line in flow:
            if _FENCE.match(line):
                inside = not inside
            elif inside:
                diagram.append(line)
        author = _header_fields(sections).get("Author", "")
        title = lines[0].removeprefix("# ").strip() if lines else ""
        return Proposal(
            path=path,
            title=title,
            author=author,
            sections={name: _paragraph(body) for name, body in sections.items() if name},
            diagram="\n".join(diagram),
            word_count=len(text.split()),
        )

    def read_review(self, path: str) -> ReviewRecord:
        """A review record: the header fields and the seven sections."""
        lines = self._store.read_text(path).splitlines()
        sections = _sections(lines)
        fields = _header_fields(sections)
        title = lines[0].removeprefix("# Design review:").strip() if lines else ""
        findings = []
        for row in table_rows(_section(sections, "Findings")):
            cls, _, note = row.get("Class", "").partition(",")
            findings.append(
                ReviewFinding(
                    row.get("#", ""), row.get("Finding", ""), row.get("Requirement", ""), cls.strip(), note.strip()
                )
            )
        disagreement_fields = _labeled(_section(sections, "Disagreement"))
        return ReviewRecord(
            path=path,
            system=title,
            date_text=fields.get("Date", ""),
            reviewers=fields.get("Reviewers", ""),
            author=fields.get("Author", ""),
            requirements_path=fields.get("Requirements file", ""),
            sections=tuple(name.split(" (")[0] for name in sections if name),
            used=tuple(
                UsedRequirement(
                    r.get("ID", ""), r.get("Requirement", ""), r.get("Target", ""), r.get("How to verify", "")
                )
                for r in table_rows(_section(sections, "Requirements used"))
            ),
            assessments=tuple(
                Assessment(r.get("ID", ""), r.get("Verdict", ""), r.get("Reason", ""))
                for r in table_rows(_section(sections, "Assessment"))
            ),
            findings=tuple(findings),
            decisions=_bullets(_section(sections, "Decisions")),
            risks=tuple(
                AcceptedRisk(r.get("Risk", ""), r.get("Owner", ""), r.get("Look again", ""))
                for r in table_rows(_section(sections, "Accepted risks"))
            ),
            actions=tuple(
                ActionItem(r.get("Action", ""), r.get("Owner", ""), r.get("Date", ""))
                for r in table_rows(_section(sections, "Action items"))
            ),
            disagreements=(
                (
                    Disagreement(
                        disagreement_fields.get("Finding", ""),
                        disagreement_fields.get("Author", ""),
                        disagreement_fields.get("Outcome", ""),
                    ),
                )
                if disagreement_fields
                else ()
            ),
        )

    def read_checklist(self, path: str) -> Checklist:
        """Checklist items are lines like `- [ ] CHK-01 [throughput] Is the peak computed?`."""
        items: list[ChecklistItem] = []
        malformed: list[str] = []
        for line in self._store.read_text(path).splitlines():
            if not line.startswith("- ["):
                continue
            match = ITEM.match(line)
            if match:
                items.append(ChecklistItem(match.group(1), match.group(2), match.group(3)))
            else:
                malformed.append(line)
        return Checklist(path, tuple(items), tuple(malformed))


def _labeled(lines: list[str]) -> dict[str, str]:
    """`Label: text` paragraphs (Finding, Author, Outcome), text continuing until the next label."""
    pattern = re.compile(r"^(Finding|Author|Outcome):\s*(.*)$")
    values: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines:
        match = pattern.match(line.strip())
        if match:
            current = match.group(1)
            values[current] = [match.group(2)]
        elif current is not None and line.strip():
            values[current].append(line.strip())
    return {key: " ".join(parts) for key, parts in values.items()}
