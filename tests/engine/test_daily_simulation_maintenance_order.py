"""Integration test for maintenance ordering."""

import pytest

from aquatwin.domain.daily_event_plan import DailyEventPlan
from aquatwin.domain.daily_inputs import DailyInputs
from aquatwin.domain.filter_unit import FilterUnit
from aquatwin.domain.fish_cohort import FishCohort
from aquatwin.domain.frozen_parameter_set import FrozenParameterSet
from aquatwin.domain.simulation_parameter import SimulationParameter
from aquatwin.domain.simulation_profile import SimulationProfile
from aquatwin.domain.species_simulation_mapping import (
    SpeciesSimulationMapping,
)
from aquatwin.domain.state import SimulationState
from aquatwin.domain.value_origin import ValueOrigin
from aquatwin.engine.daily_simulation_engine import (
    DailySimulationEngine,
)
from aquatwin.engine.step_context import StepContext


def parameter(
    name: str,
    value: float,
    unit: str,
) -> SimulationParameter:
    """Create one assumed simulation parameter."""
    return SimulationParameter(
        name=name,
        value=value,
        unit=unit,
        origin=ValueOrigin.ASSUMED,
    )


def test_maintenance_runs_before_feeding() -> None:
    """Remove opening Organic-N without removing today's feed input."""
    profile = SimulationProfile(
        profile_id="test-profile",
        name="Test Fish",
        adult_weight=parameter(
            "adult_weight",
            10.0,
            "g/fish",
        ),
        daily_feed_ratio=parameter(
            "daily_feed_ratio",
            0.01,
            "g-feed/g-fish/day",
        ),
        digestibility=parameter(
            "digestibility",
            1.0,
            "fraction",
        ),
        nitrogen_fraction=parameter(
            "nitrogen_fraction",
            0.10,
            "fraction",
        ),
        oxygen_consumption=parameter(
            "oxygen_consumption",
            0.0,
            "mg-O2/g/day",
        ),
        waste_factor=parameter(
            "waste_factor",
            1.0,
            "fraction",
        ),
        metabolic_tan_excretion=parameter(
            "metabolic_tan_excretion",
            0.0,
            "mg-N/g/day",
        ),
    )

    context = StepContext(
        previous_state=SimulationState(
            organic_n_mass_mg=100.0,
            tan_mass_mg=0.0,
            nitrite_mass_mg=0.0,
            nitrate_mass_mg=0.0,
        ),
        daily_inputs=DailyInputs(
            day=1,
            water_temperature_c=25.0,
            tank_volume_l=100.0,
            fish_cohorts=(
                FishCohort(
                    species_id="test-species",
                    count=10,
                ),
            ),
        ),
        daily_event_plan=DailyEventPlan(
            feeding=True,
            water_change=False,
            maintenance=True,
            maintenance_fraction=0.20,
        ),
        frozen_parameter_set=FrozenParameterSet(
            model_version="test-model",
            parameter_set_version="test-parameters",
            simulation_profiles=(profile,),
            species_simulation_mappings=(
                SpeciesSimulationMapping(
                    species_id="test-species",
                    simulation_profile_id="test-profile",
                ),
            ),
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

    assert result.is_valid

    assert metrics["maintenance_n_removal_mg"] == pytest.approx(
        20.0
    )
    assert metrics["feed_organic_n_input_mg"] == pytest.approx(
        100.0
    )

    assert result.new_state.organic_n_mass_mg == pytest.approx(
        180.0
    )

    maintenance_after_feeding_result_mg = (
        100.0 + metrics["feed_organic_n_input_mg"]
    ) * 0.80

    assert result.new_state.organic_n_mass_mg != pytest.approx(
        maintenance_after_feeding_result_mg
    )