from dataclasses import dataclass
from enum import Enum


class ValidationSeverity(Enum):
    """Severity levels for validation findings."""

    ERROR = "ERROR"
    WARNING = "WARNING"


@dataclass(frozen=True)
class ValidationError:
    """Represents one structured validation finding."""

    code: str
    field: str
    severity: ValidationSeverity
    message: str