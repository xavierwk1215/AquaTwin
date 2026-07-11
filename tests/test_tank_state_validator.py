from aquatwin.domain.chemical_state import ChemicalState
from aquatwin.domain.tank_state import TankState
from aquatwin.validation.tank_state_validator import TankStateValidator
from aquatwin.validation.validation_error import ValidationSeverity


def create_valid_chemical_state() -> ChemicalState:
    return ChemicalState(
        organic_n_mass_mg=100.0,
        tan_n_mass_mg=10.0,
        nitrite_n_mass_mg=5.0,
        nitrate_n_mass_mg=20.0,
    )


def test_valid_tank_state_returns_valid_result():
    state = TankState(
        chemical_state=create_valid_chemical_state(),
        effective_water_volume_l=100.0,
        temperature_c=26.0,
        ph=7.2,
    )

    result = TankStateValidator().validate(state)

    assert result.is_valid
    assert result.findings == ()


def test_invalid_effective_water_volume_returns_error():
    state = TankState(
        chemical_state=create_valid_chemical_state(),
        effective_water_volume_l=0.0,
        temperature_c=26.0,
        ph=7.2,
    )

    result = TankStateValidator().validate(state)

    assert not result.is_valid
    assert len(result.findings) == 1

    finding = result.findings[0]

    assert finding.code == "INVALID_EFFECTIVE_WATER_VOLUME"
    assert finding.field == "effective_water_volume_l"
    assert finding.severity is ValidationSeverity.ERROR


def test_temperature_outside_limits_returns_error():
    state = TankState(
        chemical_state=create_valid_chemical_state(),
        effective_water_volume_l=100.0,
        temperature_c=45.0,
        ph=7.2,
    )

    result = TankStateValidator().validate(state)

    assert not result.is_valid
    assert len(result.findings) == 1

    finding = result.findings[0]

    assert finding.code == "TEMPERATURE_OUT_OF_RANGE"
    assert finding.field == "temperature_c"
    assert finding.severity is ValidationSeverity.ERROR


def test_ph_outside_limits_returns_error():
    state = TankState(
        chemical_state=create_valid_chemical_state(),
        effective_water_volume_l=100.0,
        temperature_c=26.0,
        ph=15.0,
    )

    result = TankStateValidator().validate(state)

    assert not result.is_valid
    assert len(result.findings) == 1

    finding = result.findings[0]

    assert finding.code == "PH_OUT_OF_RANGE"
    assert finding.field == "ph"
    assert finding.severity is ValidationSeverity.ERROR


def test_invalid_chemical_state_findings_are_included():
    chemical_state = ChemicalState(
        organic_n_mass_mg=100.0,
        tan_n_mass_mg=-1.0,
        nitrite_n_mass_mg=5.0,
        nitrate_n_mass_mg=20.0,
    )
    state = TankState(
        chemical_state=chemical_state,
        effective_water_volume_l=100.0,
        temperature_c=26.0,
        ph=7.2,
    )

    result = TankStateValidator().validate(state)

    assert not result.is_valid
    assert len(result.findings) == 1

    finding = result.findings[0]

    assert finding.code == "NEGATIVE_NITROGEN_MASS"
    assert finding.field == "tan_n_mass_mg"
    assert finding.severity is ValidationSeverity.ERROR