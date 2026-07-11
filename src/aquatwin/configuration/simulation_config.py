"""Simulation configuration models."""

from dataclasses import dataclass, field

from aquatwin.configuration.water_change_schedule import WaterChangeSchedule


@dataclass(frozen=True)
class SimulationConfig:
    """Configuration values used by the AquaTwin simulation."""

    food_mass_g: float
    protein_fraction: float
    nitrogen_conversion_factor: float
    organic_decay_fraction_per_day: float
    tan_oxidation_fraction_per_day: float
    nitrite_oxidation_fraction_per_day: float
    water_change_fraction: float = 0.0
    water_change_schedule: WaterChangeSchedule = field(
        default_factory=WaterChangeSchedule,
    )