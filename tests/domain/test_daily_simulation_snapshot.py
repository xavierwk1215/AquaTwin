"""Tests for DailySimulationSnapshot."""

from dataclasses import FrozenInstanceError

import pytest

from aquatwin.domain.daily_simulation_snapshot import (
    DailySimulationSnapshot,
)
from aquatwin.domain.metrics import DailyMetric
from aquatwin.domain.state import SimulationState


def create_state() -> SimulationState:
    """Create a valid simulation state for snapshot tests."""
    return SimulationState(
        organic_n_mass_mg=120.0,
        tan_mass_mg=20.0,
        nitrite_mass_mg=10.0,
        nitrate_mass_mg=50.0,
    )


def create_metrics() -> tuple[DailyMetric, ...]:
    """Create valid daily metrics for snapshot tests."""
    return (
        DailyMetric(
            name="feed_nitrogen_added",
            value=15.0,
            unit="mg-N",
        ),
        DailyMetric(
            name="water_changed",
            value=20.0,
            unit="L",
        ),
    )


_UNSET = object()


def create_snapshot(
    *,
    run_id: object = "run-001",
    simulation_day: object = 1,
    tank_volume_l: object = 100.0,
    state: object = _UNSET,
    metrics: object = _UNSET,
    validation_passed: object = True,
) -> DailySimulationSnapshot:
    """Create a snapshot while allowing individual invalid values."""
    resolved_state = create_state() if state is _UNSET else state
    resolved_metrics = create_metrics() if metrics is _UNSET else metrics

    return DailySimulationSnapshot(
        run_id=run_id,  # type: ignore[arg-type]
        simulation_day=simulation_day,  # type: ignore[arg-type]
        tank_volume_l=tank_volume_l,  # type: ignore[arg-type]
        state=resolved_state,  # type: ignore[arg-type]
        metrics=resolved_metrics,  # type: ignore[arg-type]
        validation_passed=validation_passed,  # type: ignore[arg-type]
    )


def test_create_daily_simulation_snapshot() -> None:
    """Store one valid immutable simulation-day record."""
    state = create_state()
    metrics = create_metrics()

    snapshot = DailySimulationSnapshot(
        run_id="run-001",
        simulation_day=7,
        tank_volume_l=100.0,
        state=state,
        metrics=metrics,
        validation_passed=True,
    )

    assert snapshot.run_id == "run-001"
    assert snapshot.simulation_day == 7
    assert snapshot.tank_volume_l == 100.0
    assert snapshot.state == state
    assert snapshot.metrics == metrics
    assert snapshot.validation_passed is True


def test_daily_simulation_snapshot_is_immutable() -> None:
    """Prevent historical simulation records from being modified."""
    snapshot = create_snapshot()

    with pytest.raises(FrozenInstanceError):
        snapshot.simulation_day = 2  # type: ignore[misc]


def test_calculate_nitrogen_concentrations() -> None:
    """Convert stored nitrogen masses into mg-N/L concentrations."""
    snapshot = create_snapshot(tank_volume_l=100.0)

    assert snapshot.organic_n_mg_n_l == pytest.approx(1.2)
    assert snapshot.tan_mg_n_l == pytest.approx(0.2)
    assert snapshot.nitrite_mg_n_l == pytest.approx(0.1)
    assert snapshot.nitrate_mg_n_l == pytest.approx(0.5)


def test_calculate_total_tracked_nitrogen_mass() -> None:
    """Sum all tracked nitrogen pools."""
    snapshot = create_snapshot()

    assert snapshot.total_nitrogen_mass_mg == pytest.approx(200.0)


def test_support_zero_nitrogen_state() -> None:
    """Return zero concentrations for an empty nitrogen state."""
    state = SimulationState(
        organic_n_mass_mg=0.0,
        tan_mass_mg=0.0,
        nitrite_mass_mg=0.0,
        nitrate_mass_mg=0.0,
    )

    snapshot = create_snapshot(
        tank_volume_l=200.0,
        state=state,
        metrics=(),
    )

    assert snapshot.organic_n_mg_n_l == 0.0
    assert snapshot.tan_mg_n_l == 0.0
    assert snapshot.nitrite_mg_n_l == 0.0
    assert snapshot.nitrate_mg_n_l == 0.0
    assert snapshot.total_nitrogen_mass_mg == 0.0


