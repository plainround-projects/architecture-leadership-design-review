"""What the use cases need from the outside world."""

from __future__ import annotations

from typing import Protocol

from design_review.domain.checklist import Checklist
from design_review.domain.fitness import FitnessModel
from design_review.domain.proposal import Proposal
from design_review.domain.requirements import RequirementSet
from design_review.domain.review import ReviewRecord


class DocumentStore(Protocol):
    """Reads and writes the repository's files by path relative to its root."""

    def list_paths(self, folder: str) -> list[str]:
        """Markdown files directly inside the folder, sorted; empty when the folder is missing."""
        ...

    def read_text(self, path: str) -> str:
        """The text of a file."""
        ...

    def exists(self, path: str) -> bool:
        """True when the file exists."""
        ...

    def write_text(self, path: str, text: str) -> None:
        """Replace a file, creating its folder."""
        ...


class DocumentReader(Protocol):
    """Turns each document type's text into the domain's values."""

    def read_requirements(self, path: str) -> RequirementSet:
        """Parse a requirements document."""
        ...

    def read_proposal(self, path: str) -> Proposal:
        """Parse a proposal."""
        ...

    def read_review(self, path: str) -> ReviewRecord:
        """Parse a review record."""
        ...

    def read_checklist(self, path: str) -> Checklist:
        """Parse a checklist."""
        ...


class ModelSource(Protocol):
    """Loads the fitness model."""

    def load(self, path: str) -> FitnessModel:
        """Read and validate the model file."""
        ...
