from aquatwin.domain.chemical_state import ChemicalState


def test_create_chemical_state():
    state = ChemicalState(
        organic_n_mass_mg=100.0,
        tan_n_mass_mg=10.0,
        nitrite_n_mass_mg=5.0,
        nitrate_n_mass_mg=20.0,
    )

    assert state.organic_n_mass_mg == 100.0
    assert state.tan_n_mass_mg == 10.0
    assert state.nitrite_n_mass_mg == 5.0
    assert state.nitrate_n_mass_mg == 20.0