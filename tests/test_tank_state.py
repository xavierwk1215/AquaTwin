from aquatwin.domain.chemical_state import ChemicalState
from aquatwin.domain.tank_state import TankState


def test_create_tank_state():
    chemical_state = ChemicalState(
        organic_n_mass_mg=100.0,
        tan_n_mass_mg=10.0,
        nitrite_n_mass_mg=5.0,
        nitrate_n_mass_mg=20.0,
    )

    tank_state = TankState(
        chemical_state=chemical_state,
        effective_water_volume_l=100.0,
        temperature_c=26.0,
        ph=7.2,
    )

    assert tank_state.chemical_state == chemical_state
    assert tank_state.effective_water_volume_l == 100.0
    assert tank_state.temperature_c == 26.0
    assert tank_state.ph == 7.2