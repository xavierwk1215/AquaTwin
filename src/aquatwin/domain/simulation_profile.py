"""Simulation profile model."""

from dataclasses import dataclass

from aquatwin.domain.simulation_parameter import SimulationParameter


@dataclass(frozen=True)
class SimulationProfile:
    """Represent a reusable biological simulation profile."""

    profile_id: str
    name: str

    adult_weight: SimulationParameter
    daily_feed_ratio: SimulationParameter
    digestibility: SimulationParameter
    nitrogen_fraction: SimulationParameter
    oxygen_consumption: SimulationParameter
    waste_factor: SimulationParameter

    metabolic_tan_excretion: SimulationParameter | None = None