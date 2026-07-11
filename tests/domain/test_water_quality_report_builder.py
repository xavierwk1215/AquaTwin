"""Tests for the water-quality report builder."""

import pytest

from aquatwin.domain.status_threshold import StatusThreshold
from aquatwin.domain.threshold_range import ThresholdRange
from aquatwin.domain.water_quality_report_builder import (
    WaterQualityReportBuilder,
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


def test_build_returns_report_with_all_evaluations(
    tan_threshold: WaterQualityThreshold,
    nitrite_threshold: WaterQualityThreshold,
) -> None:
    """Builder should evaluate every measurement and create a report."""
    builder = WaterQualityReportBuilder()

    report = builder.build(
        measurements=(
            (tan_threshold, 0.2),
            (nitrite_threshold, 0.02),
        ),
    )

    assert len(report.evaluations) == 2
    assert report.evaluations[0].parameter_name == "TAN"
    assert report.evaluations[1].parameter_name == "Nitrite"


def test_build_calculates_overall_status(
    tan_threshold: WaterQualityThreshold,
    nitrite_threshold: WaterQualityThreshold,
) -> None:
    """Built report should expose the most severe evaluation status."""
    builder = WaterQualityReportBuilder()

    report = builder.build(
        measurements=(
            (tan_threshold, 0.2),
            (nitrite_threshold, 0.1),
        ),
    )

    assert report.overall_status is WaterQualityStatus.CRITICAL
    assert report.worst_evaluation.parameter_name == "Nitrite"


def test_build_preserves_measurement_order(
    tan_threshold: WaterQualityThreshold,
    nitrite_threshold: WaterQualityThreshold,
) -> None:
    """Built report should preserve the original measurement order."""
    builder = WaterQualityReportBuilder()

    report = builder.build(
        measurements=(
            (nitrite_threshold, 0.02),
            (tan_threshold, 0.2),
        ),
    )

    assert report.evaluations[0].parameter_name == "Nitrite"
    assert report.evaluations[1].parameter_name == "TAN"


def test_build_rejects_empty_measurements() -> None:
    """Builder should reject an empty measurement collection."""
    builder = WaterQualityReportBuilder()

    with pytest.raises(
        ValueError,
        match="At least one measurement is required",
    ):
        builder.build(
            measurements=(),
        )


def test_build_propagates_evaluation_errors(
    tan_threshold: WaterQualityThreshold,
) -> None:
    """Builder should not hide invalid measurement errors."""
    builder = WaterQualityReportBuilder()

    with pytest.raises(
        ValueError,
        match="No threshold matched",
    ):
        builder.build(
            measurements=(
                (tan_threshold, 5.0),
            ),
        )