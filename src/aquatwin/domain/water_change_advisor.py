"""Advisor for water-change recommendations."""

from aquatwin.domain.advice_priority import AdvicePriority
from aquatwin.domain.advisor_result import AdvisorResult
from aquatwin.domain.base_advisor import BaseAdvisor
from aquatwin.domain.water_quality_report import WaterQualityReport
from aquatwin.domain.water_quality_status import WaterQualityStatus


class WaterChangeAdvisor(BaseAdvisor):
    """Recommend water-change actions from a water-quality report."""

    ADVISOR_NAME = "Water Change Advisor"

    def advise(
        self,
        report: WaterQualityReport,
    ) -> tuple[AdvisorResult, ...]:
        """Return a water-change recommendation."""

        if report.overall_status is WaterQualityStatus.CRITICAL:
            return (
                AdvisorResult(
                    advisor_name=self.ADVISOR_NAME,
                    priority=AdvicePriority.CRITICAL,
                    title="Perform an immediate water change",
                    message=(
                        "Critical water-quality conditions were detected. "
                        "Perform a partial water change immediately and "
                        "investigate the underlying cause."
                    ),
                ),
            )

        if report.overall_status is WaterQualityStatus.WARNING:
            return (
                AdvisorResult(
                    advisor_name=self.ADVISOR_NAME,
                    priority=AdvicePriority.HIGH,
                    title="Plan a water change soon",
                    message=(
                        "Water-quality conditions require attention. "
                        "Plan a partial water change soon and continue "
                        "monitoring the aquarium."
                    ),
                ),
            )

        if report.overall_status is WaterQualityStatus.ACCEPTABLE:
            return (
                AdvisorResult(
                    advisor_name=self.ADVISOR_NAME,
                    priority=AdvicePriority.MEDIUM,
                    title="Continue the regular water-change schedule",
                    message=(
                        "Water quality is currently acceptable. "
                        "Continue the regular water-change schedule and "
                        "monitor for any deterioration."
                    ),
                ),
            )

        return (
            AdvisorResult(
                advisor_name=self.ADVISOR_NAME,
                priority=AdvicePriority.LOW,
                title="No additional water change is required",
                message=(
                    "Water quality is currently excellent. "
                    "No additional water change is required beyond the "
                    "normal maintenance schedule."
                ),
            ),
        )