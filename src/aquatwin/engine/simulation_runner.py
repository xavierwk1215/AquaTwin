"""Multi-day aquarium simulation orchestration."""

from dataclasses import replace

from aquatwin.configuration.simulation_config import SimulationConfig
from aquatwin.domain.daily_snapshot import DailySnapshot
from aquatwin.domain.tank_state import TankState
from aquatwin.engine.daily_simulator import simulate_day
from aquatwin.engine.snapshot_engine import create_daily_snapshot


class SimulationRunner:
    """Run the AquaTwin daily simulation for multiple consecutive days."""

    def __init__(
        self,
        initial_state: TankState,
        config: SimulationConfig,
    ) -> None:
        self._initial_state = initial_state
        self._config = config

    def run(self, days: int) -> list[DailySnapshot]:
        """Run the simulation."""

        self._validate_days(days)

        current_state = self._initial_state
        snapshots: list[DailySnapshot] = []

        for simulation_day in range(1, days + 1):

            water_change_fraction = (
                self._config.water_change_fraction
                if self._config.water_change_schedule.should_apply(
                    simulation_day
                )
                else 0.0
            )

            daily_config = replace(
                self._config,
                water_change_fraction=water_change_fraction,
            )

            current_state = simulate_day(
                state=current_state,
                config=daily_config,
            )

            snapshots.append(
                create_daily_snapshot(
                    simulation_day=simulation_day,
                    tank_state=current_state,
                )
            )

        return snapshots

    @staticmethod
    def _validate_days(days: int) -> None:
        """Validate simulation duration."""
        if isinstance(days, bool) or not isinstance(days, int):
            raise TypeError("days must be an integer.")

        if days < 1:
            raise ValueError(
                "days must be greater than or equal to 1."
            )
        