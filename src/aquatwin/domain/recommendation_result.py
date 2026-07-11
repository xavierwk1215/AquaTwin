"""Recommendation result domain model."""

from dataclasses import dataclass

from aquatwin.domain.advice_priority import AdvicePriority
from aquatwin.domain.advisor_result import AdvisorResult


@dataclass(frozen=True, slots=True)
class RecommendationResult:
    """Represents an aggregated recommendation result."""

    recommendations: tuple[AdvisorResult, ...]

    @property
    def recommendation_count(self) -> int:
        """Return the number of recommendations."""
        return len(self.recommendations)

    @property
    def highest_priority(self) -> AdvicePriority | None:
        """Return the highest recommendation priority."""
        if not self.recommendations:
            return None

        return max(
            recommendation.priority
            for recommendation in self.recommendations
        )

    @property
    def requires_immediate_action(self) -> bool:
        """Return whether any recommendation needs immediate action."""
        return any(
            recommendation.requires_immediate_action
            for recommendation in self.recommendations
        )