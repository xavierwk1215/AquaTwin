"""Status-based water-quality threshold rule."""

from dataclasses import dataclass

from aquatwin.domain.threshold_range import ThresholdRange
from aquatwin.domain.water_quality_status import WaterQualityStatus


@dataclass(frozen=True, slots=True)
class StatusThreshold:
    """Connect one numeric range to one water-quality status."""

    status: WaterQualityStatus
    value_range: ThresholdRange
    reason: str

    def __post_init__(self) -> None:
        """Validate the threshold rule."""
        if not self.reason.strip():
            raise ValueError("reason must not be empty.")

    def matches(self, value: float) -> bool:
        """Return whether the supplied value matches this rule."""
        return self.value_range.contains(value)