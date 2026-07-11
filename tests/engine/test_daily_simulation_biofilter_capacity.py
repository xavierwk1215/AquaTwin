"""Integration tests for biofilter capacity limits."""

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


def test_biofilter_capacity_limits_daily_oxidation() -> None:
    """Limit TAN and nitrite oxidation by available biofilter capacity."""
    context = StepContext(
        previous_state=SimulationState(
            organic_n_mass_mg=0.0,
            tan_mass_mg=100.0,
            nitrite_mass_mg=50.0,
            nitrate_mass_mg=0.0,
        ),
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
            organic_n_mineralization_fraction_per_day=0.0,
            tan_oxidation_fraction_per_day=1.0,
            nitrite_oxidation_fraction_per_day=1.0,
        ),
    )

    filter_unit = FilterUnit(
        filter_id="capacity-limited-filter",
        filter_type="canister",
        rated_flow_l_h=500.0,
        actual_flow_l_h=400.0,
        maturity_fraction=1.0,
        fouling_fraction=0.0,
        media=(
            FilterMedia(
                media_type="biological-media",
                media_volume_l=1.0,
                tan_capacity_mg_n_l_media_day=20.0,
                nitrite_capacity_mg_n_l_media_day=10.0,
                usable_fraction=1.0,
            ),
        ),
    )

    result = DailySimulationEngine.run(
        context=context,
        filter_unit=filter_unit,
    )

    metrics = {
        metric.name: metric.value
        for metric in result.metrics
    }

    assert result.is_valid

    assert metrics["biofilter_tan_capacity_mg_day"] == pytest.approx(
        20.0
    )
    assert metrics[
        "biofilter_nitrite_capacity_mg_day"
    ] == pytest.approx(10.0)

    assert metrics["potential_tan_n_oxidized_mg"] == pytest.approx(
        100.0
    )
    assert metrics["tan_n_oxidized_mg"] == pytest.approx(20.0)

    assert metrics[
        "potential_nitrite_n_oxidized_mg"
    ] == pytest.approx(70.0)
    assert metrics["nitrite_n_oxidized_mg"] == pytest.approx(10.0)

    assert result.new_state.organic_n_mass_mg == pytest.approx(0.0)
    assert result.new_state.tan_mass_mg == pytest.approx(80.0)
    assert result.new_state.nitrite_mass_mg == pytest.approx(60.0)
    assert result.new_state.nitrate_mass_mg == pytest.approx(10.0)