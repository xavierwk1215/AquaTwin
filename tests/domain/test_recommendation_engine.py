"""Tests for RecommendationEngine."""

from aquatwin.domain.advice_priority import AdvicePriority
from aquatwin.domain.advisor_registry import AdvisorRegistry
from aquatwin.domain.advisor_result import AdvisorResult
from aquatwin.domain.base_advisor import BaseAdvisor
from aquatwin.domain.maintenance_advisor import MaintenanceAdvisor
from aquatwin.domain.recommendation_engine import (
    RecommendationEngine,
)
from aquatwin.domain.water_quality_evaluation import (
    WaterQualityEvaluation,
)
from aquatwin.domain.water_quality_report import WaterQualityReport
from aquatwin.domain.water_quality_status import (
    WaterQualityStatus,
)


class DummyAdvisor(BaseAdvisor):
    """Advisor that returns predefined recommendations."""

    def __init__(
        self,
        recommendations: tuple[AdvisorResult, ...],
    ) -> None:
        """Initialize the dummy advisor."""
        self._recommendations = recommendations

    def advise(
        self,
        report: WaterQualityReport,
    ) -> tuple[AdvisorResult, ...]:
        """Return predefined recommendations."""
        return self._recommendations


def _create_recommendation(
    advisor_name: str,
    priority: AdvicePriority,
) -> AdvisorResult:
    """Create an advisor result for testing."""
    return AdvisorResult(
        advisor_name=advisor_name,
        priority=priority,
        title=f"{advisor_name} recommendation",
        message=f"Recommendation from {advisor_name}.",
    )


def _create_report(
    status: WaterQualityStatus = WaterQualityStatus.EXCELLENT,
) -> WaterQualityReport:
    """Create a water-quality report for testing."""
    evaluation = WaterQualityEvaluation(
        parameter_name="Ammonia",
        measured_value=0.0,
        unit="mg/L",
        status=status,
        reason="Water-quality evaluation for testing.",
    )

    return WaterQualityReport(
        evaluations=(evaluation,),
    )


def test_recommendations_are_sorted_by_priority() -> None:
    """Sort recommendations from highest to lowest priority."""
    engine = RecommendationEngine()

    recommendations = (
        _create_recommendation(
            advisor_name="Temperature",
            priority=AdvicePriority.LOW,
        ),
        _create_recommendation(
            advisor_name="Water Change",
            priority=AdvicePriority.CRITICAL,
        ),
        _create_recommendation(
            advisor_name="Feeding",
            priority=AdvicePriority.HIGH,
        ),
        _create_recommendation(
            advisor_name="Maintenance",
            priority=AdvicePriority.MEDIUM,
        ),
    )

    result = engine.recommend(
        recommendations=recommendations,
    )

    assert result[0].priority is AdvicePriority.CRITICAL
    assert result[1].priority is AdvicePriority.HIGH
    assert result[2].priority is AdvicePriority.MEDIUM
    assert result[3].priority is AdvicePriority.LOW


def test_generate_runs_all_registered_advisors() -> None:
    """Run every advisor registered in the registry."""
    engine = RecommendationEngine()

    registry = AdvisorRegistry(
        advisors=(
            DummyAdvisor(
                recommendations=(
                    _create_recommendation(
                        advisor_name="Water Change",
                        priority=AdvicePriority.HIGH,
                    ),
                ),
            ),
            DummyAdvisor(
                recommendations=(
                    _create_recommendation(
                        advisor_name="Feeding",
                        priority=AdvicePriority.MEDIUM,
                    ),
                ),
            ),
        ),
    )

    result = engine.generate(
        report=_create_report(),
        registry=registry,
    )

    assert result.recommendation_count == 2


def test_generate_combines_multiple_results_from_one_advisor() -> None:
    """Collect every result returned by an advisor."""
    engine = RecommendationEngine()

    registry = AdvisorRegistry(
        advisors=(
            DummyAdvisor(
                recommendations=(
                    _create_recommendation(
                        advisor_name="Water Change",
                        priority=AdvicePriority.CRITICAL,
                    ),
                    _create_recommendation(
                        advisor_name="Water Change",
                        priority=AdvicePriority.HIGH,
                    ),
                ),
            ),
        ),
    )

    result = engine.generate(
        report=_create_report(),
        registry=registry,
    )

    assert result.recommendation_count == 2


def test_generate_sorts_results_from_multiple_advisors() -> None:
    """Sort combined advisor results by priority."""
    engine = RecommendationEngine()

    registry = AdvisorRegistry(
        advisors=(
            DummyAdvisor(
                recommendations=(
                    _create_recommendation(
                        advisor_name="Temperature",
                        priority=AdvicePriority.LOW,
                    ),
                ),
            ),
            DummyAdvisor(
                recommendations=(
                    _create_recommendation(
                        advisor_name="Water Change",
                        priority=AdvicePriority.CRITICAL,
                    ),
                ),
            ),
            DummyAdvisor(
                recommendations=(
                    _create_recommendation(
                        advisor_name="Feeding",
                        priority=AdvicePriority.HIGH,
                    ),
                ),
            ),
        ),
    )

    result = engine.generate(
        report=_create_report(),
        registry=registry,
    )

    assert result.recommendations[0].priority is AdvicePriority.CRITICAL
    assert result.recommendations[1].priority is AdvicePriority.HIGH
    assert result.recommendations[2].priority is AdvicePriority.LOW
    assert result.highest_priority is AdvicePriority.CRITICAL
    assert result.requires_immediate_action is True


def test_generate_runs_maintenance_advisor() -> None:
    """Include maintenance advice from a registered advisor."""
    engine = RecommendationEngine()

    registry = AdvisorRegistry(
        advisors=(
            MaintenanceAdvisor(),
        ),
    )

    result = engine.generate(
        report=_create_report(
            status=WaterQualityStatus.WARNING,
        ),
        registry=registry,
    )

    assert result.recommendation_count == 1
    assert result.recommendations[0].advisor_name == "Maintenance Advisor"
    assert result.recommendations[0].priority is AdvicePriority.HIGH
    assert result.highest_priority is AdvicePriority.HIGH
    assert result.requires_immediate_action is True


def test_generate_returns_empty_result_for_empty_registry() -> None:
    """Return an empty result when no advisors are registered."""
    engine = RecommendationEngine()

    result = engine.generate(
        report=_create_report(),
        registry=AdvisorRegistry(),
    )

    assert result.recommendations == ()
    assert result.recommendation_count == 0
    assert result.highest_priority is None
    assert result.requires_immediate_action is False