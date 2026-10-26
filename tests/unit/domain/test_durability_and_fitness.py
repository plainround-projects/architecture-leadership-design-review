import pytest

from design_review.domain.capacity import LoadModel
from design_review.domain.durability import check_write_order
from design_review.domain.fitness import (
    DurabilityScenario,
    FitnessModel,
    FitnessReport,
    ThumbnailRequirement,
    ThumbnailScenario,
    evaluate_durability,
    evaluate_thumbnails,
    run_fitness,
)
from design_review.domain.queue_model import BurstProfile

LOAD = LoadModel(120_000, 10, 0.70, 2.5, 40)
BURST = BurstProfile(LOAD.average_rate, 40, 3600, 60)
REQUIREMENT = ThumbnailRequirement(95, 30)
ONE_DAY = 86_400


def thumbnails(workers: int, expect_pass: bool = True):
    return evaluate_thumbnails(LOAD, 2.0, BURST, REQUIREMENT, ThumbnailScenario("x", workers, expect_pass), ONE_DAY)


def test_one_worker_cannot_keep_up_with_the_average():
    result = thumbnails(1, expect_pass=False)
    assert not result.passed
    assert result.as_expected
    assert result.capacity == 0.5


def test_eight_workers_cover_the_average_but_not_the_burst():
    result = thumbnails(8, expect_pass=False)
    assert result.capacity >= result.average_rate
    assert result.wait_at_percentile > 30
    assert not result.passed


def test_eighty_workers_cover_the_burst():
    result = thumbnails(80)
    assert result.passed
    assert result.workers_for_peak == 80
    assert result.wait_at_percentile == 0


def test_a_surprising_verdict_is_flagged():
    assert not thumbnails(80, expect_pass=False).as_expected


def test_the_drafts_write_order_loses_an_accepted_upload():
    result = check_write_order(("put_object", "respond", "write_row"))
    assert not result.holds
    assert "the row is missing" in result.violations[0]


def test_file_then_row_then_response_loses_nothing_but_leaves_an_orphan():
    result = check_write_order(("put_object", "write_row", "respond"))
    assert result.holds
    assert result.orphans


def test_the_row_first_order_loses_nothing_and_leaves_no_orphan():
    result = check_write_order(("write_row_pending", "put_object", "mark_stored", "respond"))
    assert result.holds
    assert result.orphans == ()


def test_responding_first_loses_both_parts():
    result = check_write_order(("respond", "write_row", "put_object"))
    assert "the row and the object" in result.violations[0]


def test_responding_after_the_row_only_loses_the_object():
    result = check_write_order(("write_row", "respond", "put_object"))
    assert "the object is missing" in result.violations[0]


def test_an_unknown_step_is_rejected():
    with pytest.raises(ValueError, match="unknown"):
        check_write_order(("teleport",))


def test_a_durability_verdict_compares_with_the_expectation():
    assert evaluate_durability(DurabilityScenario("d", ("put_object", "respond", "write_row"), False)).as_expected
    assert not evaluate_durability(DurabilityScenario("d", ("put_object", "respond", "write_row"), True)).as_expected


def test_the_report_is_ok_only_when_every_scenario_is_as_expected():
    model = FitnessModel(
        LOAD,
        2.0,
        BURST,
        REQUIREMENT,
        (ThumbnailScenario("ceiling", 80, True),),
        (DurabilityScenario("reviewed", ("write_row_pending", "put_object", "mark_stored", "respond"), True),),
    )
    assert run_fitness(model, ONE_DAY).ok
    wrong = FitnessModel(LOAD, 2.0, BURST, REQUIREMENT, (ThumbnailScenario("ceiling", 80, False),), ())
    assert not run_fitness(wrong, ONE_DAY).ok
    assert isinstance(run_fitness(wrong, ONE_DAY), FitnessReport)
