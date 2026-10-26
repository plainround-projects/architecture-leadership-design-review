"""Fitness functions: the requirements of the review, checked by arithmetic and simulation on every run."""

from __future__ import annotations

from dataclasses import dataclass

from design_review.domain.capacity import LoadModel, Stage, workers_needed
from design_review.domain.durability import DurabilityResult, check_write_order
from design_review.domain.queue_model import BurstProfile, percentile_wait, simulate_waits


@dataclass(frozen=True)
class ThumbnailRequirement:
    """Thumbnails ready within `seconds` for `percentile` percent of uploads."""

    percentile: float
    seconds: float


@dataclass(frozen=True)
class ThumbnailScenario:
    """One worker count to try, and the verdict the review expects for it."""

    name: str
    workers: int
    expect_pass: bool


@dataclass(frozen=True)
class ThumbnailResult:
    """Capacity, the workers the peak needs, and the simulated wait."""

    scenario: ThumbnailScenario
    capacity: float
    average_rate: float
    peak_rate: float
    workers_for_peak: int
    percentile: float
    wait_at_percentile: float
    passed: bool

    @property
    def as_expected(self) -> bool:
        """True when the verdict is the one the review recorded for this scenario."""
        return self.passed is self.scenario.expect_pass


def evaluate_thumbnails(
    load: LoadModel,
    seconds_per_photo: float,
    burst: BurstProfile,
    requirement: ThumbnailRequirement,
    scenario: ThumbnailScenario,
    horizon_seconds: int | None = None,
) -> ThumbnailResult:
    """Run one scenario: pass when the pool keeps up with the average and the burst wait is within the target."""
    stage = Stage(scenario.workers, seconds_per_photo)
    horizon = horizon_seconds if horizon_seconds is not None else int(load.weekend_seconds)
    samples = simulate_waits(burst.rates(horizon), stage.capacity)
    wait = percentile_wait(samples, requirement.percentile)
    passed = stage.capacity >= load.average_rate and wait <= requirement.seconds
    return ThumbnailResult(
        scenario=scenario,
        capacity=stage.capacity,
        average_rate=load.average_rate,
        peak_rate=burst.peak_rate,
        workers_for_peak=workers_needed(burst.peak_rate, seconds_per_photo),
        percentile=requirement.percentile,
        wait_at_percentile=wait,
        passed=passed,
    )


@dataclass(frozen=True)
class DurabilityScenario:
    """One write order to try, and the verdict the review expects for it."""

    name: str
    order: tuple[str, ...]
    expect_pass: bool


@dataclass(frozen=True)
class DurabilityVerdict:
    """The crash-point result with the expectation."""

    scenario: DurabilityScenario
    result: DurabilityResult

    @property
    def as_expected(self) -> bool:
        """True when the verdict is the one the review recorded for this order."""
        return self.result.holds is self.scenario.expect_pass


def evaluate_durability(scenario: DurabilityScenario) -> DurabilityVerdict:
    """Run one write order through the crash-point check."""
    return DurabilityVerdict(scenario, check_write_order(scenario.order))


@dataclass(frozen=True)
class FitnessModel:
    """Everything the fitness functions need, loaded from `model/uploads.toml`."""

    load: LoadModel
    seconds_per_photo: float
    burst: BurstProfile
    requirement: ThumbnailRequirement
    thumbnails: tuple[ThumbnailScenario, ...]
    durability: tuple[DurabilityScenario, ...]


@dataclass(frozen=True)
class FitnessReport:
    """Every scenario's result. The report is `ok` when each scenario gave the verdict the review expected."""

    thumbnails: tuple[ThumbnailResult, ...]
    durability: tuple[DurabilityVerdict, ...]

    @property
    def ok(self) -> bool:
        """True when no scenario surprised the review."""
        return all(item.as_expected for item in self.thumbnails) and all(item.as_expected for item in self.durability)


def run_fitness(model: FitnessModel, horizon_seconds: int | None = None) -> FitnessReport:
    """Evaluate every scenario in the model."""
    return FitnessReport(
        thumbnails=tuple(
            evaluate_thumbnails(
                model.load, model.seconds_per_photo, model.burst, model.requirement, scenario, horizon_seconds
            )
            for scenario in model.thumbnails
        ),
        durability=tuple(evaluate_durability(scenario) for scenario in model.durability),
    )
