"""Water-quality evaluation service."""

from math import isfinite

from aquatwin.domain.water_quality_evaluation import WaterQualityEvaluation
from aquatwin.domain.water_quality_thresholds import WaterQualityThreshold


class WaterQualityEvaluator:
    """Evaluate one measured value against a threshold configuration."""

    def evaluate(
        self,
        *,
        threshold: WaterQualityThreshold,
        measured_value: float,
    ) -> WaterQualityEvaluation:
        """Return the evaluation for the first matching threshold rule."""
        if not isfinite(measured_value):
            raise ValueError("measured_value must be a finite number.")

        matched_threshold = threshold.find_matching_threshold(
            measured_value
        )

        if matched_threshold is None:
            raise ValueError(
                "No threshold matched "
                f"{threshold.parameter_name} value {measured_value}."
            )

        return WaterQualityEvaluation(
            parameter_name=threshold.parameter_name,
            measured_value=measured_value,
            unit=threshold.unit,
            status=matched_threshold.status,
            reason=matched_threshold.reason,
        )