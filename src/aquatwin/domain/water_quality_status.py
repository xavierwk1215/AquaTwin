"""Water quality status definitions."""

from enum import Enum


class WaterQualityStatus(str, Enum):
    """Possible evaluation results for a water-quality parameter."""

    EXCELLENT = "Excellent"
    ACCEPTABLE = "Acceptable"
    WARNING = "Warning"
    CRITICAL = "Critical"

    @property
    def is_safe(self) -> bool:
        """Return whether the status is considered safe."""
        return self in (
            WaterQualityStatus.EXCELLENT,
            WaterQualityStatus.ACCEPTABLE,
        )

    @property
    def requires_attention(self) -> bool:
        """Return whether the status requires user attention."""
        return self in (
            WaterQualityStatus.WARNING,
            WaterQualityStatus.CRITICAL,
        )