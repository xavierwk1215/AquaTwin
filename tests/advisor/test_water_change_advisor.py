"""Tests for WaterChangeAdvisor."""

from aquatwin.domain.advice_priority import AdvicePriority
from aquatwin.domain.water_change_advisor import WaterChangeAdvisor
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
    """Create a simple water-quality report for testing."""

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
    """Return low priority when water quality is excellent."""
    advisor = WaterChangeAdvisor()

    results = advisor.advise(
        report=_create_report(
            WaterQualityStatus.EXCELLENT,
        ),
    )

    assert len(results) == 1
    assert results[0].priority is AdvicePriority.LOW


def test_returns_medium_priority_for_acceptable() -> None:
    """Return medium priority when water quality is acceptable."""
    advisor = WaterChangeAdvisor()

    results = advisor.advise(
        report=_create_report(
            WaterQualityStatus.ACCEPTABLE,
        ),
    )

    assert len(results) == 1
    assert results[0].priority is AdvicePriority.MEDIUM


def test_returns_high_priority_for_warning() -> None:
    """Return high priority when water quality is warning."""
    advisor = WaterChangeAdvisor()

    results = advisor.advise(
        report=_create_report(
            WaterQualityStatus.WARNING,
        ),
    )

    assert len(results) == 1
    assert results[0].priority is AdvicePriority.HIGH


def test_returns_critical_priority_for_critical() -> None:
    """Return critical priority when water quality is critical."""
    advisor = WaterChangeAdvisor()

    results = advisor.advise(
        report=_create_report(
            WaterQualityStatus.CRITICAL,
        ),
    )

    assert len(results) == 1
    assert results[0].priority is AdvicePriority.CRITICAL