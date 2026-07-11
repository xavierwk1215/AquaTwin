"""Tests for RecommendationResult."""

from aquatwin.domain.advice_priority import AdvicePriority
from aquatwin.domain.advisor_result import AdvisorResult
from aquatwin.domain.recommendation_result import (
    RecommendationResult,
)


def _create_recommendation(
    priority: AdvicePriority,
) -> AdvisorResult:
    """Create a recommendation for testing."""

    return AdvisorResult(
        advisor_name="Test Advisor",
        priority=priority,
        title="Test recommendation",
        message="Test recommendation message.",
    )


def test_empty_result_has_zero_recommendations() -> None:
    """Return zero when no recommendations exist."""

    result = RecommendationResult(
        recommendations=(),
    )

    assert result.recommendation_count == 0


def test_empty_result_has_no_highest_priority() -> None:
    """Return no highest priority when no recommendations exist."""

    result = RecommendationResult(
        recommendations=(),
    )

    assert result.highest_priority is None


def test_empty_result_does_not_require_immediate_action() -> None:
    """Return false when no recommendation needs immediate action."""

    result = RecommendationResult(
        recommendations=(),
    )

    assert result.requires_immediate_action is False


def test_recommendation_count_matches_number_of_items() -> None:
    """Return the number of stored recommendations."""

    result = RecommendationResult(
        recommendations=(
            _create_recommendation(AdvicePriority.LOW),
            _create_recommendation(AdvicePriority.HIGH),
            _create_recommendation(AdvicePriority.CRITICAL),
        ),
    )

    assert result.recommendation_count == 3


def test_highest_priority_returns_most_urgent_priority() -> None:
    """Return the most urgent recommendation priority."""

    result = RecommendationResult(
        recommendations=(
            _create_recommendation(AdvicePriority.LOW),
            _create_recommendation(AdvicePriority.CRITICAL),
            _create_recommendation(AdvicePriority.MEDIUM),
        ),
    )

    assert result.highest_priority is AdvicePriority.CRITICAL


def test_requires_immediate_action_when_high_priority_exists() -> None:
    """Return true when a high-priority recommendation exists."""

    result = RecommendationResult(
        recommendations=(
            _create_recommendation(AdvicePriority.LOW),
            _create_recommendation(AdvicePriority.HIGH),
        ),
    )

    assert result.requires_immediate_action is True


def test_does_not_require_immediate_action_for_medium_or_lower() -> None:
    """Return false when all recommendations are medium or lower."""

    result = RecommendationResult(
        recommendations=(
            _create_recommendation(AdvicePriority.LOW),
            _create_recommendation(AdvicePriority.MEDIUM),
        ),
    )

    assert result.requires_immediate_action is False