"""Run one complete day of the AquaTwin simulation."""

from dataclasses import replace

from aquatwin.configuration.simulation_config import SimulationConfig
from aquatwin.domain.tank_state import TankState
from aquatwin.engine.feeding_engine import FeedingEngine
from aquatwin.engine.nitrite_oxidation import apply_nitrite_oxidation
from aquatwin.engine.organic_decay import apply_organic_decay
from aquatwin.engine.tan_oxidation import apply_tan_oxidation
from aquatwin.engine.water_change import apply_water_change


def simulate_day(
    state: TankState,
    config: SimulationConfig,
) -> TankState:
    """Run all currently implemented daily simulation steps.

    The simulation applies each process in a fixed deterministic order:

    1. Feeding adds Organic-N.
    2. Organic decay converts part of Organic-N into TAN-N.
    3. TAN oxidation converts part of TAN-N into Nitrite-N.
    4. Nitrite oxidation converts part of Nitrite-N into Nitrate-N.
    5. Water change removes the configured fraction of all nitrogen masses.

    Args:
        state:
            Immutable tank state at the beginning of the simulation day.

        config:
            Configuration values used for the daily simulation.

    Returns:
        A new TankState containing the state at the end of the day.
    """
    organic_n_added_mg = FeedingEngine.calculate_organic_n(
        food_mass_g=config.food_mass_g,
        protein_fraction=config.protein_fraction,
        nitrogen_conversion_factor=config.nitrogen_conversion_factor,
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
        decay_fraction_per_day=config.organic_decay_fraction_per_day,
    )

    state_after_tan_oxidation = apply_tan_oxidation(
        state_after_organic_decay,
        oxidation_fraction_per_day=config.tan_oxidation_fraction_per_day,
    )

    state_after_nitrite_oxidation = apply_nitrite_oxidation(
        state_after_tan_oxidation,
        oxidation_fraction_per_day=config.nitrite_oxidation_fraction_per_day,
    )

    state_after_water_change = apply_water_change(
        state_after_nitrite_oxidation,
        water_change_fraction=config.water_change_fraction,
    )

    return state_after_water_change