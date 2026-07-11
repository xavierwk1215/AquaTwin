"""Daily operational event plan."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DailyEventPlan:
    """Represent resolved operational events for one simulation day."""

    feeding: bool
    water_change: bool
    maintenance: bool

    water_change_fraction: float = 0.0
    maintenance_fraction: float = 0.0