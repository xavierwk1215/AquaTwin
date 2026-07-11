"""Tests for FeedingAdvisor."""

from aquatwin.domain.advice_priority import AdvicePriority
from aquatwin.domain.feeding_advisor import FeedingAdvisor
from aquatwin.domain.water_quality_evaluation import (
    WaterQualityEvaluation,
)
from aquatwin.domain.water_quality_report import WaterQualityReport
from aquatwin.domain.water_quality_status import (
    WaterQualityStatus,
)


def _create_report(
    status: WaterQualityStatus,
) -> WaterQualityReport:
    """Create a report for testing."""

    evaluation = WaterQualityEvaluation(
        parameter_name="Ammonia",
        measured_value=0.0,
        unit="mg/L",
        status=status,
        reason="Test evaluation.",
    )

    return WaterQualityReport(
        evaluations=(evaluation,),
    )


def test_returns_low_priority_for_excellent() -> None:
    advisor = FeedingAdvisor()

    result = advisor.advise(
        report=_create_report(
            WaterQualityStatus.EXCELLENT,
        ),
    )

    assert len(result) == 1
    assert result[0].priority is AdvicePriority.LOW


def test_returns_medium_priority_for_acceptable() -> None:
    advisor = FeedingAdvisor()

    result = advisor.advise(
        report=_create_report(
            WaterQualityStatus.ACCEPTABLE,
        ),
    )

    assert result[0].priority is AdvicePriority.MEDIUM


def test_returns_high_priority_for_warning() -> None:
    advisor = FeedingAdvisor()

    result = advisor.advise(
        report=_create_report(
            WaterQualityStatus.WARNING,
        ),
    )

    assert result[0].priority is AdvicePriority.HIGH


def test_returns_critical_priority_for_critical() -> None:
    advisor = FeedingAdvisor()

    result = advisor.advise(
        report=_create_report(
            WaterQualityStatus.CRITICAL,
        ),
    )

    assert result[0].priority is AdvicePriority.CRITICAL