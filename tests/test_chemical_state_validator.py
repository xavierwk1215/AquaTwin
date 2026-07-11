from aquatwin.domain.chemical_state import ChemicalState
from aquatwin.validation.chemical_state_validator import (
    ChemicalStateValidator,
)
from aquatwin.validation.validation_error import ValidationSeverity


def test_valid_chemical_state_returns_valid_result():
    state = ChemicalState(
        organic_n_mass_mg=100.0,
        tan_n_mass_mg=10.0,
        nitrite_n_mass_mg=5.0,
        nitrate_n_mass_mg=20.0,
    )

    result = ChemicalStateValidator().validate(state)

    assert result.is_valid
    assert result.findings == ()


def test_negative_nitrogen_mass_returns_error():
    state = ChemicalState(
        organic_n_mass_mg=100.0,
        tan_n_mass_mg=-1.0,
        nitrite_n_mass_mg=5.0,
        nitrate_n_mass_mg=20.0,
    )

    result = ChemicalStateValidator().validate(state)

    assert not result.is_valid
    assert len(result.findings) == 1

    finding = result.findings[0]

    assert finding.code == "NEGATIVE_NITROGEN_MASS"
    assert finding.field == "tan_n_mass_mg"
    assert finding.severity is ValidationSeverity.ERROR


def test_multiple_negative_nitrogen_masses_return_multiple_errors():
    state = ChemicalState(
        organic_n_mass_mg=-10.0,
        tan_n_mass_mg=2.0,
        nitrite_n_mass_mg=-3.0,
        nitrate_n_mass_mg=20.0,
    )

    result = ChemicalStateValidator().validate(state)

    assert not result.is_valid
    assert len(result.findings) == 2
    assert {finding.field for finding in result.findings} == {
        "organic_n_mass_mg",
        "nitrite_n_mass_mg",
    }