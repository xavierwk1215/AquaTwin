"""Golden Scenario for the official DailySimulationEngine pipeline."""

import pytest

from aquatwin.domain.daily_event_plan import DailyEventPlan
from aquatwin.domain.daily_inputs import DailyInputs
from aquatwin.domain.filter_media import FilterMedia
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


def make_parameter(
    name: str,
    value: float,
    unit: str,
) -> SimulationParameter:
    """Create one deterministic assumed simulation parameter."""
    return SimulationParameter(
        name=name,
        value=value,
        unit=unit,
        origin=ValueOrigin.ASSUMED,
    )


def make_parameter_set() -> FrozenParameterSet:
    """Create the frozen parameters used by the Golden Scenario."""
    profile = SimulationProfile(
        profile_id="golden-profile",
        name="Golden Scenario Fish",
        adult_weight=make_parameter(
            name="adult_weight",
            value=10.0,
            unit="g/fish",
        ),
        daily_feed_ratio=make_parameter(
            name="daily_feed_ratio",
            value=0.01,
            unit="fraction/day",
        ),
        digestibility=make_parameter(
            name="digestibility",
            value=0.80,
            unit="fraction",
        ),
        nitrogen_fraction=make_parameter(
            name="nitrogen_fraction",
            value=0.05,
            unit="fraction",
        ),
        oxygen_consumption=make_parameter(
            name="oxygen_consumption",
            value=1.0,
            unit="mg-O2/g/day",
        ),
        waste_factor=make_parameter(
            name="waste_factor",
            value=1.0,
            unit="fraction",
        ),
        metabolic_tan_excretion=make_parameter(
            name="metabolic_tan_excretion",
            value=0.10,
            unit="mg-N/g/day",
        ),
    )

    mapping = SpeciesSimulationMapping(
        species_id="golden-species",
        simulation_profile_id="golden-profile",
    )

    return FrozenParameterSet(
        model_version="golden-model-v1",
        parameter_set_version="golden-parameters-v1",
        simulation_profiles=(profile,),
        species_simulation_mappings=(mapping,),
        organic_n_mineralization_fraction_per_day=0.20,
        tan_oxidation_fraction_per_day=0.50,
        nitrite_oxidation_fraction_per_day=0.50,
    )


def make_filter_unit() -> FilterUnit:
    """Create a filter with intentionally limiting daily capacities."""
    return FilterUnit(
        filter_id="golden-filter",
        filter_type="canister",
        rated_flow_l_h=500.0,
        actual_flow_l_h=400.0,
        maturity_fraction=1.0,
        fouling_fraction=0.0,
        media=(
            FilterMedia(
                media_type="golden-biological-media",
                media_volume_l=1.0,
                tan_capacity_mg_n_l_media_day=3.0,
                nitrite_capacity_mg_n_l_media_day=2.0,
                usable_fraction=1.0,
            ),
        ),
    )


def make_fish_cohorts() -> tuple[FishCohort, ...]:
    """Create a 20-gram fish population."""
    return (
        FishCohort(
            species_id="golden-species",
            count=2,
        ),
    )


def metric_value(
    result_metrics: tuple,
    metric_name: str,
) -> float:
    """Return a named metric value from one daily result."""
    return next(
        metric.value
        for metric in result_metrics
        if metric.name == metric_name
    )


def run_golden_scenario() -> tuple:
    """Run the deterministic two-day Golden Scenario."""
    parameter_set = make_parameter_set()
    filter_unit = make_filter_unit()
    fish_cohorts = make_fish_cohorts()

    opening_state = SimulationState(
        organic_n_mass_mg=0.0,
        tan_mass_mg=8.0,
        nitrite_mass_mg=4.0,
        nitrate_mass_mg=10.0,
    )

    day_1_context = StepContext(
        previous_state=opening_state,
        daily_inputs=DailyInputs(
            day=1,
            water_temperature_c=25.0,
            tank_volume_l=100.0,
            source_tan_mg_n_l=0.04,
            source_nitrite_mg_n_l=0.02,
            source_nitrate_mg_n_l=0.10,
            fish_cohorts=fish_cohorts,
        ),
        daily_event_plan=DailyEventPlan(
            feeding=True,
            water_change=True,
            maintenance=False,
            water_change_fraction=0.25,
        ),
        frozen_parameter_set=parameter_set,
    )

    day_1_result = DailySimulationEngine.run(
        context=day_1_context,
        filter_unit=filter_unit,
    )

    day_2_context = StepContext(
        previous_state=day_1_result.new_state,
        daily_inputs=DailyInputs(
            day=2,
            water_temperature_c=25.0,
            tank_volume_l=100.0,
            fish_cohorts=fish_cohorts,
        ),
        daily_event_plan=DailyEventPlan(
            feeding=False,
            water_change=False,
            maintenance=True,
            maintenance_fraction=0.20,
        ),
        frozen_parameter_set=parameter_set,
    )

    day_2_result = DailySimulationEngine.run(
        context=day_2_context,
        filter_unit=filter_unit,
    )

    return opening_state, day_1_result, day_2_result


