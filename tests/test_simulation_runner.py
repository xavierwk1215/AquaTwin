"""Tests for the multi-day simulation runner."""

import pytest

from aquatwin.configuration.simulation_config import SimulationConfig
from aquatwin.domain.chemical_state import ChemicalState
from aquatwin.domain.daily_snapshot import DailySnapshot
from aquatwin.domain.tank_state import TankState
from aquatwin.engine.simulation_runner import SimulationRunner


@pytest.fixture
def initial_state() -> TankState:
    """Create a valid immutable tank state for runner tests."""
    return TankState(
        chemical_state=ChemicalState(
            organic_n_mass_mg=0.0,
            tan_n_mass_mg=0.0,
            nitrite_n_mass_mg=0.0,
            nitrate_n_mass_mg=0.0,
        ),
        effective_water_volume_l=100.0,
        temperature_c=25.0,
        ph=7.0,
    )


@pytest.fixture
def simulation_config() -> SimulationConfig:
    """Create a valid daily simulation configuration for runner tests."""
    return SimulationConfig(
        food_mass_g=1.0,
        protein_fraction=0.40,
        nitrogen_conversion_factor=0.16,
        organic_decay_fraction_per_day=0.20,
        tan_oxidation_fraction_per_day=0.30,
        nitrite_oxidation_fraction_per_day=0.40,
        water_change_fraction=0.0,
    )


@pytest.fixture
def runner(
    initial_state: TankState,
    simulation_config: SimulationConfig,
) -> SimulationRunner:
    """Create a simulation runner with valid test inputs."""
    return SimulationRunner(
        initial_state=initial_state,
        config=simulation_config,
    )


def test_run_one_day_returns_one_snapshot(
    runner: SimulationRunner,
) -> None:
    """Running one day should return one Day 1 snapshot."""
    snapshots = runner.run(days=1)

    assert len(snapshots) == 1
    assert isinstance(snapshots[0], DailySnapshot)
    assert snapshots[0].simulation_day == 1


def test_run_multiple_days_returns_snapshot_for_each_day(
    runner: SimulationRunner,
) -> None:
    """Running multiple days should return snapshots in day order."""
    snapshots = runner.run(days=5)

    assert len(snapshots) == 5
    assert [snapshot.simulation_day for snapshot in snapshots] == [
        1,
        2,
        3,
        4,
        5,
    ]
    assert all(isinstance(snapshot, DailySnapshot) for snapshot in snapshots)


@pytest.mark.parametrize("days", [0, -1, -30])
def test_run_rejects_days_less_than_one(
    runner: SimulationRunner,
    days: int,
) -> None:
    """Zero and negative simulation durations should be rejected."""
    with pytest.raises(
        ValueError,
        match="days must be greater than or equal to 1",
    ):
        runner.run(days=days)


@pytest.mark.parametrize(
    "days",
    [
        1.5,
        "30",
        None,
        True,
        False,
    ],
)
def test_run_rejects_non_integer_days(
    runner: SimulationRunner,
    days: object,
) -> None:
    """Non-integer simulation durations should be rejected."""
    with pytest.raises(
        TypeError,
        match="days must be an integer",
    ):
        runner.run(days=days)  # type: ignore[arg-type]


def test_run_does_not_modify_initial_state(
    runner: SimulationRunner,
    initial_state: TankState,
) -> None:
    """Running the simulation should preserve the immutable initial state."""
    original_state = initial_state

    runner.run(days=3)

    assert initial_state == original_state


def test_each_day_uses_previous_day_result(
    runner: SimulationRunner,
) -> None:
    """Later snapshots should reflect cumulative multi-day simulation."""
    snapshots = runner.run(days=3)

    day_1_state = snapshots[0].tank_state
    day_2_state = snapshots[1].tank_state
    day_3_state = snapshots[2].tank_state

    assert day_1_state != day_2_state
    assert day_2_state != day_3_state