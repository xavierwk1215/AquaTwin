"""Tests for WaterChangeEngine."""

import pytest

from aquatwin.domain.daily_event_plan import DailyEventPlan
from aquatwin.domain.daily_inputs import DailyInputs
from aquatwin.domain.frozen_parameter_set import FrozenParameterSet
from aquatwin.domain.state import SimulationState
from aquatwin.engine.step_context import StepContext
from aquatwin.engine.water_change_engine import WaterChangeEngine


def _context(
    *,
    water_change: bool = True,
    water_change_fraction: float = 0.3,
    tank_volume_l: float = 100.0,
    source_tan_mg_n_l: float = 0.0,
    source_nitrite_mg_n_l: float = 0.0,
    source_nitrate_mg_n_l: float = 0.0,
) -> StepContext:
    """Create a step context for water-change testing."""
    return StepContext(
        previous_state=SimulationState(
            organic_n_mass_mg=100.0,
            tan_mass_mg=10.0,
            nitrite_mass_mg=20.0,
            nitrate_mass_mg=30.0,
        ),
        daily_inputs=DailyInputs(
            day=1,
            water_temperature_c=25.0,
            tank_volume_l=tank_volume_l,
            source_tan_mg_n_l=source_tan_mg_n_l,
            source_nitrite_mg_n_l=source_nitrite_mg_n_l,
            source_nitrate_mg_n_l=source_nitrate_mg_n_l,
        ),
        daily_event_plan=DailyEventPlan(
            feeding=False,
            water_change=water_change,
            maintenance=False,
            water_change_fraction=water_change_fraction,
        ),
        frozen_parameter_set=FrozenParameterSet(
            model_version="0.1.0",
            parameter_set_version="test-v1",
        ),
    )


def test_no_water_change_leaves_state_and_metrics_unchanged() -> None:
    """Do nothing when no water-change event is scheduled."""
    context = _context(
        water_change=False,
        water_change_fraction=0.3,
        tank_volume_l=0.0,
    )

    WaterChangeEngine.apply(context)

    assert context.working_state.organic_n_mass_mg == 100.0
    assert context.working_state.tan_mass_mg == 10.0
    assert context.working_state.nitrite_mass_mg == 20.0
    assert context.working_state.nitrate_mass_mg == 30.0
    assert context.metrics == []


def test_water_change_removes_dissolved_nitrogen_proportionally() -> None:
    """Remove the configured fraction of dissolved nitrogen."""
    context = _context(
        water_change_fraction=0.3,
    )

    WaterChangeEngine.apply(context)

    assert context.working_state.tan_mass_mg == pytest.approx(7.0)
    assert context.working_state.nitrite_mass_mg == pytest.approx(14.0)
    assert context.working_state.nitrate_mass_mg == pytest.approx(21.0)


def test_water_change_does_not_remove_organic_nitrogen() -> None:
    """Keep modelled Organic-N unchanged during routine water changes."""
    context = _context(
        water_change_fraction=0.5,
    )

    WaterChangeEngine.apply(context)

    assert context.working_state.organic_n_mass_mg == 100.0


def test_source_water_adds_dissolved_nitrogen() -> None:
    """Add nitrogen contained in the replacement water."""
    context = _context(
        water_change_fraction=0.3,
        tank_volume_l=100.0,
        source_tan_mg_n_l=1.0,
        source_nitrite_mg_n_l=2.0,
        source_nitrate_mg_n_l=3.0,
    )

    WaterChangeEngine.apply(context)

    assert context.working_state.tan_mass_mg == pytest.approx(37.0)
    assert context.working_state.nitrite_mass_mg == pytest.approx(74.0)
    assert context.working_state.nitrate_mass_mg == pytest.approx(111.0)


def test_water_change_records_explanatory_metrics() -> None:
    """Record total removal, source input, and applied fraction."""
    context = _context(
        water_change_fraction=0.3,
        tank_volume_l=100.0,
        source_tan_mg_n_l=1.0,
        source_nitrite_mg_n_l=2.0,
        source_nitrate_mg_n_l=3.0,
    )

    WaterChangeEngine.apply(context)

    metrics_by_name = {
        metric.name: metric
        for metric in context.metrics
    }

    assert metrics_by_name[
        "water_change_n_removal_mg"
    ].value == pytest.approx(18.0)

    assert metrics_by_name[
        "source_water_n_input_mg"
    ].value == pytest.approx(180.0)

    assert metrics_by_name[
        "water_change_fraction"
    ].value == pytest.approx(0.3)


def test_invalid_water_change_fraction_raises_value_error() -> None:
    """Reject a water-change fraction outside the valid range."""
    context = _context(
        water_change_fraction=1.1,
    )

    with pytest.raises(
        ValueError,
        match="water_change_fraction",
    ):
        WaterChangeEngine.apply(context)


def test_non_positive_tank_volume_raises_value_error() -> None:
    """Require a positive tank volume for a water change."""
    context = _context(
        tank_volume_l=0.0,
    )

    with pytest.raises(
        ValueError,
        match="tank_volume_l",
    ):
        WaterChangeEngine.apply(context)