"""Water quality evaluation domain model."""

from dataclasses import dataclass
from math import isfinite

from aquatwin.domain.water_quality_status import WaterQualityStatus


@dataclass(frozen=True, slots=True)
class WaterQualityEvaluation:
    """Represents the evaluation result of one water-quality parameter."""

    parameter_name: str
    measured_value: float
    unit: str
    status: WaterQualityStatus
    reason: str

    def __post_init__(self) -> None:
        """Validate evaluation data."""
        if not self.parameter_name.strip():
            raise ValueError("parameter_name must not be empty.")

        if not self.unit.strip():
            raise ValueError("unit must not be empty.")

        if not self.reason.strip():
            raise ValueError("reason must not be empty.")

        if not isfinite(self.measured_value):
            raise ValueError("measured_value must be a finite number.")