"""Frozen parameter set for one reproducible simulation run."""

from dataclasses import dataclass

from aquatwin.domain.simulation_profile import SimulationProfile
from aquatwin.domain.species_simulation_mapping import (
    SpeciesSimulationMapping,
)


@dataclass(frozen=True)
class FrozenParameterSet:
    """Store immutable reference parameters used by one simulation run."""

    model_version: str
    parameter_set_version: str
    simulation_profiles: tuple[SimulationProfile, ...] = ()
    species_simulation_mappings: tuple[
        SpeciesSimulationMapping,
        ...
    ] = ()