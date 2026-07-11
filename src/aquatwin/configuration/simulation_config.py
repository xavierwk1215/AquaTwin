from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationConfig:
    """Configuration values used for one simulation day."""

    food_mass_g: float
    protein_fraction: float
    nitrogen_conversion_factor: float
    organic_decay_fraction_per_day: float
    tan_oxidation_fraction_per_day: float
    nitrite_oxidation_fraction_per_day: float
    water_change_fraction: float = 0.0