from dataclasses import dataclass

from aquatwin.domain.chemical_state import ChemicalState


@dataclass(frozen=True)
class TankState:
    """Represents the immutable state of a tank at one simulation point."""

    chemical_state: ChemicalState
    effective_water_volume_l: float
    temperature_c: float
    ph: float