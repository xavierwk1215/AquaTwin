"""Integration tests for DailySimulationEngine."""

import pytest

from aquatwin.domain.daily_event_plan import DailyEventPlan
from aquatwin.domain.daily_inputs import DailyInputs
from aquatwin.domain.filter_media import FilterMedia
from aquatwin.domain.filter_unit import FilterUnit
from aquatwin.domain.frozen_parameter_set import FrozenParameterSet
from aquatwin.domain.state import SimulationState
from aquatwin.engine.daily_simulation_engine import (
    DailySimulationEngine,
)
from aquatwin.engine.step_context import StepContext


def make_filter_unit() -> FilterUnit:
    """Create a mature biofilter with capacity above test demand."""
    return FilterUnit(
        filter_id="test-filter",
        filter_type="canister",
        rated_flow_l_h=500.0,
        actual_flow_l_h=400.0,
        maturity_fraction=1.0,
        fouling_fraction=0.0,
        media=(
            FilterMedia(
                media_type="biological-media",
                media_volume_l=1.0,
                tan_capacity_mg_n_l_media_day=100.0,
                nitrite_capacity_mg_n_l_media_day=100.0,
                usable_fraction=1.0,
            ),
        ),
    )


def test_run_executes_complete_daily_pipeline() -> None:
    """Execute one complete validated daily simulation step."""
    previous_state = SimulationState(
        organic_n_mass_mg=40.0,
        tan_mass_mg=20.0,
        nitrite_mass_mg=10.0,
        nitrate_mass_mg=30.0,
    )

    context = StepContext(
        previous_state=previous_state,
        daily_inputs=DailyInputs(
            day=1,
            water_temperature_c=25.0,
            tank_volume_l=100.0,
        ),
        daily_event_plan=DailyEventPlan(
            feeding=False,
            water_change=True,
            maintenance=True,
            water_change_fraction=0.25,
            maintenance_fraction=0.25,
        ),
        frozen_parameter_set=FrozenParameterSet(
            model_version="test-model",
            parameter_set_version="test-parameters",
            organic_n_mineralization_fraction_per_day=0.10,
            tan_oxidation_fraction_per_day=0.50,
            nitrite_oxidation_fraction_per_day=0.50,
        ),
    )

    result = DailySimulationEngine.run(
        context=context,
        filter_unit=make_filter_unit(),
    )

    assert result.is_valid
    assert result.simulation_day == 1

    assert result.new_state.organic_n_mass_mg == pytest.approx(26.0)
    assert result.new_state.tan_mass_mg == pytest.approx(9.5)
    assert result.new_state.nitrite_mass_mg == pytest.approx(8.5)
    assert result.new_state.nitrate_mass_mg == pytest.approx(31.0)

    metric_names = tuple(
        metric.name
        for metric in result.metrics
    )

    assert metric_names == (
        "water_change_n_removal_mg",
        "source_water_n_input_mg",
        "water_change_fraction",
        "maintenance_n_removal_mg",
        "organic_n_mineralized_mg",
        "biofilter_tan_capacity_mg_day",
        "biofilter_nitrite_capacity_mg_day",
        "potential_tan_n_oxidized_mg",
        "tan_n_oxidized_mg",
        "potential_nitrite_n_oxidized_mg",
        "nitrite_n_oxidized_mg",
    )

    assert previous_state == SimulationState(
        organic_n_mass_mg=40.0,
        tan_mass_mg=20.0,
        nitrite_mass_mg=10.0,
        nitrate_mass_mg=30.0,
    )


def test_run_returns_immutable_result_data() -> None:
    """Return state and metrics detached from later context changes."""
    context = StepContext(
        previous_state=SimulationState(
            organic_n_mass_mg=0.0,
            tan_mass_mg=0.0,
            nitrite_mass_mg=0.0,
            nitrate_mass_mg=0.0,
        ),
        daily_inputs=DailyInputs(
            day=2,
            water_temperature_c=25.0,
            tank_volume_l=100.0,
        ),
        daily_event_plan=DailyEventPlan(
            feeding=False,
            water_change=False,
            maintenance=False,
        ),
        frozen_parameter_set=FrozenParameterSet(
            model_version="test-model",
            parameter_set_version="test-parameters",
        ),
    )

    result = DailySimulationEngine.run(
        context=context,
        filter_unit=make_filter_unit(),
    )

    original_metrics = result.metrics
    context.metrics.clear()
    context.working_state.tan_mass_mg = 999.0

    assert result.is_valid
    assert result.new_state.tan_mass_mg == 0.0
    assert result.metrics == original_metrics
    assert isinstance(result.metrics, tuple)