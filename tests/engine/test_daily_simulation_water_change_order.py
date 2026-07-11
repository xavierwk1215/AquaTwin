"""Integration tests for water-change ordering and source-water input."""

import pytest

from aquatwin.domain.daily_event_plan import DailyEventPlan
from aquatwin.domain.daily_inputs import DailyInputs
from aquatwin.domain.filter_unit import FilterUnit
from aquatwin.domain.frozen_parameter_set import FrozenParameterSet
from aquatwin.domain.state import SimulationState
from aquatwin.engine.daily_simulation_engine import (
    DailySimulationEngine,
)
from aquatwin.engine.step_context import StepContext


def make_filter_unit() -> FilterUnit:
    """Create a filter with no configured biological media."""
    return FilterUnit(
        filter_id="test-filter",
        filter_type="internal",
        rated_flow_l_h=100.0,
        actual_flow_l_h=100.0,
        media=(),
    )


def test_water_change_runs_before_mineralization() -> None:
    """Apply water change first while preserving modelled Organic-N."""
    context = StepContext(
        previous_state=SimulationState(
            organic_n_mass_mg=100.0,
            tan_mass_mg=40.0,
            nitrite_mass_mg=20.0,
            nitrate_mass_mg=60.0,
        ),
        daily_inputs=DailyInputs(
            day=1,
            water_temperature_c=25.0,
            tank_volume_l=100.0,
        ),
        daily_event_plan=DailyEventPlan(
            feeding=False,
            water_change=True,
            maintenance=False,
            water_change_fraction=0.50,
        ),
        frozen_parameter_set=FrozenParameterSet(
            model_version="test-model",
            parameter_set_version="test-parameters",
            organic_n_mineralization_fraction_per_day=0.20,
            tan_oxidation_fraction_per_day=0.0,
            nitrite_oxidation_fraction_per_day=0.0,
        ),
    )

    result = DailySimulationEngine.run(
        context=context,
        filter_unit=make_filter_unit(),
    )

    metrics = {
        metric.name: metric.value
        for metric in result.metrics
    }

    assert result.is_valid

    assert metrics["water_change_n_removal_mg"] == pytest.approx(
        60.0
    )
    assert metrics["organic_n_mineralized_mg"] == pytest.approx(
        20.0
    )

    assert result.new_state.organic_n_mass_mg == pytest.approx(
        80.0
    )
    assert result.new_state.tan_mass_mg == pytest.approx(40.0)
    assert result.new_state.nitrite_mass_mg == pytest.approx(10.0)
    assert result.new_state.nitrate_mass_mg == pytest.approx(30.0)


def test_source_water_nitrogen_is_added_during_water_change() -> None:
    """Add replacement-water nitrogen after dissolved mass removal."""
    context = StepContext(
        previous_state=SimulationState(
            organic_n_mass_mg=0.0,
            tan_mass_mg=40.0,
            nitrite_mass_mg=20.0,
            nitrate_mass_mg=60.0,
        ),
        daily_inputs=DailyInputs(
            day=2,
            water_temperature_c=25.0,
            tank_volume_l=100.0,
            source_tan_mg_n_l=0.10,
            source_nitrite_mg_n_l=0.05,
            source_nitrate_mg_n_l=5.0,
        ),
        daily_event_plan=DailyEventPlan(
            feeding=False,
            water_change=True,
            maintenance=False,
            water_change_fraction=0.50,
        ),
        frozen_parameter_set=FrozenParameterSet(
            model_version="test-model",
            parameter_set_version="test-parameters",
            organic_n_mineralization_fraction_per_day=0.0,
            tan_oxidation_fraction_per_day=0.0,
            nitrite_oxidation_fraction_per_day=0.0,
        ),
    )

    result = DailySimulationEngine.run(
        context=context,
        filter_unit=make_filter_unit(),
    )

    metrics = {
        metric.name: metric.value
        for metric in result.metrics
    }

    assert result.is_valid

    assert metrics["water_change_n_removal_mg"] == pytest.approx(
        60.0
    )
    assert metrics["source_water_n_input_mg"] == pytest.approx(
        257.5
    )

    assert result.new_state.tan_mass_mg == pytest.approx(25.0)
    assert result.new_state.nitrite_mass_mg == pytest.approx(12.5)
    assert result.new_state.nitrate_mass_mg == pytest.approx(280.0)

    closing_total_n_mg = (
        result.new_state.organic_n_mass_mg
        + result.new_state.tan_mass_mg
        + result.new_state.nitrite_mass_mg
        + result.new_state.nitrate_mass_mg
    )

    assert closing_total_n_mg == pytest.approx(
        120.0 - 60.0 + 257.5
    )