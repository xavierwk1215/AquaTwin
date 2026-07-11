"""Tests for FeedNitrogenEngine."""

import pytest

from aquatwin.domain.fish_cohort import FishCohort
from aquatwin.domain.frozen_parameter_set import FrozenParameterSet
from aquatwin.domain.simulation_parameter import SimulationParameter
from aquatwin.domain.simulation_profile import SimulationProfile
from aquatwin.domain.species_simulation_mapping import (
    SpeciesSimulationMapping,
)
from aquatwin.domain.value_origin import ValueOrigin
from aquatwin.engine.feed_nitrogen_engine import (
    FeedNitrogenEngine,
)


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


def make_frozen_parameter_set(
    *,
    adult_weight: float = 2.5,
    daily_feed_ratio: float = 0.02,
    nitrogen_fraction: float = 0.08,
) -> FrozenParameterSet:
    profile = SimulationProfile(
        profile_id="profile_1",
        name="Test Profile",
        adult_weight=make_parameter(
            "adult_weight",
            adult_weight,
            "g",
        ),
        daily_feed_ratio=make_parameter(
            "daily_feed_ratio",
            daily_feed_ratio,
            "ratio/day",
        ),
        digestibility=make_parameter(
            "digestibility",
            0.8,
            "ratio",
        ),
        nitrogen_fraction=make_parameter(
            "nitrogen_fraction",
            nitrogen_fraction,
            "ratio",
        ),
        oxygen_consumption=make_parameter(
            "oxygen_consumption",
            0.2,
            "mg-O2/g/day",
        ),
        waste_factor=make_parameter(
            "waste_factor",
            0.2,
            "ratio",
        ),
    )

    return FrozenParameterSet(
        model_version="test-model",
        parameter_set_version="test-parameters",
        simulation_profiles=(profile,),
        species_simulation_mappings=(
            SpeciesSimulationMapping(
                species_id="neon_tetra",
                simulation_profile_id="profile_1",
            ),
        ),
    )


def test_calculate_total_feed_mass() -> None:
    frozen = make_frozen_parameter_set()

    result = FeedNitrogenEngine.calculate_total_feed_mass_g(
        cohorts=(
            FishCohort(
                species_id="neon_tetra",
                count=20,
            ),
        ),
        frozen_parameter_set=frozen,
    )

    assert result == pytest.approx(1.0)


def test_calculate_total_feed_nitrogen() -> None:
    frozen = make_frozen_parameter_set()

    result = FeedNitrogenEngine.calculate_total_feed_nitrogen_mg(
        cohorts=(
            FishCohort(
                species_id="neon_tetra",
                count=20,
            ),
        ),
        frozen_parameter_set=frozen,
    )

    assert result == pytest.approx(80.0)


def test_empty_cohorts_return_zero() -> None:
    frozen = make_frozen_parameter_set()

    assert (
        FeedNitrogenEngine.calculate_total_feed_mass_g(
            cohorts=(),
            frozen_parameter_set=frozen,
        )
        == pytest.approx(0.0)
    )

    assert (
        FeedNitrogenEngine.calculate_total_feed_nitrogen_mg(
            cohorts=(),
            frozen_parameter_set=frozen,
        )
        == pytest.approx(0.0)
    )


@pytest.mark.parametrize(
    "nitrogen_fraction",
    [-0.1, 1.1],
)
def test_invalid_nitrogen_fraction_raises(
    nitrogen_fraction: float,
) -> None:
    frozen = make_frozen_parameter_set(
        nitrogen_fraction=nitrogen_fraction,
    )

    with pytest.raises(
        ValueError,
        match="Nitrogen fraction must be between 0.0 and 1.0.",
    ):
        FeedNitrogenEngine.calculate_total_feed_nitrogen_mg(
            cohorts=(
                FishCohort(
                    species_id="neon_tetra",
                    count=20,
                ),
            ),
            frozen_parameter_set=frozen,
        )