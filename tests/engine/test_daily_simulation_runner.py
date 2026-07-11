"""Tests for the official multi-day DailySimulationRunner."""

from unittest.mock import MagicMock, call, patch

import pytest

from aquatwin.domain.daily_event_plan import DailyEventPlan
from aquatwin.domain.daily_inputs import DailyInputs
from aquatwin.domain.daily_simulation_result import (
    DailySimulationResult,
)
from aquatwin.domain.state import SimulationState
from aquatwin.engine.daily_simulation_runner import (
    DailySimulationRunner,
)
from aquatwin.validation.validation_result import ValidationResult


def make_result(
    simulation_day: int,
    new_state: SimulationState,
) -> DailySimulationResult:
    """Create one valid daily result for runner tests."""
    return DailySimulationResult(
        simulation_day=simulation_day,
        new_state=new_state,
        metrics=(),
        validation_result=ValidationResult(findings=()),
    )


def make_runner(
    initial_state: SimulationState,
    daily_inputs_factory: MagicMock,
    daily_event_plan_factory: MagicMock,
) -> DailySimulationRunner:
    """Create a runner with isolated dependencies."""
    return DailySimulationRunner(
        initial_state=initial_state,
        frozen_parameter_set=MagicMock(),
        filter_unit=MagicMock(),
        daily_inputs_factory=daily_inputs_factory,
        daily_event_plan_factory=daily_event_plan_factory,
    )


def test_runner_executes_consecutive_days_and_chains_state() -> None:
    """Use each completed state as the following day's opening state."""
    initial_state = SimulationState(
        organic_n_mass_mg=1.0,
        tan_mass_mg=2.0,
        nitrite_mass_mg=3.0,
        nitrate_mass_mg=4.0,
    )
    day_1_state = SimulationState(
        organic_n_mass_mg=2.0,
        tan_mass_mg=3.0,
        nitrite_mass_mg=4.0,
        nitrate_mass_mg=5.0,
    )
    day_2_state = SimulationState(
        organic_n_mass_mg=3.0,
        tan_mass_mg=4.0,
        nitrite_mass_mg=5.0,
        nitrate_mass_mg=6.0,
    )

    daily_inputs_factory = MagicMock(
        side_effect=[
            DailyInputs(
                day=1,
                water_temperature_c=25.0,
            ),
            DailyInputs(
                day=2,
                water_temperature_c=25.0,
            ),
        ]
    )
    daily_event_plan_factory = MagicMock(
        side_effect=[
            DailyEventPlan(
                feeding=True,
                water_change=False,
                maintenance=False,
            ),
            DailyEventPlan(
                feeding=False,
                water_change=False,
                maintenance=False,
            ),
        ]
    )

    day_1_result = make_result(1, day_1_state)
    day_2_result = make_result(2, day_2_state)

    runner = make_runner(
        initial_state=initial_state,
        daily_inputs_factory=daily_inputs_factory,
        daily_event_plan_factory=daily_event_plan_factory,
    )

    with patch(
        "aquatwin.engine.daily_simulation_runner."
        "DailySimulationEngine.run",
        side_effect=[day_1_result, day_2_result],
    ) as engine_run:
        results = runner.run(days=2)

    assert results == [day_1_result, day_2_result]
    assert daily_inputs_factory.call_args_list == [call(1), call(2)]
    assert daily_event_plan_factory.call_args_list == [
        call(1),
        call(2),
    ]

    day_1_context = engine_run.call_args_list[0].kwargs["context"]
    day_2_context = engine_run.call_args_list[1].kwargs["context"]

    assert day_1_context.previous_state is initial_state
    assert day_2_context.previous_state is day_1_state
    assert initial_state == SimulationState(
        organic_n_mass_mg=1.0,
        tan_mass_mg=2.0,
        nitrite_mass_mg=3.0,
        nitrate_mass_mg=4.0,
    )


def test_runner_rejects_daily_inputs_with_wrong_day() -> None:
    """Reject factory output that does not match the requested day."""
    runner = make_runner(
        initial_state=SimulationState(
            organic_n_mass_mg=0.0,
            tan_mass_mg=0.0,
            nitrite_mass_mg=0.0,
            nitrate_mass_mg=0.0,
        ),
        daily_inputs_factory=MagicMock(
            return_value=DailyInputs(
                day=99,
                water_temperature_c=25.0,
            )
        ),
        daily_event_plan_factory=MagicMock(
            return_value=DailyEventPlan(
                feeding=False,
                water_change=False,
                maintenance=False,
            )
        ),
    )

    with pytest.raises(
        ValueError,
        match="day matching the requested simulation day",
    ):
        runner.run(days=1)


@pytest.mark.parametrize("days", [0, -1])
def test_runner_rejects_non_positive_days(days: int) -> None:
    """Require at least one simulation day."""
    runner = make_runner(
        initial_state=SimulationState(
            organic_n_mass_mg=0.0,
            tan_mass_mg=0.0,
            nitrite_mass_mg=0.0,
            nitrate_mass_mg=0.0,
        ),
        daily_inputs_factory=MagicMock(),
        daily_event_plan_factory=MagicMock(),
    )

    with pytest.raises(
        ValueError,
        match="greater than or equal to 1",
    ):
        runner.run(days=days)


@pytest.mark.parametrize("days", [True, 1.5, "2"])
def test_runner_rejects_non_integer_days(days: object) -> None:
    """Reject booleans and non-integer duration values."""
    runner = make_runner(
        initial_state=SimulationState(
            organic_n_mass_mg=0.0,
            tan_mass_mg=0.0,
            nitrite_mass_mg=0.0,
            nitrate_mass_mg=0.0,
        ),
        daily_inputs_factory=MagicMock(),
        daily_event_plan_factory=MagicMock(),
    )

    with pytest.raises(TypeError, match="days must be an integer"):
        runner.run(days=days)  # type: ignore[arg-type]