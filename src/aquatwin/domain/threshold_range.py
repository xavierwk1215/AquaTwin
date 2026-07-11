"""Reusable numeric threshold range domain model."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class ThresholdRange:
    """Inclusive finite numeric range."""

    minimum: float
    maximum: float

    def __post_init__(self) -> None:
        """Validate the range boundaries."""
        if not isfinite(self.minimum):
            raise ValueError("minimum must be a finite number.")

        if not isfinite(self.maximum):
            raise ValueError("maximum must be a finite number.")

        if self.minimum > self.maximum:
            raise ValueError(
                "minimum must be less than or equal to maximum."
            )

    def contains(self, value: float) -> bool:
        """Return whether a finite value belongs to this inclusive range."""
        if not isfinite(value):
            return False

        return self.minimum <= value <= self.maximum