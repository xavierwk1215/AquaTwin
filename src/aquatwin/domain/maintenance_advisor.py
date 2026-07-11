"""Advisor for aquarium maintenance recommendations."""

from collections.abc import Mapping

from aquatwin.domain.advice_priority import AdvicePriority
from aquatwin.domain.advisor_result import AdvisorResult
from aquatwin.domain.rule_based_advisor import RuleBasedAdvisor
from aquatwin.domain.water_quality_status import WaterQualityStatus


class MaintenanceAdvisor(RuleBasedAdvisor):
    """Recommend aquarium maintenance actions from water-quality status."""

    ADVISOR_NAME = "Maintenance Advisor"

    @property
    def rules(
        self,
    ) -> Mapping[WaterQualityStatus, AdvisorResult]:
        """Return aquarium maintenance rules."""
        return {
            WaterQualityStatus.EXCELLENT: AdvisorResult(
                advisor_name=self.ADVISOR_NAME,
                priority=AdvicePriority.LOW,
                title="Continue routine aquarium maintenance",
                message=(
                    "Continue the normal aquarium cleaning and "
                    "equipment inspection schedule."
                ),
            ),
            WaterQualityStatus.ACCEPTABLE: AdvisorResult(
                advisor_name=self.ADVISOR_NAME,
                priority=AdvicePriority.MEDIUM,
                title="Review routine maintenance",
                message=(
                    "Check the aquarium glass, substrate, filter flow, "
                    "and equipment condition during the next maintenance."
                ),
            ),
            WaterQualityStatus.WARNING: AdvisorResult(
                advisor_name=self.ADVISOR_NAME,
                priority=AdvicePriority.HIGH,
                title="Inspect aquarium maintenance conditions",
                message=(
                    "Inspect the filter flow, accumulated waste, substrate, "
                    "and equipment condition. Perform necessary maintenance "
                    "without replacing all biological filter media."
                ),
            ),
            WaterQualityStatus.CRITICAL: AdvisorResult(
                advisor_name=self.ADVISOR_NAME,
                priority=AdvicePriority.CRITICAL,
                title="Inspect aquarium equipment immediately",
                message=(
                    "Immediately inspect the filter, heater, aeration, "
                    "water circulation, and visible waste accumulation. "
                    "Preserve biological filter media while correcting "
                    "equipment or maintenance problems."
                ),
            ),
        }