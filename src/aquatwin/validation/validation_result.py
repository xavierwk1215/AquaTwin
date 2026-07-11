from dataclasses import dataclass

from aquatwin.validation.validation_error import (
    ValidationError,
    ValidationSeverity,
)


@dataclass(frozen=True)
class ValidationResult:
    """Represents the complete result of one validation operation."""

    findings: tuple[ValidationError, ...]

    @property
    def is_valid(self) -> bool:
        """Return True when no error-level findings exist."""

        return not any(
            finding.severity is ValidationSeverity.ERROR
            for finding in self.findings
        )

    @property
    def errors(self) -> tuple[ValidationError, ...]:
        """Return only error-level findings."""

        return tuple(
            finding
            for finding in self.findings
            if finding.severity is ValidationSeverity.ERROR
        )

    @property
    def warnings(self) -> tuple[ValidationError, ...]:
        """Return only warning-level findings."""

        return tuple(
            finding
            for finding in self.findings
            if finding.severity is ValidationSeverity.WARNING
        )