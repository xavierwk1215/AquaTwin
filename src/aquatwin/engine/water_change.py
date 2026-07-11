from dataclasses import replace

from aquatwin.domain.tank_state import TankState


def apply_water_change(
    state: TankState,
    water_change_fraction: float,
) -> TankState:
    """Reduce all tracked nitrogen masses by the water-change fraction."""

    if not 0.0 <= water_change_fraction <= 1.0:
        raise ValueError("water_change_fraction must be between 0.0 and 1.0")

    remaining_fraction = 1.0 - water_change_fraction

    updated_chemical_state = replace(
        state.chemical_state,
        organic_n_mass_mg=(
            state.chemical_state.organic_n_mass_mg * remaining_fraction
        ),
        tan_n_mass_mg=(
            state.chemical_state.tan_n_mass_mg * remaining_fraction
        ),
        nitrite_n_mass_mg=(
            state.chemical_state.nitrite_n_mass_mg * remaining_fraction
        ),
        nitrate_n_mass_mg=(
            state.chemical_state.nitrate_n_mass_mg * remaining_fraction
        ),
    )

    return replace(
        state,
        chemical_state=updated_chemical_state,
    )