"""Tests for DailySimulationResult."""

from aquatwin.domain.daily_simulation_result import (
    DailySimulationResult,
)
from aquatwin.domain.metrics import DailyMetric
from aquatwin.domain.state import SimulationState
from aquatwin.validation.validation_error import (
    ValidationError,
    ValidationSeverity,
)
from aquatwin.validation.validation_result import ValidationResult


def test_valid_daily_simulation_result() -> None:
    """Expose a valid completed daily simulation result."""
    result = DailySimulationResult(
        simulation_day=1,
        new_state=SimulationState(
            organic_n_mass_mg=40.0,
            tan_mass_mg=20.0,
            nitrite_mass_mg=10.0,
            nitrate_mass_mg=30.0,
        ),
        metrics=(
            DailyMetric(
                name="tan_n_oxidized_mg",
                value=5.0,
                unit="mg-N",
            ),
        ),
        validation_result=ValidationResult(
            findings=(),
        ),
    )

    assert result.simulation_day == 1
    assert result.is_valid
    assert result.new_state.tan_mass_mg == 20.0
    assert len(result.metrics) == 1


def test_invalid_daily_simulation_result() -> None:
    """Expose validation failure through the result object."""
    finding = ValidationError(
        code="NITROGEN_MASS_BALANCE_VIOLATION",
        field="closing_total_n_mg",
        severity=ValidationSeverity.ERROR,
        message="Daily nitrogen mass balance failed.",
    )

    result = DailySimulationResult(
        simulation_day=2,
        new_state=SimulationState(
            organic_n_mass_mg=40.0,
            tan_mass_mg=20.0,
            nitrite_mass_mg=10.0,
            nitrate_mass_mg=31.0,
        ),
        metrics=(),
        validation_result=ValidationResult(
            findings=(finding,),
        ),
    )

    assert result.simulation_day == 2
    assert not result.is_valid
    assert result.validation_result.errors == (finding,)


def test_daily_simulation_result_is_immutable() -> None:
    """Prevent official daily results from being modified."""
    result = DailySimulationResult(
        simulation_day=1,
        new_state=SimulationState(
            organic_n_mass_mg=40.0,
            tan_mass_mg=20.0,
            nitrite_mass_mg=10.0,
            nitrate_mass_mg=30.0,
        ),
        metrics=(),
        validation_result=ValidationResult(
            findings=(),
        ),
    )

    try:
        result.simulation_day = 2
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "DailySimulationResult must be immutable."
        )