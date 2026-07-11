"""Base class for rule-based advisors."""

from abc import abstractmethod
from collections.abc import Mapping

from aquatwin.domain.advisor_result import AdvisorResult
from aquatwin.domain.base_advisor import BaseAdvisor
from aquatwin.domain.water_quality_report import WaterQualityReport
from aquatwin.domain.water_quality_status import WaterQualityStatus


class RuleBasedAdvisor(BaseAdvisor):
    """Create advisor results from water-quality status rules."""

    @property
    @abstractmethod
    def rules(
        self,
    ) -> Mapping[WaterQualityStatus, AdvisorResult]:
        """Return advisor rules by water-quality status."""

    def advise(
        self,
        report: WaterQualityReport,
    ) -> tuple[AdvisorResult, ...]:
        """Return the recommendation matching the report status."""
        return (self.rules[report.overall_status],)