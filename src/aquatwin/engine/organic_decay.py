from aquatwin.domain.chemical_state import ChemicalState
from aquatwin.domain.tank_state import TankState

def apply_organic_decay(
    state: TankState,
    decay_fraction_per_day: float,
) -> TankState:
    """Move part of Organic-N mass to TAN-N."""

    if not 0.0 <= decay_fraction_per_day <= 1.0:
        raise ValueError(
            "decay_fraction_per_day must be between 0.0 and 1.0."
        )

    decayed_mass_mg = (
        state.chemical_state.organic_n_mass_mg
        * decay_fraction_per_day
    )

    next_chemical_state = ChemicalState(
        organic_n_mass_mg=(
            state.chemical_state.organic_n_mass_mg
            - decayed_mass_mg
        ),
        tan_n_mass_mg=(
            state.chemical_state.tan_n_mass_mg
            + decayed_mass_mg
        ),
        nitrite_n_mass_mg=(
            state.chemical_state.nitrite_n_mass_mg
        ),
        nitrate_n_mass_mg=(
            state.chemical_state.nitrate_n_mass_mg
        ),
    )

    return TankState(
        chemical_state=next_chemical_state,
        effective_water_volume_l=state.effective_water_volume_l,
        temperature_c=state.temperature_c,
        ph=state.ph,
    )