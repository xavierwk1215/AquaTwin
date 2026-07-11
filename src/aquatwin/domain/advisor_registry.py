"""Registry for advisor instances."""

from collections.abc import Iterable

from aquatwin.domain.base_advisor import BaseAdvisor


class AdvisorRegistry:
    """Store and provide advisor instances."""

    def __init__(
        self,
        advisors: Iterable[BaseAdvisor] = (),
    ) -> None:
        """Initialize the registry."""
        self._advisors = tuple(advisors)

    @property
    def advisors(self) -> tuple[BaseAdvisor, ...]:
        """Return registered advisors."""
        return self._advisors