@pytest.mark.parametrize(
    "invalid_run_id",
    [None, 101, 1.5, True],
)
def test_reject_non_string_run_id(
    invalid_run_id: object,
) -> None:
    """Require a text identifier for the parent simulation run."""
    with pytest.raises(
        TypeError,
        match=r"run_id must be a string\.",
    ):
        create_snapshot(run_id=invalid_run_id)


@pytest.mark.parametrize(
    "invalid_run_id",
    ["", "   ", "\t"],
)
def test_reject_empty_run_id(
    invalid_run_id: str,
) -> None:
    """Reject blank simulation-run identifiers."""
    with pytest.raises(
        ValueError,
        match=r"run_id must not be empty\.",
    ):
        create_snapshot(run_id=invalid_run_id)


@pytest.mark.parametrize(
    "invalid_simulation_day",
    [None, 1.5, "1", True],
)
def test_reject_non_integer_simulation_day(
    invalid_simulation_day: object,
) -> None:
    """Require simulation days to use whole-number values."""
    with pytest.raises(
        TypeError,
        match=r"simulation_day must be an integer\.",
    ):
        create_snapshot(
            simulation_day=invalid_simulation_day,
        )


@pytest.mark.parametrize(
    "invalid_simulation_day",
    [0, -1, -30],
)
def test_reject_simulation_day_below_one(
    invalid_simulation_day: int,
) -> None:
    """Reject snapshots outside the valid simulation timeline."""
    with pytest.raises(
        ValueError,
        match=(
            r"simulation_day must be greater than or equal to 1\."
        ),
    ):
        create_snapshot(
            simulation_day=invalid_simulation_day,
        )


@pytest.mark.parametrize(
    "invalid_tank_volume_l",
    [None, "100", object(), True],
)
def test_reject_non_numeric_tank_volume(
    invalid_tank_volume_l: object,
) -> None:
    """Require tank volume to be a numeric value."""
    with pytest.raises(
        TypeError,
        match=r"tank_volume_l must be numeric\.",
    ):
        create_snapshot(
            tank_volume_l=invalid_tank_volume_l,
        )


@pytest.mark.parametrize(
    "invalid_tank_volume_l",
    [0.0, -1.0, -100],
)
def test_reject_non_positive_tank_volume(
    invalid_tank_volume_l: float,
) -> None:
    """Prevent invalid concentration calculations."""
    with pytest.raises(
        ValueError,
        match=r"tank_volume_l must be greater than zero\.",
    ):
        create_snapshot(
            tank_volume_l=invalid_tank_volume_l,
        )


@pytest.mark.parametrize(
    "invalid_state",
    [None, {}, "state", 100],
)
def test_reject_invalid_simulation_state(
    invalid_state: object,
) -> None:
    """Require the official immutable SimulationState contract."""
    with pytest.raises(
        TypeError,
        match=r"state must be a SimulationState\.",
    ):
        create_snapshot(state=invalid_state)


@pytest.mark.parametrize(
    "invalid_metrics",
    [
        [],
        {
            DailyMetric(
                name="feed_nitrogen_added",
                value=15.0,
                unit="mg-N",
            )
        },
    ],
)
def test_reject_metrics_that_are_not_a_tuple(
    invalid_metrics: object,
) -> None:
    """Keep snapshot metrics immutable and ordered."""
    with pytest.raises(
        TypeError,
        match=r"metrics must be a tuple\.",
    ):
        create_snapshot(metrics=invalid_metrics)


@pytest.mark.parametrize(
    "invalid_metrics",
    [
        ("invalid metric",),
        (
            DailyMetric(
                name="valid_metric",
                value=1.0,
                unit="mg-N",
            ),
            100,
        ),
    ],
)
def test_reject_tuple_with_invalid_metric_objects(
    invalid_metrics: tuple[object, ...],
) -> None:
    """Allow only DailyMetric objects in the metric collection."""
    with pytest.raises(
        TypeError,
        match=(
            r"metrics must contain only DailyMetric objects\."
        ),
    ):
        create_snapshot(metrics=invalid_metrics)


@pytest.mark.parametrize(
    "invalid_validation_passed",
    [None, 1, 0, "true"],
)
def test_reject_non_boolean_validation_status(
    invalid_validation_passed: object,
) -> None:
    """Require an explicit boolean validation result."""
    with pytest.raises(
        TypeError,
        match=r"validation_passed must be a boolean\.",
    ):
        create_snapshot(
            validation_passed=invalid_validation_passed,
        )