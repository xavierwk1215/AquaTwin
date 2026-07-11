from aquatwin.domain.chemical_state import ChemicalState
from aquatwin.domain.tank_state import TankState
from aquatwin.engine.daily_simulator import simulate_day


def test_simulate_day_runs_steps_in_order():
    state = TankState(
        chemical_state=ChemicalState(
            organic_n_mass_mg=100.0,
            tan_n_mass_mg=10.0,
            nitrite_n_mass_mg=5.0,
            nitrate_n_mass_mg=20.0,
        ),
        effective_water_volume_l=100.0,
        temperature_c=26.0,
        ph=7.2,
    )

    result = simulate_day(
        state,
        organic_decay_fraction_per_day=0.10,
        tan_oxidation_fraction_per_day=0.50,
    )

    assert result.chemical_state.organic_n_mass_mg == 90.0
    assert result.chemical_state.tan_n_mass_mg == 10.0
    assert result.chemical_state.nitrite_n_mass_mg == 15.0
    assert result.chemical_state.nitrate_n_mass_mg == 20.0