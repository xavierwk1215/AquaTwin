"""Tests for AdvisorRegistry."""

from aquatwin.domain.advisor_registry import AdvisorRegistry
from aquatwin.domain.base_advisor import BaseAdvisor
from aquatwin.domain.advisor_result import AdvisorResult
from aquatwin.domain.water_quality_report import WaterQualityReport


class DummyAdvisor(BaseAdvisor):
    """Simple advisor used for testing."""

    def advise(
        self,
        report: WaterQualityReport,
    ) -> tuple[AdvisorResult, ...]:
        return ()


def test_registry_is_empty_by_default() -> None:
    """Registry should be empty when no advisors are provided."""

    registry = AdvisorRegistry()

    assert registry.advisors == ()


def test_registry_returns_registered_advisors() -> None:
    """Registry should return the advisors provided during construction."""

    advisor1 = DummyAdvisor()
    advisor2 = DummyAdvisor()

    registry = AdvisorRegistry(
        advisors=(
            advisor1,
            advisor2,
        ),
    )

    assert registry.advisors == (
        advisor1,
        advisor2,
    )


def test_registry_is_immutable() -> None:
    """Returned advisor collection should be immutable."""

    registry = AdvisorRegistry(
        advisors=(
            DummyAdvisor(),
        ),
    )

    assert isinstance(
        registry.advisors,
        tuple,
    )