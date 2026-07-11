"""Advisor for feeding recommendations."""

from collections.abc import Mapping

from aquatwin.domain.advice_priority import AdvicePriority
from aquatwin.domain.advisor_result import AdvisorResult
from aquatwin.domain.rule_based_advisor import RuleBasedAdvisor
from aquatwin.domain.water_quality_status import WaterQualityStatus


class FeedingAdvisor(RuleBasedAdvisor):
    """Recommend feeding actions from water-quality status."""

    ADVISOR_NAME = "Feeding Advisor"

    @property
    def rules(
        self,
    ) -> Mapping[WaterQualityStatus, AdvisorResult]:
        """Return feeding rules."""
        return {
            WaterQualityStatus.EXCELLENT: AdvisorResult(
                advisor_name=self.ADVISOR_NAME,
                priority=AdvicePriority.LOW,
                title="Continue the normal feeding schedule",
                message=(
                    "Water quality is excellent. Continue the normal "
                    "feeding schedule while monitoring for uneaten food."
                ),
            ),
            WaterQualityStatus.ACCEPTABLE: AdvisorResult(
                advisor_name=self.ADVISOR_NAME,
                priority=AdvicePriority.MEDIUM,
                title="Maintain controlled feeding",
                message=(
                    "Water quality is acceptable. Continue controlled "
                    "feeding and avoid excess food."
                ),
            ),
            WaterQualityStatus.WARNING: AdvisorResult(
                advisor_name=self.ADVISOR_NAME,
                priority=AdvicePriority.HIGH,
                title="Reduce feeding temporarily",
                message=(
                    "Water quality requires attention. Reduce feeding "
                    "temporarily and remove any uneaten food."
                ),
            ),
            WaterQualityStatus.CRITICAL: AdvisorResult(
                advisor_name=self.ADVISOR_NAME,
                priority=AdvicePriority.CRITICAL,
                title="Pause feeding temporarily",
                message=(
                    "Critical water-quality conditions were detected. "
                    "Pause feeding temporarily to reduce additional "
                    "organic waste while corrective action is taken."
                ),
            ),
        }