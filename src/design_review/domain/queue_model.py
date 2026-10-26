"""A fluid queue in front of a worker pool: how long a photo waits when load comes in bursts."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from design_review.domain.capacity import ModelError


@dataclass(frozen=True)
class BurstProfile:
    """A steady base rate with a burst at the peak rate at the start of every window.

    The base is chosen so the long-run mean equals the average rate, so bursts do not add load on top of the facts.
    """

    average_rate: float
    peak_rate: float
    every_seconds: int
    length_seconds: int

    def __post_init__(self) -> None:
        if not 0 < self.length_seconds < self.every_seconds:
            raise ModelError("the burst must be shorter than its window")
        if self.peak_rate < self.average_rate:
            raise ModelError("the peak cannot be below the average")

    @property
    def base_rate(self) -> float:
        """Photos a second between bursts."""
        quiet = self.every_seconds - self.length_seconds
        return (self.average_rate * self.every_seconds - self.peak_rate * self.length_seconds) / quiet

    def rates(self, seconds: int) -> Iterator[float]:
        """The arrival rate for each second of the horizon."""
        for second in range(seconds):
            yield self.peak_rate if second % self.every_seconds < self.length_seconds else self.base_rate


def simulate_waits(rates: Iterator[float], service_rate: float) -> list[tuple[float, float]]:
    """For each second, (seconds a photo arriving then waits, photos arriving). Backlog never goes below zero."""
    backlog = 0.0
    samples: list[tuple[float, float]] = []
    for rate in rates:
        backlog = max(0.0, backlog + rate - service_rate)
        samples.append((backlog / service_rate, rate))
    return samples


def percentile_wait(samples: list[tuple[float, float]], percentile: float) -> float:
    """The wait that `percentile` percent of photos stay within, weighting each second by its arrivals."""
    if not 0 < percentile <= 100:
        raise ModelError("percentile must be in (0, 100]")
    total = sum(weight for _, weight in samples)
    threshold = total * percentile / 100
    seen = 0.0
    for wait, weight in sorted(samples):
        seen += weight
        if seen >= threshold:
            return wait
    return 0.0
