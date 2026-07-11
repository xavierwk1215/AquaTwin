"""Tests for the water-quality report domain model."""

import pytest

from aquatwin.domain.water_quality_evaluation import WaterQualityEvaluation
from aquatwin.domain.water_quality_report import WaterQualityReport
from aquatwin.domain.water_quality_status import WaterQualityStatus


def create_evaluation(
    *,
    parameter_name: str,
    status: WaterQualityStatus,
    measured_value: float = 0.0,
) -> WaterQualityEvaluation:
    """Create a water-quality evaluation for report tests."""
    return WaterQualityEvaluation(
        parameter_name=parameter_name,
        measured_value=measured_value,
        unit="mg-N/L",
        status=status,
        reason=f"{parameter_name} evaluation reason.",
    )


def test_report_stores_all_evaluations() -> None:
    """Report should preserve every supplied evaluation."""
    evaluations = (
        create_evaluation(
            parameter_name="TAN",
            status=WaterQualityStatus.WARNING,
            measured_value=0.3,
        ),
        create_evaluation(
            parameter_name="Nitrite",
            status=WaterQualityStatus.EXCELLENT,
            measured_value=0.01,
        ),
    )

    report = WaterQualityReport(
        evaluations=evaluations,
    )

    assert report.evaluations == evaluations


@pytest.mark.parametrize(
    ("statuses", "expected_status"),
    [
        (
            (
                WaterQualityStatus.EXCELLENT,
                WaterQualityStatus.EXCELLENT,
            ),
            WaterQualityStatus.EXCELLENT,
        ),
        (
            (
                WaterQualityStatus.EXCELLENT,
                WaterQualityStatus.ACCEPTABLE,
            ),
            WaterQualityStatus.ACCEPTABLE,
        ),
        (
            (
                WaterQualityStatus.ACCEPTABLE,
                WaterQualityStatus.WARNING,
            ),
            WaterQualityStatus.WARNING,
        ),
        (
            (
                WaterQualityStatus.WARNING,
                WaterQualityStatus.CRITICAL,
            ),
            WaterQualityStatus.CRITICAL,
        ),
    ],
)
def test_overall_status_returns_most_severe_status(
    statuses: tuple[WaterQualityStatus, ...],
    expected_status: WaterQualityStatus,
) -> None:
    """Overall status should equal the most severe evaluation status."""
    evaluations = tuple(
        create_evaluation(
            parameter_name=f"Parameter {index}",
            status=status,
        )
        for index, status in enumerate(statuses)
    )

    report = WaterQualityReport(
        evaluations=evaluations,
    )

    assert report.overall_status is expected_status


def test_worst_evaluation_returns_first_most_severe_result() -> None:
    """Worst evaluation should return the first result at maximum severity."""
    first_warning = create_evaluation(
        parameter_name="TAN",
        status=WaterQualityStatus.WARNING,
        measured_value=0.3,
    )
    second_warning = create_evaluation(
        parameter_name="Nitrate",
        status=WaterQualityStatus.WARNING,
        measured_value=40.0,
    )

    report = WaterQualityReport(
        evaluations=(
            create_evaluation(
                parameter_name="Nitrite",
                status=WaterQualityStatus.EXCELLENT,
            ),
            first_warning,
            second_warning,
        ),
    )

    assert report.worst_evaluation is first_warning


def test_report_rejects_empty_evaluations() -> None:
    """A report should require at least one evaluation."""
    with pytest.raises(
        ValueError,
        match="At least one evaluation is required",
    ):
        WaterQualityReport(
            evaluations=(),
        )


def test_requires_attention_follows_overall_status() -> None:
    """Report should expose whether any result needs attention."""
    safe_report = WaterQualityReport(
        evaluations=(
            create_evaluation(
                parameter_name="TAN",
                status=WaterQualityStatus.EXCELLENT,
            ),
        ),
    )
    warning_report = WaterQualityReport(
        evaluations=(
            create_evaluation(
                parameter_name="Nitrite",
                status=WaterQualityStatus.WARNING,
            ),
        ),
    )

    assert safe_report.requires_attention is False
    assert warning_report.requires_attention is True