"""Tests for SimulationStateValidator."""

from math import inf, nan

import pytest

from aquatwin.domain.state import SimulationState
from aquatwin.validation.simulation_state_validator import (
    SimulationStateValidator,
)
from aquatwin.validation.validation_error import ValidationSeverity


def test_valid_simulation_state_returns_valid_result() -> None:
    """Accept finite, non-negative nitrogen masses."""
    state = SimulationState(
        organic_n_mass_mg=100.0,
        tan_mass_mg=10.0,
        nitrite_mass_mg=5.0,
        nitrate_mass_mg=20.0,
    )

    result = SimulationStateValidator().validate(state)

    assert result.is_valid
    assert result.findings == ()


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("organic_n_mass_mg", -1.0),
        ("tan_mass_mg", -1.0),
        ("nitrite_mass_mg", -1.0),
        ("nitrate_mass_mg", -1.0),
    ],
)
def test_negative_nitrogen_mass_returns_error(
    field_name: str,
    field_value: float,
) -> None:
    """Reject every tracked negative nitrogen mass."""
    values = {
        "organic_n_mass_mg": 100.0,
        "tan_mass_mg": 10.0,
        "nitrite_mass_mg": 5.0,
        "nitrate_mass_mg": 20.0,
    }
    values[field_name] = field_value

    state = SimulationState(**values)

    result = SimulationStateValidator().validate(state)

    assert not result.is_valid
    assert len(result.findings) == 1

    finding = result.findings[0]

    assert finding.code == "NEGATIVE_NITROGEN_MASS"
    assert finding.field == field_name
    assert finding.severity is ValidationSeverity.ERROR


@pytest.mark.parametrize(
    "invalid_value",
    [nan, inf, -inf],
)
@pytest.mark.parametrize(
    "field_name",
    [
        "organic_n_mass_mg",
        "tan_mass_mg",
        "nitrite_mass_mg",
        "nitrate_mass_mg",
    ],
)
def test_non_finite_nitrogen_mass_returns_error(
    field_name: str,
    invalid_value: float,
) -> None:
    """Reject NaN and positive or negative infinity."""
    values = {
        "organic_n_mass_mg": 100.0,
        "tan_mass_mg": 10.0,
        "nitrite_mass_mg": 5.0,
        "nitrate_mass_mg": 20.0,
    }
    values[field_name] = invalid_value

    state = SimulationState(**values)

    result = SimulationStateValidator().validate(state)

    assert not result.is_valid
    assert len(result.findings) == 1

    finding = result.findings[0]

    assert finding.code == "NON_FINITE_NITROGEN_MASS"
    assert finding.field == field_name
    assert finding.severity is ValidationSeverity.ERROR


def test_multiple_invalid_masses_return_multiple_errors() -> None:
    """Return one structured finding for every invalid mass."""
    state = SimulationState(
        organic_n_mass_mg=-10.0,
        tan_mass_mg=nan,
        nitrite_mass_mg=2.0,
        nitrate_mass_mg=inf,
    )

    result = SimulationStateValidator().validate(state)

    assert not result.is_valid
    assert len(result.findings) == 3

    assert {finding.field for finding in result.findings} == {
        "organic_n_mass_mg",
        "tan_mass_mg",
        "nitrate_mass_mg",
    }