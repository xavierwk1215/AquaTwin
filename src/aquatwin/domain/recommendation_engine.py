"""Recommendation engine for advisor results."""

from aquatwin.domain.advisor_registry import AdvisorRegistry
from aquatwin.domain.advisor_result import AdvisorResult
from aquatwin.domain.recommendation_result import (
    RecommendationResult,
)
from aquatwin.domain.water_quality_report import WaterQualityReport


class RecommendationEngine:
    """Run advisors and aggregate their recommendations."""

    def recommend(
        self,
        recommendations: tuple[AdvisorResult, ...],
    ) -> tuple[AdvisorResult, ...]:
        """Return recommendations sorted by priority."""

        return tuple(
            sorted(
                recommendations,
                key=lambda recommendation: recommendation.priority,
                reverse=True,
            )
        )

    def generate(
        self,
        report: WaterQualityReport,
        registry: AdvisorRegistry,
    ) -> RecommendationResult:
        """Run registered advisors and return aggregated results."""

        recommendations = tuple(
            recommendation
            for advisor in registry.advisors
            for recommendation in advisor.advise(report)
        )

        sorted_recommendations = self.recommend(
            recommendations=recommendations,
        )

        return RecommendationResult(
            recommendations=sorted_recommendations,
        )