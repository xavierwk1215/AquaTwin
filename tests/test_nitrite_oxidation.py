import pytest

from aquatwin.domain.chemical_state import ChemicalState
from aquatwin.domain.tank_state import TankState
from aquatwin.engine.nitrite_oxidation import (
    apply_nitrite_oxidation,
)


def test_apply_nitrite_oxidation_moves_mass_to_nitrate():
    state = TankState(
        chemical_state=ChemicalState(
            organic_n_mass_mg=90.0,
            tan_n_mass_mg=15.0,
            nitrite_n_mass_mg=20.0,
            nitrate_n_mass_mg=10.0,
        ),
        effective_water_volume_l=100.0,
        temperature_c=26.0,
        ph=7.2,
    )

    result = apply_nitrite_oxidation(
        state,
        oxidation_fraction_per_day=0.25,
    )

    assert result.chemical_state.organic_n_mass_mg == 90.0
    assert result.chemical_state.tan_n_mass_mg == 15.0
    assert result.chemical_state.nitrite_n_mass_mg == 15.0
    assert result.chemical_state.nitrate_n_mass_mg == 15.0

    assert result.effective_water_volume_l == 100.0
    assert result.temperature_c == 26.0
    assert result.ph == 7.2

def test_apply_nitrite_oxidation_preserves_total_nitrogen_mass():
    state = TankState(
        chemical_state=ChemicalState(
            organic_n_mass_mg=90.0,
            tan_n_mass_mg=15.0,
            nitrite_n_mass_mg=20.0,
            nitrate_n_mass_mg=10.0,
        ),
        effective_water_volume_l=100.0,
        temperature_c=26.0,
        ph=7.2,
    )

    before_total = (
        state.chemical_state.organic_n_mass_mg
        + state.chemical_state.tan_n_mass_mg
        + state.chemical_state.nitrite_n_mass_mg
        + state.chemical_state.nitrate_n_mass_mg
    )

    result = apply_nitrite_oxidation(
        state,
        oxidation_fraction_per_day=0.25,
    )

    after_total = (
        result.chemical_state.organic_n_mass_mg
        + result.chemical_state.tan_n_mass_mg
        + result.chemical_state.nitrite_n_mass_mg
        + result.chemical_state.nitrate_n_mass_mg
    )

    assert before_total == after_total


def test_apply_nitrite_oxidation_rejects_negative_fraction():
    state = TankState(
        chemical_state=ChemicalState(
            organic_n_mass_mg=90.0,
            tan_n_mass_mg=15.0,
            nitrite_n_mass_mg=20.0,
            nitrate_n_mass_mg=10.0,
        ),
        effective_water_volume_l=100.0,
        temperature_c=26.0,
        ph=7.2,
    )

    with pytest.raises(ValueError):
        apply_nitrite_oxidation(
            state,
            oxidation_fraction_per_day=-0.10,
        )


def test_apply_nitrite_oxidation_rejects_fraction_above_one():
    state = TankState(
        chemical_state=ChemicalState(
            organic_n_mass_mg=90.0,
            tan_n_mass_mg=15.0,
            nitrite_n_mass_mg=20.0,
            nitrate_n_mass_mg=10.0,
        ),
        effective_water_volume_l=100.0,
        temperature_c=26.0,
        ph=7.2,
    )

    with pytest.raises(ValueError):
        apply_nitrite_oxidation(
            state,
            oxidation_fraction_per_day=1.10,
        )