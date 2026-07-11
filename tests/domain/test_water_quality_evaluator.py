"""Tests for the water-quality evaluator."""

import pytest

from aquatwin.domain.status_threshold import StatusThreshold
from aquatwin.domain.threshold_range import ThresholdRange
from aquatwin.domain.water_quality_evaluator import WaterQualityEvaluator
from aquatwin.domain.water_quality_status import WaterQualityStatus
from aquatwin.domain.water_quality_thresholds import WaterQualityThreshold


@pytest.fixture
def tan_threshold() -> WaterQualityThreshold:
    """Return a sample TAN threshold configuration."""
    return WaterQualityThreshold(
        parameter_name="TAN",
        unit="mg-N/L",
        thresholds=(
            StatusThreshold(
                status=WaterQualityStatus.EXCELLENT,
                value_range=ThresholdRange(
                    minimum=0.0,
                    maximum=0.1,
                ),
                reason="TAN is within the preferred operating range.",
            ),
            StatusThreshold(
                status=WaterQualityStatus.ACCEPTABLE,
                value_range=ThresholdRange(
                    minimum=0.100001,
                    maximum=0.25,
                ),
                reason="TAN is acceptable but should be monitored.",
            ),
            StatusThreshold(
                status=WaterQualityStatus.WARNING,
                value_range=ThresholdRange(
                    minimum=0.250001,
                    maximum=0.5,
                ),
                reason="TAN is above the preferred operating range.",
            ),
            StatusThreshold(
                status=WaterQualityStatus.CRITICAL,
                value_range=ThresholdRange(
                    minimum=0.500001,
                    maximum=10.0,
                ),
                reason="TAN is at a critical concentration.",
            ),
        ),
    )


def test_evaluate_returns_matching_evaluation(
    tan_threshold: WaterQualityThreshold,
) -> None:
    """Evaluator should return the status and reason of the matching rule."""
    evaluator = WaterQualityEvaluator()

    evaluation = evaluator.evaluate(
        threshold=tan_threshold,
        measured_value=0.3,
    )

    assert evaluation.parameter_name == "TAN"
    assert evaluation.measured_value == pytest.approx(0.3)
    assert evaluation.unit == "mg-N/L"
    assert evaluation.status is WaterQualityStatus.WARNING
    assert evaluation.reason == (
        "TAN is above the preferred operating range."
    )


def test_evaluate_uses_inclusive_range_boundaries(
    tan_threshold: WaterQualityThreshold,
) -> None:
    """Evaluator should include exact minimum and maximum boundaries."""
    evaluator = WaterQualityEvaluator()

    minimum_evaluation = evaluator.evaluate(
        threshold=tan_threshold,
        measured_value=0.0,
    )
    maximum_evaluation = evaluator.evaluate(
        threshold=tan_threshold,
        measured_value=0.1,
    )

    assert minimum_evaluation.status is WaterQualityStatus.EXCELLENT
    assert maximum_evaluation.status is WaterQualityStatus.EXCELLENT


def test_evaluate_raises_error_when_no_threshold_matches(
    tan_threshold: WaterQualityThreshold,
) -> None:
    """Evaluator should reject values outside all configured rules."""
    evaluator = WaterQualityEvaluator()

    with pytest.raises(
        ValueError,
        match="No threshold matched",
    ):
        evaluator.evaluate(
            threshold=tan_threshold,
            measured_value=11.0,
        )