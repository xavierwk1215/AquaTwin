"""Water-quality threshold configuration domain model."""

from dataclasses import dataclass

from aquatwin.domain.status_threshold import StatusThreshold


@dataclass(frozen=True, slots=True)
class WaterQualityThreshold:
    """Threshold configuration for one water-quality parameter."""

    parameter_name: str
    unit: str
    thresholds: tuple[StatusThreshold, ...]

    def __post_init__(self) -> None:
        """Validate the threshold configuration."""
        if not self.parameter_name.strip():
            raise ValueError("parameter_name must not be empty.")

        if not self.unit.strip():
            raise ValueError("unit must not be empty.")

        if not self.thresholds:
            raise ValueError("At least one threshold is required.")

    def find_matching_threshold(
        self,
        value: float,
    ) -> StatusThreshold | None:
        """Return the first threshold rule matching the supplied value."""
        for threshold in self.thresholds:
            if threshold.matches(value):
                return threshold

        return None