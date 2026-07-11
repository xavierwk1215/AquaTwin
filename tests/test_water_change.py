import pytest

from aquatwin.domain.chemical_state import ChemicalState
from aquatwin.domain.tank_state import TankState
from aquatwin.engine.water_change import apply_water_change


def test_apply_water_change_reduces_all_nitrogen_masses():
    state = TankState(
        chemical_state=ChemicalState(
            organic_n_mass_mg=100.0,
            tan_n_mass_mg=20.0,
            nitrite_n_mass_mg=10.0,
            nitrate_n_mass_mg=50.0,
        ),
        effective_water_volume_l=100.0,
        temperature_c=26.0,
        ph=7.2,
    )

    result = apply_water_change(
        state,
        water_change_fraction=0.25,
    )

    assert result.chemical_state.organic_n_mass_mg == pytest.approx(75.0)
    assert result.chemical_state.tan_n_mass_mg == pytest.approx(15.0)
    assert result.chemical_state.nitrite_n_mass_mg == pytest.approx(7.5)
    assert result.chemical_state.nitrate_n_mass_mg == pytest.approx(37.5)


def test_apply_water_change_preserves_tank_properties():
    state = TankState(
        chemical_state=ChemicalState(
            organic_n_mass_mg=100.0,
            tan_n_mass_mg=20.0,
            nitrite_n_mass_mg=10.0,
            nitrate_n_mass_mg=50.0,
        ),
        effective_water_volume_l=100.0,
        temperature_c=26.0,
        ph=7.2,
    )

    result = apply_water_change(
        state,
        water_change_fraction=0.25,
    )

    assert result.effective_water_volume_l == 100.0
    assert result.temperature_c == 26.0
    assert result.ph == 7.2


def test_apply_water_change_rejects_negative_fraction():
    state = TankState(
        chemical_state=ChemicalState(
            organic_n_mass_mg=100.0,
            tan_n_mass_mg=20.0,
            nitrite_n_mass_mg=10.0,
            nitrate_n_mass_mg=50.0,
        ),
        effective_water_volume_l=100.0,
        temperature_c=26.0,
        ph=7.2,
    )

    with pytest.raises(ValueError):
        apply_water_change(
            state,
            water_change_fraction=-0.10,
        )


def test_apply_water_change_rejects_fraction_above_one():
    state = TankState(
        chemical_state=ChemicalState(
            organic_n_mass_mg=100.0,
            tan_n_mass_mg=20.0,
            nitrite_n_mass_mg=10.0,
            nitrate_n_mass_mg=50.0,
        ),
        effective_water_volume_l=100.0,
        temperature_c=26.0,
        ph=7.2,
    )

    with pytest.raises(ValueError):
        apply_water_change(
            state,
            water_change_fraction=1.10,
        )