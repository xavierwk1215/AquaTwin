"""Tests for FrozenParameterSet."""

from aquatwin.domain.frozen_parameter_set import (
    FrozenParameterSet,
)
from aquatwin.domain.simulation_parameter import (
    SimulationParameter,
)
from aquatwin.domain.simulation_profile import (
    SimulationProfile,
)
from aquatwin.domain.species_simulation_mapping import (
    SpeciesSimulationMapping,
)
from aquatwin.domain.value_origin import ValueOrigin


def _parameter(
    name: str,
    value: float,
) -> SimulationParameter:
    """Create a simulation parameter."""
    return SimulationParameter(
        name=name,
        value=value,
        unit="unit",
        origin=ValueOrigin.OBSERVED,
    )


def _profile() -> SimulationProfile:
    """Create a simulation profile."""
    return SimulationProfile(
        profile_id="small_tetra_v1",
        name="Small Tetra",
        adult_weight=_parameter("adult_weight", 2.0),
        daily_feed_ratio=_parameter("daily_feed_ratio", 0.02),
        digestibility=_parameter("digestibility", 0.85),
        nitrogen_fraction=_parameter("nitrogen_fraction", 0.16),
        oxygen_consumption=_parameter("oxygen_consumption", 1.0),
        waste_factor=_parameter("waste_factor", 1.0),
    )


def _mapping() -> SpeciesSimulationMapping:
    """Create a species mapping."""
    return SpeciesSimulationMapping(
        species_id="neon_tetra",
        simulation_profile_id="small_tetra_v1",
    )


def test_store_versions() -> None:
    """Store model and parameter versions."""
    frozen = FrozenParameterSet(
        model_version="0.1.0",
        parameter_set_version="species-v1",
    )

    assert frozen.model_version == "0.1.0"
    assert frozen.parameter_set_version == "species-v1"


def test_store_profiles() -> None:
    """Store simulation profiles."""
    profile = _profile()

    frozen = FrozenParameterSet(
        model_version="0.1.0",
        parameter_set_version="species-v1",
        simulation_profiles=(profile,),
    )

    assert frozen.simulation_profiles == (profile,)


def test_store_species_mappings() -> None:
    """Store species simulation mappings."""
    mapping = _mapping()

    frozen = FrozenParameterSet(
        model_version="0.1.0",
        parameter_set_version="species-v1",
        species_simulation_mappings=(mapping,),
    )

    assert frozen.species_simulation_mappings == (
        mapping,
    )