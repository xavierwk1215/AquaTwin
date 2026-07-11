from dataclasses import dataclass

from aquatwin.domain.tank_state import TankState


@dataclass(frozen=True)
class DailySnapshot:
    """Immutable snapshot of the tank state for a simulation day."""

    simulation_day: int
    tank_state: TankState