def test_golden_scenario_two_day_pipeline() -> None:
    """Prove the official two-day scientific pipeline."""
    opening_state, day_1_result, day_2_result = (
        run_golden_scenario()
    )

    assert day_1_result.is_valid
    assert day_2_result.is_valid

    assert opening_state == SimulationState(
        organic_n_mass_mg=0.0,
        tan_mass_mg=8.0,
        nitrite_mass_mg=4.0,
        nitrate_mass_mg=10.0,
    )

    assert day_1_result.new_state.organic_n_mass_mg == pytest.approx(
        10.0
    )
    assert day_1_result.new_state.tan_mass_mg == pytest.approx(6.0)
    assert day_1_result.new_state.nitrite_mass_mg == pytest.approx(
        4.5
    )
    assert day_1_result.new_state.nitrate_mass_mg == pytest.approx(
        12.0
    )

    assert metric_value(
        day_1_result.metrics,
        "water_change_n_removal_mg",
    ) == pytest.approx(5.5)
    assert metric_value(
        day_1_result.metrics,
        "source_water_n_input_mg",
    ) == pytest.approx(4.0)
    assert metric_value(
        day_1_result.metrics,
        "total_feed_nitrogen_mg",
    ) == pytest.approx(10.0)
    assert metric_value(
        day_1_result.metrics,
        "feed_organic_n_input_mg",
    ) == pytest.approx(10.0)
    assert metric_value(
        day_1_result.metrics,
        "organic_n_mineralized_mg",
    ) == pytest.approx(0.0)
    assert metric_value(
        day_1_result.metrics,
        "metabolic_tan_input_mg",
    ) == pytest.approx(2.0)
    assert metric_value(
        day_1_result.metrics,
        "potential_tan_n_oxidized_mg",
    ) == pytest.approx(4.5)
    assert metric_value(
        day_1_result.metrics,
        "tan_n_oxidized_mg",
    ) == pytest.approx(3.0)
    assert metric_value(
        day_1_result.metrics,
        "potential_nitrite_n_oxidized_mg",
    ) == pytest.approx(3.25)
    assert metric_value(
        day_1_result.metrics,
        "nitrite_n_oxidized_mg",
    ) == pytest.approx(2.0)

    assert day_2_result.new_state.organic_n_mass_mg == pytest.approx(
        6.0
    )
    assert day_2_result.new_state.tan_mass_mg == pytest.approx(7.0)
    assert day_2_result.new_state.nitrite_mass_mg == pytest.approx(
        5.5
    )
    assert day_2_result.new_state.nitrate_mass_mg == pytest.approx(
        14.0
    )

    assert metric_value(
        day_2_result.metrics,
        "maintenance_n_removal_mg",
    ) == pytest.approx(2.0)
    assert metric_value(
        day_2_result.metrics,
        "organic_n_mineralized_mg",
    ) == pytest.approx(2.0)
    assert metric_value(
        day_2_result.metrics,
        "metabolic_tan_input_mg",
    ) == pytest.approx(2.0)
    assert metric_value(
        day_2_result.metrics,
        "tan_n_oxidized_mg",
    ) == pytest.approx(3.0)
    assert metric_value(
        day_2_result.metrics,
        "nitrite_n_oxidized_mg",
    ) == pytest.approx(2.0)


def test_golden_scenario_is_deterministic() -> None:
    """Return identical results whenever the same scenario is repeated."""
    first_run = run_golden_scenario()
    second_run = run_golden_scenario()

    assert first_run == second_run