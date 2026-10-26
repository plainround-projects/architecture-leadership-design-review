import pytest

from design_review.domain.capacity import LoadModel, ModelError, Stage, workers_needed
from design_review.domain.queue_model import BurstProfile, percentile_wait, simulate_waits

LOAD = LoadModel(120_000, 10, 0.70, 2.5, 40)


def test_the_lessons_load_numbers():
    assert LOAD.photos_per_week == 1_200_000
    assert LOAD.weekend_seconds == 216_000
    assert LOAD.average_rate == pytest.approx(3.889, abs=0.001)
    assert LOAD.peak_ratio == pytest.approx(10.29, abs=0.01)


def test_one_worker_does_half_a_photo_a_second():
    assert Stage(1, 2.0).capacity == 0.5
    assert Stage(80, 2.0).capacity == 40


def test_workers_needed_rounds_up():
    assert workers_needed(40, 2.0) == 80
    assert workers_needed(3.9, 2.0) == 8


@pytest.mark.parametrize(
    "build",
    [
        lambda: LoadModel(0, 10, 0.7, 2.5, 40),
        lambda: LoadModel(1, 1, 0.0, 2.5, 40),
        lambda: LoadModel(1, 1, 1.5, 2.5, 40),
        lambda: LoadModel(1, 1, 0.5, 2.5, 0),
        lambda: Stage(0, 2.0),
        lambda: Stage(1, 0.0),
    ],
)
def test_impossible_values_are_rejected(build):
    with pytest.raises(ModelError):
        build()


def test_the_burst_profile_keeps_the_mean_at_the_average():
    profile = BurstProfile(LOAD.average_rate, 40, 3600, 60)
    rates = list(profile.rates(3600))
    assert sum(rates) / len(rates) == pytest.approx(LOAD.average_rate)
    assert rates[0] == 40
    assert rates[100] == pytest.approx(profile.base_rate)


@pytest.mark.parametrize("args", [(3.9, 40, 60, 60), (3.9, 40, 60, 0), (50, 40, 3600, 60)])
def test_bad_burst_profiles_are_rejected(args):
    with pytest.raises(ModelError):
        BurstProfile(*args)


def test_a_pool_that_keeps_up_never_queues():
    samples = simulate_waits(iter([3.0] * 10), service_rate=4.0)
    assert all(wait == 0 for wait, _ in samples)


def test_a_pool_that_falls_behind_queues_longer_each_second():
    samples = simulate_waits(iter([5.0] * 4), service_rate=4.0)
    assert [wait for wait, _ in samples] == [0.25, 0.5, 0.75, 1.0]


def test_the_percentile_weights_seconds_by_their_arrivals():
    samples = [(0.0, 90.0), (50.0, 10.0)]
    assert percentile_wait(samples, 90) == 0.0
    assert percentile_wait(samples, 95) == 50.0
    assert percentile_wait([], 95) == 0.0


def test_a_percentile_outside_the_range_is_rejected():
    with pytest.raises(ModelError):
        percentile_wait([(1.0, 1.0)], 0)
