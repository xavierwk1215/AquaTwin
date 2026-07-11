"""Advisor for temperature recommendations."""

from collections.abc import Mapping

from aquatwin.domain.advice_priority import AdvicePriority
from aquatwin.domain.advisor_result import AdvisorResult
from aquatwin.domain.rule_based_advisor import RuleBasedAdvisor
from aquatwin.domain.water_quality_status import WaterQualityStatus


class TemperatureAdvisor(RuleBasedAdvisor):
    """Recommend temperature actions from water-quality status."""

    ADVISOR_NAME = "Temperature Advisor"

    @property
    def rules(
        self,
    ) -> Mapping[WaterQualityStatus, AdvisorResult]:
        """Return temperature rules."""
        return {
            WaterQualityStatus.EXCELLENT: AdvisorResult(
                advisor_name=self.ADVISOR_NAME,
                priority=AdvicePriority.LOW,
                title="Temperature is under control",
                message="Continue normal temperature monitoring.",
            ),
            WaterQualityStatus.ACCEPTABLE: AdvisorResult(
                advisor_name=self.ADVISOR_NAME,
                priority=AdvicePriority.MEDIUM,
                title="Maintain stable temperature",
                message="Maintain a stable aquarium temperature.",
            ),
            WaterQualityStatus.WARNING: AdvisorResult(
                advisor_name=self.ADVISOR_NAME,
                priority=AdvicePriority.HIGH,
                title="Monitor aquarium temperature",
                message=(
                    "Monitor aquarium temperature closely until water "
                    "quality stabilizes."
                ),
            ),
            WaterQualityStatus.CRITICAL: AdvisorResult(
                advisor_name=self.ADVISOR_NAME,
                priority=AdvicePriority.CRITICAL,
                title="Check aquarium temperature immediately",
                message=(
                    "Verify the heater and thermometer immediately. "
                    "Sudden temperature changes may worsen fish stress."
                ),
            ),
        }