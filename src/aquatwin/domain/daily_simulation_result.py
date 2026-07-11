"""Official result of one completed daily simulation step."""

from dataclasses import dataclass

from aquatwin.domain.metrics import DailyMetric
from aquatwin.domain.state import SimulationState
from aquatwin.validation.validation_result import ValidationResult


@dataclass(frozen=True)
class DailySimulationResult:
    """Store the validated output of one simulation day."""

    simulation_day: int
    new_state: SimulationState
    metrics: tuple[DailyMetric, ...]
    validation_result: ValidationResult

    @property
    def is_valid(self) -> bool:
        """Return whether the completed daily step passed validation."""
        return self.validation_result.is_valid