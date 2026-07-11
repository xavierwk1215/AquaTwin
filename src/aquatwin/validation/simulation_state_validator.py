"""Validation for immutable simulation states."""

from math import isfinite

from aquatwin.domain.state import SimulationState
from aquatwin.validation.validation_error import (
    ValidationError,
    ValidationSeverity,
)
from aquatwin.validation.validation_result import ValidationResult


class SimulationStateValidator:
    """Validate all tracked nitrogen masses in a SimulationState."""

    def validate(
        self,
        state: SimulationState,
    ) -> ValidationResult:
        """Return validation findings for the supplied simulation state."""
        findings: list[ValidationError] = []

        nitrogen_fields = (
            ("organic_n_mass_mg", state.organic_n_mass_mg),
            ("tan_mass_mg", state.tan_mass_mg),
            ("nitrite_mass_mg", state.nitrite_mass_mg),
            ("nitrate_mass_mg", state.nitrate_mass_mg),
        )

        for field_name, value in nitrogen_fields:
            if not isfinite(value):
                findings.append(
                    ValidationError(
                        code="NON_FINITE_NITROGEN_MASS",
                        field=field_name,
                        severity=ValidationSeverity.ERROR,
                        message=f"{field_name} must be a finite number.",
                    )
                )
            elif value < 0.0:
                findings.append(
                    ValidationError(
                        code="NEGATIVE_NITROGEN_MASS",
                        field=field_name,
                        severity=ValidationSeverity.ERROR,
                        message=(
                            f"{field_name} must be greater than or equal to zero."
                        ),
                    )
                )

        return ValidationResult(findings=tuple(findings))