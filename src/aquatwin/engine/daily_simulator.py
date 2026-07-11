from dataclasses import replace

from aquatwin.domain.tank_state import TankState
from aquatwin.engine.feeding_engine import FeedingEngine
from aquatwin.engine.nitrite_oxidation import apply_nitrite_oxidation
from aquatwin.engine.organic_decay import apply_organic_decay
from aquatwin.engine.tan_oxidation import apply_tan_oxidation

def simulate_day(
    state: TankState,
    food_mass_g: float,
    protein_fraction: float,
    nitrogen_conversion_factor: float,
    organic_decay_fraction_per_day: float,
    tan_oxidation_fraction_per_day: float,
    nitrite_oxidation_fraction_per_day: float,
) -> TankState:
    """Run the currently implemented daily simulation steps."""

    organic_n_added_mg = FeedingEngine.calculate_organic_n(
        food_mass_g=food_mass_g,
        protein_fraction=protein_fraction,
        nitrogen_conversion_factor=nitrogen_conversion_factor,
    )

    chemical_state_after_feeding = replace(
        state.chemical_state,
        organic_n_mass_mg=(
            state.chemical_state.organic_n_mass_mg + organic_n_added_mg
        ),
    )

    state_after_feeding = replace(
        state,
        chemical_state=chemical_state_after_feeding,
    )

    state_after_organic_decay = apply_organic_decay(
        state_after_feeding,
        decay_fraction_per_day=organic_decay_fraction_per_day,
    )

    state_after_tan_oxidation = apply_tan_oxidation(
        state_after_organic_decay,
        oxidation_fraction_per_day=tan_oxidation_fraction_per_day,
    )

    state_after_nitrite_oxidation = apply_nitrite_oxidation(
        state_after_tan_oxidation,
        oxidation_fraction_per_day=nitrite_oxidation_fraction_per_day,
    )

    return state_after_nitrite_oxidation