"""Multi-day aquarium simulation orchestration."""

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
        """Initialize the simulation runner.

        Args:
            initial_state:
                The immutable tank state used as the starting point
                of the simulation.

            config:
                Configuration values used for each simulated day.
        """
        self._initial_state = initial_state
        self._config = config

    def run(self, days: int) -> list[DailySnapshot]:
        """Run the simulation and return one snapshot for each simulated day.

        Args:
            days:
                Number of consecutive days to simulate.

        Returns:
            A list containing one DailySnapshot for every simulated day.

        Raises:
            TypeError:
                If days is not an integer.

            ValueError:
                If days is less than one.
        """
        self._validate_days(days)

        current_state = self._initial_state
        snapshots: list[DailySnapshot] = []

        for simulation_day in range(1, days + 1):
            current_state = simulate_day(
                state=current_state,
                config=self._config,
            )

            snapshot = create_daily_snapshot(
                simulation_day=simulation_day,
                tank_state=current_state,
            )

            snapshots.append(snapshot)

        return snapshots

    @staticmethod
    def _validate_days(days: int) -> None:
        """Validate the requested simulation duration."""
        if isinstance(days, bool) or not isinstance(days, int):
            raise TypeError("days must be an integer.")

        if days < 1:
            raise ValueError("days must be greater than or equal to 1.")