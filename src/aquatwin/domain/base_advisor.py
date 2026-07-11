"""Base class for all advisors."""

from abc import ABC, abstractmethod

from aquatwin.domain.advisor_result import AdvisorResult
from aquatwin.domain.water_quality_report import WaterQualityReport


class BaseAdvisor(ABC):
    """Abstract base class for AquaTwin advisors."""

    @abstractmethod
    def advise(
        self,
        *,
        report: WaterQualityReport,
    ) -> tuple[AdvisorResult, ...]:
        """Return advisor recommendations."""
        raise NotImplementedError