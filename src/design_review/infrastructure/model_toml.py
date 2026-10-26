"""Load and validate `model/uploads.toml` into the fitness model."""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from typing import Any

from design_review.application.ports import DocumentStore
from design_review.domain.capacity import LoadModel, ModelError
from design_review.domain.fitness import DurabilityScenario, FitnessModel, ThumbnailRequirement, ThumbnailScenario
from design_review.domain.queue_model import BurstProfile


def _table(data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ModelError(f"the model file has no [{key}] table")
    return value


def _expect(table: Mapping[str, Any], name: str) -> bool:
    expect = table.get("expect")
    if expect not in ("pass", "fail"):
        raise ModelError(f"scenario {name!r}: expect must be 'pass' or 'fail', got {expect!r}")
    return bool(expect == "pass")


class TomlModelSource:
    """Reads the model through the document store, so tests need no disk."""

    def __init__(self, store: DocumentStore) -> None:
        self._store = store

    def load(self, path: str) -> FitnessModel:
        """Parse the file; a missing table or a value out of range raises ModelError."""
        try:
            data = tomllib.loads(self._store.read_text(path))
        except tomllib.TOMLDecodeError as problem:
            raise ModelError(f"{path} is not valid TOML: {problem}") from None
        load_table, burst_table = _table(data, "load"), _table(data, "burst")
        service, requirement = _table(data, "service"), _table(data, "requirement")
        try:
            load = LoadModel(
                listings_per_week=int(load_table["listings_per_week"]),
                photos_per_listing=int(load_table["photos_per_listing"]),
                weekend_share=float(load_table["weekend_share"]),
                weekend_days=float(load_table["weekend_days"]),
                peak_uploads_per_second=float(requirement["peak_uploads_per_second"]),
            )
            burst = BurstProfile(
                average_rate=load.average_rate,
                peak_rate=load.peak_uploads_per_second,
                every_seconds=int(burst_table["every_seconds"]),
                length_seconds=int(burst_table["length_seconds"]),
            )
            thumbnails = tuple(
                ThumbnailScenario(name, int(table["workers"]), _expect(table, name))
                for name, table in _table(data, "thumbnails").items()
            )
            durability = tuple(
                DurabilityScenario(name, tuple(table["order"]), _expect(table, name))
                for name, table in _table(data, "durability").items()
            )
            return FitnessModel(
                load=load,
                seconds_per_photo=float(service["seconds_per_photo_per_worker"]),
                burst=burst,
                requirement=ThumbnailRequirement(
                    float(requirement["thumbnail_percentile"]), float(requirement["thumbnail_seconds"])
                ),
                thumbnails=thumbnails,
                durability=durability,
            )
        except KeyError as missing:
            raise ModelError(f"the model file is missing {missing}") from None
