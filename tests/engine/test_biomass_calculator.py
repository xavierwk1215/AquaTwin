"""Tests for BiomassCalculator."""

import pytest

from aquatwin.domain.fish_cohort import FishCohort
from aquatwin.domain.frozen_parameter_set import FrozenParameterSet
from aquatwin.domain.simulation_parameter import SimulationParameter
from aquatwin.domain.simulation_profile import SimulationProfile
from aquatwin.domain.species_simulation_mapping import (
    SpeciesSimulationMapping,
)
from aquatwin.domain.value_origin import ValueOrigin
from aquatwin.engine.biomass_calculator import BiomassCalculator


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
    adult_weight_g: float = 2.5,
) -> FrozenParameterSet:
    return FrozenParameterSet(
        model_version="test-model",
        parameter_set_version="test-parameters",
        simulation_profiles=[
            SimulationProfile(
                profile_id="profile_1",
                name="Test Profile",
                adult_weight=make_parameter(
                    name="adult_weight",
                    value=adult_weight_g,
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
        ],
        species_simulation_mappings=[
            SpeciesSimulationMapping(
                species_id="neon_tetra",
                simulation_profile_id="profile_1",
            )
        ],
    )


def test_calculate_total_biomass() -> None:
    frozen = make_frozen_parameter_set()

    biomass = BiomassCalculator.calculate_total_biomass_g(
        cohorts=[
            FishCohort(
                species_id="neon_tetra",
                count=20,
            )
        ],
        frozen_parameter_set=frozen,
    )

    assert biomass == pytest.approx(50.0)


def test_empty_cohort_returns_zero() -> None:
    frozen = make_frozen_parameter_set()

    biomass = BiomassCalculator.calculate_total_biomass_g(
        cohorts=[],
        frozen_parameter_set=frozen,
    )

    assert biomass == pytest.approx(0.0)


def test_missing_species_mapping_raises() -> None:
    frozen = make_frozen_parameter_set()

    with pytest.raises(
        ValueError,
        match="No simulation profile mapping found",
    ):
        BiomassCalculator.calculate_total_biomass_g(
            cohorts=[
                FishCohort(
                    species_id="unknown_species",
                    count=5,
                )
            ],
            frozen_parameter_set=frozen,
        )


def test_missing_profile_raises() -> None:
    frozen = FrozenParameterSet(
        model_version="test-model",
        parameter_set_version="test-parameters",
        simulation_profiles=[],
        species_simulation_mappings=[
            SpeciesSimulationMapping(
                species_id="neon_tetra",
                simulation_profile_id="missing_profile",
            )
        ],
    )

    with pytest.raises(
        ValueError,
        match="Simulation profile not found",
    ):
        BiomassCalculator.calculate_total_biomass_g(
            cohorts=[
                FishCohort(
                    species_id="neon_tetra",
                    count=10,
                )
            ],
            frozen_parameter_set=frozen,
        )


def test_negative_adult_weight_raises() -> None:
    frozen = make_frozen_parameter_set(
        adult_weight_g=-1.0,
    )

    with pytest.raises(
        ValueError,
        match="Adult weight must be non-negative.",
    ):
        BiomassCalculator.calculate_total_biomass_g(
            cohorts=[
                FishCohort(
                    species_id="neon_tetra",
                    count=10,
                )
            ],
            frozen_parameter_set=frozen,
        )