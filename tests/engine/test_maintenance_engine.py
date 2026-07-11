"""Tests for the StepContext-based maintenance engine."""

import pytest

from aquatwin.domain.daily_event_plan import DailyEventPlan
from aquatwin.domain.daily_inputs import DailyInputs
from aquatwin.domain.frozen_parameter_set import FrozenParameterSet
from aquatwin.domain.state import SimulationState
from aquatwin.engine.maintenance_engine import MaintenanceEngine
from aquatwin.engine.step_context import StepContext


def make_context(
    *,
    maintenance: bool,
    maintenance_fraction: float = 0.0,
) -> StepContext:
    """Create a StepContext for maintenance engine tests."""
    return StepContext(
        previous_state=SimulationState(
            organic_n_mass_mg=100.0,
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
            maintenance=maintenance,
            maintenance_fraction=maintenance_fraction,
        ),
        frozen_parameter_set=FrozenParameterSet(
            model_version="test-model",
            parameter_set_version="test-parameters",
        ),
    )


def test_no_maintenance_event_does_not_change_state_or_metrics() -> None:
    """Do nothing when maintenance is not scheduled."""
    context = make_context(
        maintenance=False,
        maintenance_fraction=0.5,
    )

    MaintenanceEngine.apply(context)

    assert context.working_state.to_simulation_state() == (
        context.previous_state
    )
    assert context.metrics == []


def test_zero_maintenance_fraction_removes_nothing() -> None:
    """Allow an explicit maintenance event with a zero fraction."""
    context = make_context(
        maintenance=True,
        maintenance_fraction=0.0,
    )

    MaintenanceEngine.apply(context)

    assert context.working_state.organic_n_mass_mg == pytest.approx(
        100.0
    )
    assert context.metrics[0].name == "maintenance_n_removal_mg"
    assert context.metrics[0].value == pytest.approx(0.0)
    assert context.metrics[0].unit == "mg-N"


def test_partial_maintenance_removes_organic_n_proportionally() -> None:
    """Remove the requested fraction of modelled Organic-N."""
    context = make_context(
        maintenance=True,
        maintenance_fraction=0.25,
    )

    MaintenanceEngine.apply(context)

    assert context.working_state.organic_n_mass_mg == pytest.approx(
        75.0
    )
    assert context.metrics[0].name == "maintenance_n_removal_mg"
    assert context.metrics[0].value == pytest.approx(25.0)
    assert context.metrics[0].unit == "mg-N"


def test_full_maintenance_can_remove_all_organic_n() -> None:
    """Allow complete removal when the fraction is one."""
    context = make_context(
        maintenance=True,
        maintenance_fraction=1.0,
    )

    MaintenanceEngine.apply(context)

    assert context.working_state.organic_n_mass_mg == pytest.approx(
        0.0
    )
    assert context.metrics[0].value == pytest.approx(100.0)


def test_maintenance_does_not_change_dissolved_nitrogen() -> None:
    """Leave TAN-N, nitrite-N, and nitrate-N unchanged."""
    context = make_context(
        maintenance=True,
        maintenance_fraction=0.5,
    )

    MaintenanceEngine.apply(context)

    assert context.working_state.tan_mass_mg == pytest.approx(20.0)
    assert context.working_state.nitrite_mass_mg == pytest.approx(10.0)
    assert context.working_state.nitrate_mass_mg == pytest.approx(50.0)


@pytest.mark.parametrize(
    "maintenance_fraction",
    [-0.01, 1.01],
)
def test_invalid_maintenance_fraction_raises_value_error(
    maintenance_fraction: float,
) -> None:
    """Reject maintenance fractions outside the inclusive range."""
    context = make_context(
        maintenance=True,
        maintenance_fraction=maintenance_fraction,
    )

    with pytest.raises(
        ValueError,
        match=(
            "maintenance_fraction must be between "
            "0.0 and 1.0."
        ),
    ):
        MaintenanceEngine.apply(context)