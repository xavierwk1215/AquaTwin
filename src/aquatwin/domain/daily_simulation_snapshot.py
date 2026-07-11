"""Persistable snapshot of one validated simulation day."""

from dataclasses import dataclass

from aquatwin.domain.metrics import DailyMetric
from aquatwin.domain.state import SimulationState


@dataclass(frozen=True)
class DailySimulationSnapshot:
    """Store one simulation day's immutable historical record."""

    run_id: str
    simulation_day: int
    tank_volume_l: float
    state: SimulationState
    metrics: tuple[DailyMetric, ...]
    validation_passed: bool

    def __post_init__(self) -> None:
        """Validate snapshot identity and physical values."""
        if not isinstance(self.run_id, str):
            raise TypeError("run_id must be a string.")

        if not self.run_id.strip():
            raise ValueError("run_id must not be empty.")

        if isinstance(self.simulation_day, bool) or not isinstance(
            self.simulation_day,
            int,
        ):
            raise TypeError("simulation_day must be an integer.")

        if self.simulation_day < 1:
            raise ValueError(
                "simulation_day must be greater than or equal to 1."
            )

        if isinstance(self.tank_volume_l, bool) or not isinstance(
            self.tank_volume_l,
            (int, float),
        ):
            raise TypeError("tank_volume_l must be numeric.")

        if self.tank_volume_l <= 0:
            raise ValueError(
                "tank_volume_l must be greater than zero."
            )

        if not isinstance(self.state, SimulationState):
            raise TypeError("state must be a SimulationState.")

        if not isinstance(self.metrics, tuple):
            raise TypeError("metrics must be a tuple.")

        if not all(
            isinstance(metric, DailyMetric)
            for metric in self.metrics
        ):
            raise TypeError(
                "metrics must contain only DailyMetric objects."
            )

        if not isinstance(self.validation_passed, bool):
            raise TypeError("validation_passed must be a boolean.")

    @property
    def organic_n_mg_n_l(self) -> float:
        """Return Organic-N concentration."""
        return self.state.organic_n_mass_mg / self.tank_volume_l

    @property
    def tan_mg_n_l(self) -> float:
        """Return TAN-N concentration."""
        return self.state.tan_mass_mg / self.tank_volume_l

    @property
    def nitrite_mg_n_l(self) -> float:
        """Return nitrite-N concentration."""
        return self.state.nitrite_mass_mg / self.tank_volume_l

    @property
    def nitrate_mg_n_l(self) -> float:
        """Return nitrate-N concentration."""
        return self.state.nitrate_mass_mg / self.tank_volume_l

    @property
    def total_nitrogen_mass_mg(self) -> float:
        """Return the total tracked nitrogen mass."""
        return (
            self.state.organic_n_mass_mg
            + self.state.tan_mass_mg
            + self.state.nitrite_mass_mg
            + self.state.nitrate_mass_mg
        )