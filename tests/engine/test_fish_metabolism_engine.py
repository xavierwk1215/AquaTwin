"""Tests for FishMetabolismEngine."""

import pytest

from aquatwin.domain.daily_event_plan import DailyEventPlan
from aquatwin.domain.daily_inputs import DailyInputs
from aquatwin.domain.fish_cohort import FishCohort
from aquatwin.domain.frozen_parameter_set import FrozenParameterSet
from aquatwin.domain.simulation_parameter import SimulationParameter
from aquatwin.domain.simulation_profile import SimulationProfile
from aquatwin.domain.species_simulation_mapping import (
    SpeciesSimulationMapping,
)
from aquatwin.domain.state import SimulationState
from aquatwin.domain.value_origin import ValueOrigin
from aquatwin.engine.fish_metabolism_engine import FishMetabolismEngine
from aquatwin.engine.step_context import StepContext


def make_parameter(
    name: str,
    value: float,
    unit: str,
) -> SimulationParameter:
    return SimulationParameter(
        name=name,
        value=value,
        unit=unit,
        origin=ValueOrigin.DERIVED,
    )


def make_context(
    *,
    feeding: bool,
    fish_cohorts: tuple[FishCohort, ...],
    metabolic_tan_rate: float = 0.04,
    oxygen_consumption_rate: float = 0.2,
) -> StepContext:
    profile = SimulationProfile(
        profile_id="profile_1",
        name="Test Profile",
        adult_weight=make_parameter(
            name="adult_weight",
            value=2.5,
            unit="g",
        ),
        daily_feed_ratio=make_parameter(
            name="daily_feed_ratio",
            value=0.02,
            unit="ratio/day",
        ),
        digestibility=make_parameter(
            name="digestibility",
            value=0.8,
            unit="ratio",
        ),
        nitrogen_fraction=make_parameter(
            name="nitrogen_fraction",
            value=0.08,
            unit="ratio",
        ),
        oxygen_consumption=make_parameter(
            name="oxygen_consumption",
            value=oxygen_consumption_rate,
            unit="mg-O2/g/day",
        ),
        waste_factor=make_parameter(
            name="waste_factor",
            value=0.2,
            unit="ratio",
        ),
        metabolic_tan_excretion=make_parameter(
            name="metabolic_tan_excretion",
            value=metabolic_tan_rate,
            unit="mg-N/g/day",
        ),
    )

    return StepContext(
        previous_state=SimulationState(
            organic_n_mass_mg=100.0,
            tan_mass_mg=20.0,
            nitrite_mass_mg=10.0,
            nitrate_mass_mg=50.0,
        ),
        daily_inputs=DailyInputs(
            day=1,
            water_temperature_c=25.0,
            tank_volume_l=100.0,
            fish_cohorts=fish_cohorts,
        ),
        daily_event_plan=DailyEventPlan(
            feeding=feeding,
            water_change=False,
            maintenance=False,
        ),
        frozen_parameter_set=FrozenParameterSet(
            model_version="test-model",
            parameter_set_version="test-parameters",
            simulation_profiles=(profile,),
            species_simulation_mappings=(
                SpeciesSimulationMapping(
                    species_id="neon_tetra",
                    simulation_profile_id="profile_1",
                ),
            ),
        ),
    )


def test_metabolism_runs_without_feeding_event() -> None:
    context = make_context(
        feeding=False,
        fish_cohorts=(
            FishCohort(
                species_id="neon_tetra",
                count=20,
            ),
        ),
    )

    FishMetabolismEngine.apply(context)

    assert context.working_state.tan_mass_mg == pytest.approx(22.0)

    assert context.metrics[0].name == "fish_biomass_g"
    assert context.metrics[0].value == pytest.approx(50.0)

    assert context.metrics[1].name == "fish_oxygen_consumption_mg"
    assert context.metrics[1].value == pytest.approx(10.0)

    assert context.metrics[2].name == "metabolic_tan_input_mg"
    assert context.metrics[2].value == pytest.approx(2.0)


def test_metabolism_also_runs_with_feeding_event() -> None:
    context = make_context(
        feeding=True,
        fish_cohorts=(
            FishCohort(
                species_id="neon_tetra",
                count=20,
            ),
        ),
    )

    FishMetabolismEngine.apply(context)

    assert context.working_state.tan_mass_mg == pytest.approx(22.0)
    assert len(context.metrics) == 3


def test_no_fish_does_not_change_state_or_metrics() -> None:
    context = make_context(
        feeding=False,
        fish_cohorts=(),
    )

    FishMetabolismEngine.apply(context)

    assert context.working_state.to_simulation_state() == (
        context.previous_state
    )
    assert context.metrics == []


def test_missing_metabolic_tan_parameter_defaults_to_zero() -> None:
    context = make_context(
        feeding=False,
        fish_cohorts=(
            FishCohort(
                species_id="neon_tetra",
                count=20,
            ),
        ),
    )

    profile = context.frozen_parameter_set.simulation_profiles[0]

    profile_without_tan_rate = SimulationProfile(
        profile_id=profile.profile_id,
        name=profile.name,
        adult_weight=profile.adult_weight,
        daily_feed_ratio=profile.daily_feed_ratio,
        digestibility=profile.digestibility,
        nitrogen_fraction=profile.nitrogen_fraction,
        oxygen_consumption=profile.oxygen_consumption,
        waste_factor=profile.waste_factor,
        metabolic_tan_excretion=None,
    )

    context = StepContext(
        previous_state=context.previous_state,
        daily_inputs=context.daily_inputs,
        daily_event_plan=context.daily_event_plan,
        frozen_parameter_set=FrozenParameterSet(
            model_version="test-model",
            parameter_set_version="test-parameters",
            simulation_profiles=(profile_without_tan_rate,),
            species_simulation_mappings=(
                SpeciesSimulationMapping(
                    species_id="neon_tetra",
                    simulation_profile_id="profile_1",
                ),
            ),
        ),
    )

    FishMetabolismEngine.apply(context)

    assert context.working_state.tan_mass_mg == pytest.approx(20.0)
    assert context.metrics[2].value == pytest.approx(0.0)


def test_metabolism_does_not_change_other_nitrogen_pools() -> None:
    context = make_context(
        feeding=False,
        fish_cohorts=(
            FishCohort(
                species_id="neon_tetra",
                count=20,
            ),
        ),
    )

    FishMetabolismEngine.apply(context)

    assert context.working_state.organic_n_mass_mg == pytest.approx(
        100.0
    )
    assert context.working_state.nitrite_mass_mg == pytest.approx(
        10.0
    )
    assert context.working_state.nitrate_mass_mg == pytest.approx(
        50.0
    )