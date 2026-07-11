"""Simulation parameter model."""

from dataclasses import dataclass

from aquatwin.domain.value_origin import ValueOrigin


@dataclass(frozen=True)
class SimulationParameter:
    """Represent a quantitative parameter used by the simulator."""

    name: str
    value: float
    unit: str
    origin: ValueOrigin