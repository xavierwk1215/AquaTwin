"""Daily simulation metrics."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DailyMetric:
    """Represent one calculated metric during a simulation day."""

    name: str
    value: float
    unit: str