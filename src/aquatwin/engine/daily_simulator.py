from aquatwin.domain.tank_state import TankState
from aquatwin.engine.organic_decay import apply_organic_decay
from aquatwin.engine.tan_oxidation import apply_tan_oxidation


def simulate_day(
    state: TankState,
    organic_decay_fraction_per_day: float,
    tan_oxidation_fraction_per_day: float,
) -> TankState:
    """Run the currently implemented daily simulation steps."""

    state_after_organic_decay = apply_organic_decay(
        state,
        decay_fraction_per_day=organic_decay_fraction_per_day,
    )

    state_after_tan_oxidation = apply_tan_oxidation(
        state_after_organic_decay,
        oxidation_fraction_per_day=tan_oxidation_fraction_per_day,
    )

    return state_after_tan_oxidation