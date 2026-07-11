"""Tests for StepContextNitriteOxidationEngine."""

import pytest

from aquatwin.domain.daily_event_plan import DailyEventPlan
from aquatwin.domain.daily_inputs import DailyInputs
from aquatwin.domain.frozen_parameter_set import FrozenParameterSet
from aquatwin.domain.state import SimulationState
from aquatwin.engine.step_context import StepContext
from aquatwin.engine.step_context_nitrite_oxidation_engine import (
    StepContextNitriteOxidationEngine,
)


def make_context(
    *,
    nitrite_mass_mg: float = 100.0,
    nitrate_mass_mg: float = 20.0,
    fraction: float = 0.5,
) -> StepContext:
    return StepContext(
        previous_state=SimulationState(
            organic_n_mass_mg=50.0,
            tan_mass_mg=30.0,
            nitrite_mass_mg=nitrite_mass_mg,
            nitrate_mass_mg=nitrate_mass_mg,
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
            nitrite_oxidation_fraction_per_day=fraction,
        ),
    )


def test_partial_nitrite_oxidation() -> None:
    context = make_context(
        nitrite_mass_mg=100.0,
        nitrate_mass_mg=20.0,
        fraction=0.5,
    )

    StepContextNitriteOxidationEngine.apply(context)

    assert context.working_state.nitrite_mass_mg == pytest.approx(
        50.0
    )
    assert context.working_state.nitrate_mass_mg == pytest.approx(
        70.0
    )
    assert context.metrics[-1].name == "nitrite_n_oxidized_mg"
    assert context.metrics[-1].value == pytest.approx(50.0)
    assert context.metrics[-1].unit == "mg-N"


def test_zero_fraction_changes_nothing() -> None:
    context = make_context(
        fraction=0.0,
    )

    StepContextNitriteOxidationEngine.apply(context)

    assert context.working_state.nitrite_mass_mg == pytest.approx(
        100.0
    )
    assert context.working_state.nitrate_mass_mg == pytest.approx(
        20.0
    )
    assert context.metrics[-1].value == pytest.approx(0.0)


def test_full_fraction_oxidizes_all_nitrite() -> None:
    context = make_context(
        fraction=1.0,
    )

    StepContextNitriteOxidationEngine.apply(context)

    assert context.working_state.nitrite_mass_mg == pytest.approx(
        0.0
    )
    assert context.working_state.nitrate_mass_mg == pytest.approx(
        120.0
    )


def test_nitrite_oxidation_does_not_change_other_nitrogen_pools() -> None:
    context = make_context(
        fraction=0.5,
    )

    StepContextNitriteOxidationEngine.apply(context)

    assert context.working_state.organic_n_mass_mg == pytest.approx(
        50.0
    )
    assert context.working_state.tan_mass_mg == pytest.approx(
        30.0
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
            "nitrite_oxidation_fraction_per_day must be "
            "between 0.0 and 1.0."
        ),
    ):
        StepContextNitriteOxidationEngine.apply(context)