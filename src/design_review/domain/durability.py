"""Crash-point enumeration for the upload write order: can an accepted upload be lost?"""

from __future__ import annotations

from dataclasses import dataclass

STEPS = frozenset({"write_row", "write_row_pending", "put_object", "mark_stored", "respond"})


@dataclass(frozen=True)
class DurabilityResult:
    """The order tried and every crash point where an upload the seller was told about is missing a part."""

    order: tuple[str, ...]
    violations: tuple[str, ...]
    orphans: tuple[str, ...] = ()

    @property
    def holds(self) -> bool:
        """True when no crash point loses an accepted upload."""
        return not self.violations


def check_write_order(order: tuple[str, ...]) -> DurabilityResult:
    """Crash after each prefix of the steps. Once `respond` has run the seller believes the upload is safe,
    so the row and the object must both exist. A half-written upload that was never acknowledged loses nothing,
    but an object with no row is an orphan nobody can find, so those crash points are reported too.
    """
    unknown = [step for step in order if step not in STEPS]
    if unknown:
        raise ValueError(f"unknown steps: {', '.join(unknown)}")
    violations: list[str] = []
    orphans: list[str] = []
    for crash_after in range(len(order) + 1):
        done = order[:crash_after]
        row = "write_row" in done or "write_row_pending" in done
        stored = "put_object" in done
        if "respond" in done and not (row and stored):
            missing = "the row" if stored else "the object" if row else "the row and the object"
            violations.append(f"crash after {', '.join(done)}: the seller was told yes, but {missing} is missing")
        if stored and not row:
            orphans.append(f"crash after {', '.join(done)}: an object with no row to find it by")
    return DurabilityResult(order, tuple(violations), tuple(orphans))
