from aquatwin.configuration.validation_limits import (
    MAX_PH,
    MAX_TEMPERATURE_C,
    MIN_EFFECTIVE_WATER_VOLUME_L,
    MIN_PH,
    MIN_TEMPERATURE_C,
)
from aquatwin.domain.tank_state import TankState
from aquatwin.validation.chemical_state_validator import ChemicalStateValidator
from aquatwin.validation.validation_error import (
    ValidationError,
    ValidationSeverity,
)
from aquatwin.validation.validation_result import ValidationResult


class TankStateValidator:
    """Validates TankState objects."""

    def validate(
        self,
        state: TankState,
    ) -> ValidationResult:
        findings: list[ValidationError] = []

        if state.effective_water_volume_l < MIN_EFFECTIVE_WATER_VOLUME_L:
            findings.append(
                ValidationError(
                    code="INVALID_EFFECTIVE_WATER_VOLUME",
                    field="effective_water_volume_l",
                    severity=ValidationSeverity.ERROR,
                    message=(
                        "effective_water_volume_l must be greater than or "
                        f"equal to {MIN_EFFECTIVE_WATER_VOLUME_L}."
                    ),
                )
            )

        if not MIN_TEMPERATURE_C <= state.temperature_c <= MAX_TEMPERATURE_C:
            findings.append(
                ValidationError(
                    code="TEMPERATURE_OUT_OF_RANGE",
                    field="temperature_c",
                    severity=ValidationSeverity.ERROR,
                    message=(
                        "temperature_c must be between "
                        f"{MIN_TEMPERATURE_C} and {MAX_TEMPERATURE_C}."
                    ),
                )
            )

        if not MIN_PH <= state.ph <= MAX_PH:
            findings.append(
                ValidationError(
                    code="PH_OUT_OF_RANGE",
                    field="ph",
                    severity=ValidationSeverity.ERROR,
                    message=f"ph must be between {MIN_PH} and {MAX_PH}.",
                )
            )

        chemical_result = ChemicalStateValidator().validate(state.chemical_state)
        findings.extend(chemical_result.findings)

        return ValidationResult(findings=tuple(findings))