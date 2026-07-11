"""Build a WaterQualityReport from measured water-quality values."""

from aquatwin.domain.water_quality_evaluation_engine import (
    WaterQualityEvaluationEngine,
)
from aquatwin.domain.water_quality_report import (
    WaterQualityReport,
)
from aquatwin.domain.water_quality_thresholds import (
    WaterQualityThreshold,
)


class WaterQualityReportBuilder:
    """Build a complete water-quality report."""

    def __init__(self) -> None:
        """Initialize the report builder."""
        self._evaluation_engine = WaterQualityEvaluationEngine()

    def build(
        self,
        *,
        measurements: tuple[
            tuple[WaterQualityThreshold, float],
            ...,
        ],
    ) -> WaterQualityReport:
        """Build a report from measured values."""
        if not measurements:
            raise ValueError(
                "At least one measurement is required."
            )

        evaluations = self._evaluation_engine.evaluate_all(
            measurements=measurements,
        )

        return WaterQualityReport(
            evaluations=evaluations,
        )