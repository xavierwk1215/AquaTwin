"""Tests for SimulationState."""

from aquatwin.domain.state import SimulationState


def test_store_nitrogen_masses() -> None:
    """Store the tracked nitrogen masses."""
    state = SimulationState(
        organic_n_mass_mg=120.0,
        tan_mass_mg=8.5,
        nitrite_mass_mg=2.1,
        nitrate_mass_mg=45.3,
    )

    assert state.organic_n_mass_mg == 120.0
    assert state.tan_mass_mg == 8.5
    assert state.nitrite_mass_mg == 2.1
    assert state.nitrate_mass_mg == 45.3


def test_states_with_same_values_are_equal() -> None:
    """Equal values produce equal immutable states."""
    first = SimulationState(
        organic_n_mass_mg=10.0,
        tan_mass_mg=1.0,
        nitrite_mass_mg=2.0,
        nitrate_mass_mg=3.0,
    )

    second = SimulationState(
        organic_n_mass_mg=10.0,
        tan_mass_mg=1.0,
        nitrite_mass_mg=2.0,
        nitrate_mass_mg=3.0,
    )

    assert first == second