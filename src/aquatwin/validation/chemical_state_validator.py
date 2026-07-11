from aquatwin.domain.chemical_state import ChemicalState
from aquatwin.validation.validation_error import (
    ValidationError,
    ValidationSeverity,
)
from aquatwin.validation.validation_result import ValidationResult


class ChemicalStateValidator:
    """Validates ChemicalState objects."""

    def validate(
        self,
        state: ChemicalState,
    ) -> ValidationResult:

        findings: list[ValidationError] = []

        nitrogen_fields = [
            ("organic_n_mass_mg", state.organic_n_mass_mg),
            ("tan_n_mass_mg", state.tan_n_mass_mg),
            ("nitrite_n_mass_mg", state.nitrite_n_mass_mg),
            ("nitrate_n_mass_mg", state.nitrate_n_mass_mg),
        ]

        for field_name, value in nitrogen_fields:
            if value < 0:
                findings.append(
                    ValidationError(
                        code="NEGATIVE_NITROGEN_MASS",
                        field=field_name,
                        severity=ValidationSeverity.ERROR,
                        message=f"{field_name} must be greater than or equal to zero.",
                    )
                )

        return ValidationResult(findings=tuple(findings))