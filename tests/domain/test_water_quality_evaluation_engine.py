"""Tests for the water-quality evaluation engine."""

import pytest

from aquatwin.domain.status_threshold import StatusThreshold
from aquatwin.domain.threshold_range import ThresholdRange
from aquatwin.domain.water_quality_evaluation_engine import (
    WaterQualityEvaluationEngine,
)
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
                status=WaterQualityStatus.WARNING,
                value_range=ThresholdRange(
                    minimum=0.100001,
                    maximum=1.0,
                ),
                reason="TAN is above the preferred operating range.",
            ),
        ),
    )


@pytest.fixture
def nitrite_threshold() -> WaterQualityThreshold:
    """Return a sample nitrite threshold configuration."""
    return WaterQualityThreshold(
        parameter_name="Nitrite",
        unit="mg-N/L",
        thresholds=(
            StatusThreshold(
                status=WaterQualityStatus.EXCELLENT,
                value_range=ThresholdRange(
                    minimum=0.0,
                    maximum=0.05,
                ),
                reason="Nitrite is within the preferred operating range.",
            ),
            StatusThreshold(
                status=WaterQualityStatus.CRITICAL,
                value_range=ThresholdRange(
                    minimum=0.050001,
                    maximum=1.0,
                ),
                reason="Nitrite is at a critical concentration.",
            ),
        ),
    )


def test_evaluate_all_returns_all_evaluations(
    tan_threshold: WaterQualityThreshold,
    nitrite_threshold: WaterQualityThreshold,
) -> None:
    """All configured measurements should be evaluated."""
    engine = WaterQualityEvaluationEngine()

    evaluations = engine.evaluate_all(
        measurements=(
            (tan_threshold, 0.2),
            (nitrite_threshold, 0.02),
        ),
    )

    assert len(evaluations) == 2

    assert evaluations[0].parameter_name == "TAN"
    assert evaluations[0].status is WaterQualityStatus.WARNING

    assert evaluations[1].parameter_name == "Nitrite"
    assert evaluations[1].status is WaterQualityStatus.EXCELLENT


def test_evaluate_all_preserves_input_order(
    tan_threshold: WaterQualityThreshold,
    nitrite_threshold: WaterQualityThreshold,
) -> None:
    """Evaluation order should match measurement input order."""
    engine = WaterQualityEvaluationEngine()

    evaluations = engine.evaluate_all(
        measurements=(
            (nitrite_threshold, 0.02),
            (tan_threshold, 0.2),
        ),
    )

    assert evaluations[0].parameter_name == "Nitrite"
    assert evaluations[1].parameter_name == "TAN"


def test_evaluate_all_returns_empty_tuple_for_no_measurements() -> None:
    """An empty measurement collection should return an empty result."""
    engine = WaterQualityEvaluationEngine()

    evaluations = engine.evaluate_all(
        measurements=(),
    )

    assert evaluations == ()


def test_evaluate_all_propagates_evaluation_errors(
    tan_threshold: WaterQualityThreshold,
) -> None:
    """Invalid measurements should not be silently ignored."""
    engine = WaterQualityEvaluationEngine()

    with pytest.raises(
        ValueError,
        match="No threshold matched",
    ):
        engine.evaluate_all(
            measurements=(
                (tan_threshold, 5.0),
            ),
        )