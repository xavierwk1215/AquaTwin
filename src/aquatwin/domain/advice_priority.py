"""Priority levels for advisor recommendations."""

from enum import IntEnum


class AdvicePriority(IntEnum):
    """Priority of an advisor recommendation.

    Higher values indicate higher urgency.
    """

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

    @property
    def requires_immediate_action(self) -> bool:
        """Return whether this priority requires immediate action."""
        return self >= AdvicePriority.HIGH