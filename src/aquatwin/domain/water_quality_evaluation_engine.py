"""Water-quality evaluation engine."""

from aquatwin.domain.water_quality_evaluation import (
    WaterQualityEvaluation,
)
from aquatwin.domain.water_quality_evaluator import (
    WaterQualityEvaluator,
)
from aquatwin.domain.water_quality_thresholds import (
    WaterQualityThreshold,
)


class WaterQualityEvaluationEngine:
    """Coordinate the evaluation of multiple water-quality parameters."""

    def __init__(self) -> None:
        """Initialize the engine."""
        self._evaluator = WaterQualityEvaluator()

    def evaluate_all(
        self,
        *,
        measurements: tuple[
            tuple[WaterQualityThreshold, float],
            ...,
        ],
    ) -> tuple[WaterQualityEvaluation, ...]:
        """Evaluate all supplied measurements."""

        evaluations: list[WaterQualityEvaluation] = []

        for threshold, measured_value in measurements:
            evaluation = self._evaluator.evaluate(
                threshold=threshold,
                measured_value=measured_value,
            )

            evaluations.append(evaluation)

        return tuple(evaluations)