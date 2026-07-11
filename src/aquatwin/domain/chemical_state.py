from dataclasses import dataclass


@dataclass(frozen=True)
class ChemicalState:
    """Represents tracked nitrogen masses at a single simulation point."""

    organic_n_mass_mg: float
    tan_n_mass_mg: float
    nitrite_n_mass_mg: float
    nitrate_n_mass_mg: float