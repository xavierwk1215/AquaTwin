"""Tests for MineralizationEngine."""

import pytest

from aquatwin.domain.daily_event_plan import DailyEventPlan
from aquatwin.domain.daily_inputs import DailyInputs
from aquatwin.domain.frozen_parameter_set import FrozenParameterSet
from aquatwin.domain.state import SimulationState
from aquatwin.engine.mineralization_engine import MineralizationEngine
from aquatwin.engine.step_context import StepContext


def make_context(
    *,
    opening_organic_n: float = 100.0,
    fraction: float = 0.1,
) -> StepContext:
    return StepContext(
        previous_state=SimulationState(
            organic_n_mass_mg=opening_organic_n,
            tan_mass_mg=20.0,
            nitrite_mass_mg=10.0,
            nitrate_mass_mg=50.0,
        ),
        daily_inputs=DailyInputs(
            day=1,
            water_temperature_c=25.0,
            tank_volume_l=100.0,
        ),
        daily_event_plan=DailyEventPlan(
            feeding=False,
            water_change=False,
            maintenance=False,
        ),
        frozen_parameter_set=FrozenParameterSet(
            model_version="test-model",
            parameter_set_version="test-parameters",
            organic_n_mineralization_fraction_per_day=fraction,
        ),
    )


def test_partial_mineralization() -> None:
    context = make_context(
        opening_organic_n=100.0,
        fraction=0.1,
    )

    MineralizationEngine.apply(context)

    assert context.working_state.organic_n_mass_mg == pytest.approx(
        90.0
    )
    assert context.working_state.tan_mass_mg == pytest.approx(
        30.0
    )
    assert context.metrics[-1].name == "organic_n_mineralized_mg"
    assert context.metrics[-1].value == pytest.approx(10.0)


def test_zero_fraction_changes_nothing() -> None:
    context = make_context(
        fraction=0.0,
    )

    MineralizationEngine.apply(context)

    assert context.working_state.organic_n_mass_mg == pytest.approx(
        100.0
    )
    assert context.working_state.tan_mass_mg == pytest.approx(
        20.0
    )
    assert context.metrics[-1].value == pytest.approx(0.0)


def test_full_fraction_mineralizes_all_opening_organic_n() -> None:
    context = make_context(
        fraction=1.0,
    )

    MineralizationEngine.apply(context)

    assert context.working_state.organic_n_mass_mg == pytest.approx(
        0.0
    )
    assert context.working_state.tan_mass_mg == pytest.approx(
        120.0
    )


def test_today_feed_is_not_mineralized() -> None:
    context = make_context(
        opening_organic_n=100.0,
        fraction=0.1,
    )

    context.working_state.organic_n_mass_mg += 80.0

    MineralizationEngine.apply(context)

    assert context.working_state.organic_n_mass_mg == pytest.approx(
        170.0
    )


@pytest.mark.parametrize(
    "fraction",
    [-0.1, 1.1],
)
def test_invalid_fraction_raises(
    fraction: float,
) -> None:
    context = make_context(
        fraction=fraction,
    )

    with pytest.raises(
        ValueError,
        match=(
            "organic_n_mineralization_fraction_per_day "
            "must be between 0.0 and 1.0."
        ),
    ):
        MineralizationEngine.apply(context)