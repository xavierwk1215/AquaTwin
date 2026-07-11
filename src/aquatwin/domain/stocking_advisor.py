"""Advisor for aquarium stocking recommendations."""

from collections.abc import Mapping

from aquatwin.domain.advice_priority import AdvicePriority
from aquatwin.domain.advisor_result import AdvisorResult
from aquatwin.domain.stocking_evaluation import StockingEvaluation
from aquatwin.domain.stocking_status import StockingStatus


class StockingAdvisor:
    """Recommend stocking actions from a stocking evaluation."""

    ADVISOR_NAME = "Stocking Advisor"

    @property
    def rules(
        self,
    ) -> Mapping[StockingStatus, AdvisorResult]:
        """Return stocking recommendation rules."""
        return {
            StockingStatus.LIGHT: AdvisorResult(
                advisor_name=self.ADVISOR_NAME,
                priority=AdvicePriority.LOW,
                title="Stocking level is light",
                message=(
                    "The estimated bioload is well below the current "
                    "aquarium capacity. Continue normal monitoring."
                ),
            ),
            StockingStatus.BALANCED: AdvisorResult(
                advisor_name=self.ADVISOR_NAME,
                priority=AdvicePriority.LOW,
                title="Stocking level is balanced",
                message=(
                    "The estimated bioload is within the balanced range. "
                    "Maintain the current stocking and care routine."
                ),
            ),
            StockingStatus.HIGH: AdvisorResult(
                advisor_name=self.ADVISOR_NAME,
                priority=AdvicePriority.HIGH,
                title="Stocking level is approaching capacity",
                message=(
                    "The aquarium is operating near its estimated stocking "
                    "capacity. Avoid adding more livestock and monitor water "
                    "quality and filtration performance closely."
                ),
            ),
            StockingStatus.OVERSTOCKED: AdvisorResult(
                advisor_name=self.ADVISOR_NAME,
                priority=AdvicePriority.CRITICAL,
                title="Estimated stocking capacity exceeded",
                message=(
                    "The adjusted bioload exceeds the estimated aquarium "
                    "capacity. Reduce stocking pressure or improve the "
                    "supported aquarium capacity."
                ),
            ),
        }

    def advise(
        self,
        evaluation: StockingEvaluation,
    ) -> tuple[AdvisorResult, ...]:
        """Return advice for the evaluated stocking condition."""
        return (
            self.rules[evaluation.status],
        )