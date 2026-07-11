from aquatwin.domain.daily_snapshot import DailySnapshot
from aquatwin.domain.tank_state import TankState


def create_daily_snapshot(
    simulation_day: int,
    tank_state: TankState,
) -> DailySnapshot:
    """Create an immutable snapshot for a simulation day."""

    return DailySnapshot(
        simulation_day=simulation_day,
        tank_state=tank_state,
    )