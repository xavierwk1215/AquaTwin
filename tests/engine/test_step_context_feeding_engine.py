"""Tests for the StepContext-based FeedingEngine."""

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
from aquatwin.engine.feeding_engine import FeedingEngine
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
            value=0.2,
            unit="mg-O2/g/day",
        ),
        waste_factor=make_parameter(
            name="waste_factor",
            value=0.2,
            unit="ratio",
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


def test_no_feeding_event_does_not_add_metric() -> None:
    context = make_context(
        feeding=False,
        fish_cohorts=(
            FishCohort(
                species_id="neon_tetra",
                count=20,
            ),
        ),
    )

    FeedingEngine.apply(context)

    assert context.metrics == []


def test_feeding_event_records_feeding_metrics() -> None:
    context = make_context(
        feeding=True,
        fish_cohorts=(
            FishCohort(
                species_id="neon_tetra",
                count=20,
            ),
        ),
    )

    FeedingEngine.apply(context)

    assert len(context.metrics) == 3

    assert context.metrics[0].name == "total_biomass_g"
    assert context.metrics[0].value == pytest.approx(50.0)
    assert context.metrics[0].unit == "g"

    assert context.metrics[1].name == "total_feed_mass_g"
    assert context.metrics[1].value == pytest.approx(1.0)
    assert context.metrics[1].unit == "g"

    assert context.metrics[2].name == "total_feed_nitrogen_mg"
    assert context.metrics[2].value == pytest.approx(80.0)
    assert context.metrics[2].unit == "mg-N"


def test_feeding_engine_does_not_change_nitrogen_state() -> None:
    context = make_context(
        feeding=True,
        fish_cohorts=(
            FishCohort(
                species_id="neon_tetra",
                count=20,
            ),
        ),
    )

    FeedingEngine.apply(context)

    assert context.working_state.to_simulation_state() == (
        context.previous_state
    )


def test_empty_fish_cohorts_records_zero_feeding_values() -> None:
    context = make_context(
        feeding=True,
        fish_cohorts=(),
    )

    FeedingEngine.apply(context)

    assert len(context.metrics) == 3
    assert context.metrics[0].value == pytest.approx(0.0)
    assert context.metrics[1].value == pytest.approx(0.0)
    assert context.metrics[2].value == pytest.approx(0.0)