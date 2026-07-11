"""Advisor recommendation result."""

from dataclasses import dataclass

from aquatwin.domain.advice_priority import AdvicePriority


@dataclass(frozen=True, slots=True)
class AdvisorResult:
    """Represents one advisor recommendation."""

    advisor_name: str
    priority: AdvicePriority
    title: str
    message: str

    def __post_init__(self) -> None:
        """Validate the recommendation."""
        if not self.advisor_name.strip():
            raise ValueError(
                "advisor_name must not be empty."
            )

        if not self.title.strip():
            raise ValueError(
                "title must not be empty."
            )

        if not self.message.strip():
            raise ValueError(
                "message must not be empty."
            )

    @property
    def requires_immediate_action(self) -> bool:
        """Return whether immediate action is recommended."""
        return self.priority.requires_immediate_action