"""Tests for the water-change advisor."""

from aquatwin.advisor.water_change_advisor import WaterChangeAdvisor
from aquatwin.domain.advice_priority import AdvicePriority
from aquatwin.domain.water_quality_evaluation import WaterQualityEvaluation
from aquatwin.domain.water_quality_report import WaterQualityReport
from aquatwin.domain.water_quality_status import WaterQualityStatus


def create_report(
    *,
    parameter_name: str,
    status: WaterQualityStatus,
) -> WaterQualityReport:
    """Create a report containing one evaluation."""
    evaluation = WaterQualityEvaluation(
        parameter_name=parameter_name,
        measured_value=0.3,
        unit="mg-N/L",
        status=status,
        reason=f"{parameter_name} evaluation reason.",
    )

    return WaterQualityReport(
        evaluations=(evaluation,),
    )


def test_advisor_returns_no_advice_for_excellent_status() -> None:
    """Excellent water quality should not trigger a water-change action."""
    advisor = WaterChangeAdvisor()
    report = create_report(
        parameter_name="TAN",
        status=WaterQualityStatus.EXCELLENT,
    )

    results = advisor.advise(
        report=report,
    )

    assert results == ()


def test_advisor_returns_no_advice_for_acceptable_status() -> None:
    """Acceptable water quality should not trigger a water-change action."""
    advisor = WaterChangeAdvisor()
    report = create_report(
        parameter_name="Nitrate",
        status=WaterQualityStatus.ACCEPTABLE,
    )

    results = advisor.advise(
        report=report,
    )

    assert results == ()


def test_advisor_returns_high_priority_advice_for_warning() -> None:
    """Warning status should produce a high-priority recommendation."""
    advisor = WaterChangeAdvisor()
    report = create_report(
        parameter_name="TAN",
        status=WaterQualityStatus.WARNING,
    )

    results = advisor.advise(
        report=report,
    )

    assert len(results) == 1

    result = results[0]

    assert result.advisor_name == "Water Change Advisor"
    assert result.priority is AdvicePriority.HIGH
    assert result.title == "Partial water change recommended"
    assert "TAN" in result.message
    assert result.requires_immediate_action is True


def test_advisor_returns_critical_advice_for_critical_status() -> None:
    """Critical status should produce an immediate recommendation."""
    advisor = WaterChangeAdvisor()
    report = create_report(
        parameter_name="Nitrite",
        status=WaterQualityStatus.CRITICAL,
    )

    results = advisor.advise(
        report=report,
    )

    assert len(results) == 1

    result = results[0]

    assert result.advisor_name == "Water Change Advisor"
    assert result.priority is AdvicePriority.CRITICAL
    assert result.title == "Immediate partial water change required"
    assert "Nitrite" in result.message
    assert result.requires_immediate_action is True


def test_advisor_uses_worst_evaluation_parameter() -> None:
    """Recommendation should identify the parameter causing the highest risk."""
    report = WaterQualityReport(
        evaluations=(
            WaterQualityEvaluation(
                parameter_name="TAN",
                measured_value=0.1,
                unit="mg-N/L",
                status=WaterQualityStatus.ACCEPTABLE,
                reason="TAN is acceptable.",
            ),
            WaterQualityEvaluation(
                parameter_name="Nitrite",
                measured_value=0.2,
                unit="mg-N/L",
                status=WaterQualityStatus.CRITICAL,
                reason="Nitrite is critical.",
            ),
        ),
    )

    advisor = WaterChangeAdvisor()

    results = advisor.advise(
        report=report,
    )

    assert len(results) == 1
    assert "Nitrite" in results[0].message