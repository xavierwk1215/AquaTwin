"""Simulation state models."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationState:
    """Represent the immutable closing state of one simulation day."""

    organic_n_mass_mg: float
    tan_mass_mg: float
    nitrite_mass_mg: float
    nitrate_mass_mg: float