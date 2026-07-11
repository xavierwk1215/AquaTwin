"""Integration tests for daily nitrogen mass balance."""

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


def test_complete_daily_pipeline_preserves_nitrogen_mass() -> None:
    """Preserve total nitrogen through internal transformations."""
    previous_state = SimulationState(
        organic_n_mass_mg=80.0,
        tan_mass_mg=40.0,
        nitrite_mass_mg=20.0,
        nitrate_mass_mg=60.0,
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
            water_change=False,
            maintenance=False,
        ),
        frozen_parameter_set=FrozenParameterSet(
            model_version="test-model",
            parameter_set_version="test-parameters",
            organic_n_mineralization_fraction_per_day=0.25,
            tan_oxidation_fraction_per_day=0.50,
            nitrite_oxidation_fraction_per_day=0.50,
        ),
    )

    filter_unit = FilterUnit(
        filter_id="unlimited-test-filter",
        filter_type="internal",
        rated_flow_l_h=100.0,
        actual_flow_l_h=100.0,
        media=(),
    )

    result = DailySimulationEngine.run(
        context=context,
        filter_unit=filter_unit,
    )

    opening_total_n_mg = (
        previous_state.organic_n_mass_mg
        + previous_state.tan_mass_mg
        + previous_state.nitrite_mass_mg
        + previous_state.nitrate_mass_mg
    )

    closing_total_n_mg = (
        result.new_state.organic_n_mass_mg
        + result.new_state.tan_mass_mg
        + result.new_state.nitrite_mass_mg
        + result.new_state.nitrate_mass_mg
    )

    assert result.is_valid
    assert closing_total_n_mg == pytest.approx(opening_total_n_mg)

    assert not any(
        finding.code == "NITROGEN_MASS_BALANCE_VIOLATION"
        for finding in result.validation_result.findings
    )


def test_water_change_and_maintenance_removals_are_balanced() -> None:
    """Balance closing nitrogen against recorded external removals."""
    previous_state = SimulationState(
        organic_n_mass_mg=100.0,
        tan_mass_mg=40.0,
        nitrite_mass_mg=20.0,
        nitrate_mass_mg=60.0,
    )

    context = StepContext(
        previous_state=previous_state,
        daily_inputs=DailyInputs(
            day=2,
            water_temperature_c=25.0,
            tank_volume_l=100.0,
        ),
        daily_event_plan=DailyEventPlan(
            feeding=False,
            water_change=True,
            maintenance=True,
            water_change_fraction=0.25,
            maintenance_fraction=0.20,
        ),
        frozen_parameter_set=FrozenParameterSet(
            model_version="test-model",
            parameter_set_version="test-parameters",
            organic_n_mineralization_fraction_per_day=0.0,
            tan_oxidation_fraction_per_day=0.0,
            nitrite_oxidation_fraction_per_day=0.0,
        ),
    )

    filter_unit = FilterUnit(
        filter_id="test-filter",
        filter_type="internal",
        rated_flow_l_h=100.0,
        actual_flow_l_h=100.0,
        media=(),
    )

    result = DailySimulationEngine.run(
        context=context,
        filter_unit=filter_unit,
    )

    metrics = {
        metric.name: metric.value
        for metric in result.metrics
    }

    opening_total_n_mg = 220.0
    total_removal_mg = (
        metrics["water_change_n_removal_mg"]
        + metrics["maintenance_n_removal_mg"]
    )

    closing_total_n_mg = (
        result.new_state.organic_n_mass_mg
        + result.new_state.tan_mass_mg
        + result.new_state.nitrite_mass_mg
        + result.new_state.nitrate_mass_mg
    )

    assert result.is_valid
    assert metrics["source_water_n_input_mg"] == pytest.approx(0.0)

    assert closing_total_n_mg == pytest.approx(
        opening_total_n_mg - total_removal_mg
    )