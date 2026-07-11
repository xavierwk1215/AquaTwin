"""Water-quality report domain model."""

from dataclasses import dataclass

from aquatwin.domain.water_quality_evaluation import (
    WaterQualityEvaluation,
)
from aquatwin.domain.water_quality_status import (
    WaterQualityStatus,
)


_STATUS_PRIORITY = {
    WaterQualityStatus.EXCELLENT: 0,
    WaterQualityStatus.ACCEPTABLE: 1,
    WaterQualityStatus.WARNING: 2,
    WaterQualityStatus.CRITICAL: 3,
}


@dataclass(frozen=True, slots=True)
class WaterQualityReport:
    """Aggregate multiple water-quality evaluations."""

    evaluations: tuple[WaterQualityEvaluation, ...]

    def __post_init__(self) -> None:
        """Validate the report."""
        if not self.evaluations:
            raise ValueError(
                "At least one evaluation is required."
            )

    @property
    def overall_status(self) -> WaterQualityStatus:
        """Return the most severe status."""
        return max(
            self.evaluations,
            key=lambda evaluation: _STATUS_PRIORITY[
                evaluation.status
            ],
        ).status

    @property
    def worst_evaluation(self) -> WaterQualityEvaluation:
        """Return the first evaluation with the highest severity."""
        return max(
            self.evaluations,
            key=lambda evaluation: _STATUS_PRIORITY[
                evaluation.status
            ],
        )

    @property
    def requires_attention(self) -> bool:
        """Return whether any evaluation requires attention."""
        return self.overall_status.requires_attention