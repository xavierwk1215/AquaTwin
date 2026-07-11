from aquatwin.validation.validation_error import (
    ValidationError,
    ValidationSeverity,
)
from aquatwin.validation.validation_result import ValidationResult


def test_empty_validation_result_is_valid():
    result = ValidationResult(findings=())

    assert result.is_valid
    assert result.errors == ()
    assert result.warnings == ()


def test_error_finding_makes_result_invalid():
    error = ValidationError(
        code="NEGATIVE_VALUE",
        field="tan_n_mass_mg",
        severity=ValidationSeverity.ERROR,
        message="Negative value.",
    )

    result = ValidationResult(findings=(error,))

    assert not result.is_valid
    assert result.errors == (error,)
    assert result.warnings == ()


def test_warning_does_not_make_result_invalid():
    warning = ValidationError(
        code="HIGH_TEMPERATURE",
        field="temperature_c",
        severity=ValidationSeverity.WARNING,
        message="Temperature is above the recommended range.",
    )

    result = ValidationResult(findings=(warning,))

    assert result.is_valid
    assert result.errors == ()
    assert result.warnings == (warning,)