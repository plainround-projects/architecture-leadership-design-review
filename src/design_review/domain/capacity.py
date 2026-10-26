"""The arithmetic of the review: how much load arrives, and how much one stage can carry."""

from __future__ import annotations

import math
from dataclasses import dataclass


class ModelError(ValueError):
    """A model value is out of range."""


@dataclass(frozen=True)
class LoadModel:
    """The facts the lesson gives: listings a week, photos per listing, and when they arrive."""

    listings_per_week: int
    photos_per_listing: int
    weekend_share: float
    weekend_days: float
    peak_uploads_per_second: float

    def __post_init__(self) -> None:
        if min(self.listings_per_week, self.photos_per_listing) <= 0 or self.weekend_days <= 0:
            raise ModelError("listings, photos and days must be positive")
        if not 0 < self.weekend_share <= 1:
            raise ModelError("weekend_share must be in (0, 1]")
        if self.peak_uploads_per_second <= 0:
            raise ModelError("the peak must be positive")

    @property
    def photos_per_week(self) -> int:
        """Most photos a week: every listing with its maximum number of photos."""
        return self.listings_per_week * self.photos_per_listing

    @property
    def weekend_seconds(self) -> float:
        """The length of the busy window in seconds."""
        return self.weekend_days * 86_400

    @property
    def average_rate(self) -> float:
        """Photos a second, averaged over the busy window."""
        return self.photos_per_week * self.weekend_share / self.weekend_seconds

    @property
    def peak_ratio(self) -> float:
        """How many times the average the requirement's peak is."""
        return self.peak_uploads_per_second / self.average_rate


@dataclass(frozen=True)
class Stage:
    """A worker pool: how many workers and how long one worker takes for one photo (all sizes)."""

    workers: int
    seconds_per_photo: float

    def __post_init__(self) -> None:
        if self.workers <= 0 or self.seconds_per_photo <= 0:
            raise ModelError("workers and seconds per photo must be positive")

    @property
    def capacity(self) -> float:
        """Photos a second this pool can finish."""
        return self.workers / self.seconds_per_photo


def workers_needed(rate: float, seconds_per_photo: float) -> int:
    """The smallest pool that keeps up with a rate of photos a second."""
    return math.ceil(rate * seconds_per_photo)
