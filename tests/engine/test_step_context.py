"""Tests for StepContext and WorkingState."""

from aquatwin.domain.daily_event_plan import DailyEventPlan
from aquatwin.domain.daily_inputs import DailyInputs
from aquatwin.domain.frozen_parameter_set import FrozenParameterSet
from aquatwin.domain.metrics import DailyMetric
from aquatwin.domain.state import SimulationState
from aquatwin.engine.step_context import StepContext


def _previous_state() -> SimulationState:
    """Create an immutable previous simulation state."""
    return SimulationState(
        organic_n_mass_mg=120.0,
        tan_mass_mg=8.0,
        nitrite_mass_mg=3.0,
        nitrate_mass_mg=45.0,
    )


def _daily_inputs() -> DailyInputs:
    """Create daily external inputs."""
    return DailyInputs(
        day=1,
        water_temperature_c=25.0,
    )


def _daily_event_plan() -> DailyEventPlan:
    """Create a resolved daily event plan."""
    return DailyEventPlan(
        feeding=True,
        water_change=False,
        maintenance=False,
    )


def _frozen_parameter_set() -> FrozenParameterSet:
    """Create a frozen parameter set."""
    return FrozenParameterSet(
        model_version="0.1.0",
        parameter_set_version="test-v1",
    )


def _context() -> StepContext:
    """Create a step context for testing."""
    return StepContext(
        previous_state=_previous_state(),
        daily_inputs=_daily_inputs(),
        daily_event_plan=_daily_event_plan(),
        frozen_parameter_set=_frozen_parameter_set(),
    )


def test_working_state_is_initialized_from_previous_state() -> None:
    """Copy all tracked nitrogen masses into WorkingState."""
    context = _context()

    assert context.working_state.organic_n_mass_mg == 120.0
    assert context.working_state.tan_mass_mg == 8.0
    assert context.working_state.nitrite_mass_mg == 3.0
    assert context.working_state.nitrate_mass_mg == 45.0


def test_changing_working_state_does_not_change_previous_state() -> None:
    """Protect the immutable previous state from working mutations."""
    context = _context()

    context.working_state.tan_mass_mg += 5.0

    assert context.working_state.tan_mass_mg == 13.0
    assert context.previous_state.tan_mass_mg == 8.0


def test_opening_organic_n_mass_is_preserved() -> None:
    """Preserve opening Organic-N for the one-day mineralization lag."""
    context = _context()

    context.working_state.organic_n_mass_mg += 25.0

    assert context.opening_organic_n_mass_mg == 120.0
    assert context.working_state.organic_n_mass_mg == 145.0


def test_context_stores_daily_dependencies() -> None:
    """Store daily inputs, event plan, and frozen parameters unchanged."""
    previous_state = _previous_state()
    daily_inputs = _daily_inputs()
    daily_event_plan = _daily_event_plan()
    frozen_parameter_set = _frozen_parameter_set()

    context = StepContext(
        previous_state=previous_state,
        daily_inputs=daily_inputs,
        daily_event_plan=daily_event_plan,
        frozen_parameter_set=frozen_parameter_set,
    )

    assert context.previous_state is previous_state
    assert context.daily_inputs is daily_inputs
    assert context.daily_event_plan is daily_event_plan
    assert context.frozen_parameter_set is frozen_parameter_set


def test_metrics_start_empty_and_can_be_appended() -> None:
    """Collect metrics generated during the daily calculation."""
    context = _context()

    metric = DailyMetric(
        name="tan_oxidized_mg",
        value=4.5,
        unit="mg-N",
    )

    assert context.metrics == []

    context.metrics.append(metric)

    assert context.metrics == [metric]