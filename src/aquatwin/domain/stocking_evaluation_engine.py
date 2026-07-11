"""Engine for evaluating aquarium stocking conditions."""

from collections.abc import Iterable

from aquatwin.domain.stocking import Stocking
from aquatwin.domain.stocking_evaluation import StockingEvaluation
from aquatwin.domain.stocking_status import StockingStatus


class StockingEvaluationEngine:
    """Evaluate aquarium stocking from bioload and estimated capacity."""

    LIGHT_MAX_RATIO = 0.50
    BALANCED_MAX_RATIO = 0.80
    HIGH_MAX_RATIO = 1.00

    def evaluate(
        self,
        stockings: Iterable[Stocking],
        estimated_capacity_g: float,
    ) -> StockingEvaluation:
        """Return the evaluated aquarium stocking condition."""
        stocking_items = tuple(stockings)

        total_adult_weight_g = sum(
            stocking.total_adult_weight_g
            for stocking in stocking_items
        )
        adjusted_bioload_g = sum(
            stocking.adjusted_bioload_g
            for stocking in stocking_items
        )

        capacity_usage_ratio = (
            adjusted_bioload_g / estimated_capacity_g
        )

        status = self._determine_status(
            capacity_usage_ratio=capacity_usage_ratio,
        )

        return StockingEvaluation(
            total_adult_weight_g=total_adult_weight_g,
            adjusted_bioload_g=adjusted_bioload_g,
            estimated_capacity_g=estimated_capacity_g,
            capacity_usage_ratio=capacity_usage_ratio,
            status=status,
            reason=self._create_reason(
                status=status,
                capacity_usage_ratio=capacity_usage_ratio,
            ),
        )

    def _determine_status(
        self,
        capacity_usage_ratio: float,
    ) -> StockingStatus:
        """Return the stocking status for a capacity usage ratio."""
        if capacity_usage_ratio <= self.LIGHT_MAX_RATIO:
            return StockingStatus.LIGHT

        if capacity_usage_ratio <= self.BALANCED_MAX_RATIO:
            return StockingStatus.BALANCED

        if capacity_usage_ratio <= self.HIGH_MAX_RATIO:
            return StockingStatus.HIGH

        return StockingStatus.OVERSTOCKED

    def _create_reason(
        self,
        status: StockingStatus,
        capacity_usage_ratio: float,
    ) -> str:
        """Return an explainable reason for the stocking status."""
        usage_percentage = capacity_usage_ratio * 100

        return (
            f"Adjusted bioload uses approximately "
            f"{usage_percentage:.1f}% of the estimated capacity. "
            f"Stocking status is {status.value}."
        )