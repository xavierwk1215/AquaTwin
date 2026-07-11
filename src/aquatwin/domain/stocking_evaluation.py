"""Stocking evaluation domain model."""

from dataclasses import dataclass

from aquatwin.domain.stocking_status import StockingStatus


@dataclass(frozen=True)
class StockingEvaluation:
    """Represent the evaluated stocking condition of an aquarium."""

    total_adult_weight_g: float
    adjusted_bioload_g: float
    estimated_capacity_g: float
    capacity_usage_ratio: float
    status: StockingStatus
    reason: str