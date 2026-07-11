"""Mapping between a species and a simulation profile."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SpeciesSimulationMapping:
    """Link one aquarium species to one simulation profile."""

    species_id: str
    simulation_profile_id: str