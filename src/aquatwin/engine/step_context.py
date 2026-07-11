"""Execution context for one daily simulation step."""

from dataclasses import dataclass, field

from aquatwin.domain.daily_event_plan import DailyEventPlan
from aquatwin.domain.daily_inputs import DailyInputs
from aquatwin.domain.frozen_parameter_set import FrozenParameterSet
from aquatwin.domain.metrics import DailyMetric
from aquatwin.domain.state import SimulationState


@dataclass
class WorkingState:
    """Hold temporary mutable nitrogen state during one simulation day."""

    organic_n_mass_mg: float
    tan_mass_mg: float
    nitrite_mass_mg: float
    nitrate_mass_mg: float

    @classmethod
    def from_simulation_state(
        cls,
        state: SimulationState,
    ) -> "WorkingState":
        """Create a mutable working copy from an immutable simulation state."""
        return cls(
            organic_n_mass_mg=state.organic_n_mass_mg,
            tan_mass_mg=state.tan_mass_mg,
            nitrite_mass_mg=state.nitrite_mass_mg,
            nitrate_mass_mg=state.nitrate_mass_mg,
        )

    def to_simulation_state(self) -> SimulationState:
        """Create an immutable simulation state from current working values."""
        return SimulationState(
            organic_n_mass_mg=self.organic_n_mass_mg,
            tan_mass_mg=self.tan_mass_mg,
            nitrite_mass_mg=self.nitrite_mass_mg,
            nitrate_mass_mg=self.nitrate_mass_mg,
        )


@dataclass
class StepContext:
    """Carry state, inputs, parameters, and metrics for one daily step."""

    previous_state: SimulationState
    daily_inputs: DailyInputs
    daily_event_plan: DailyEventPlan
    frozen_parameter_set: FrozenParameterSet
    metrics: list[DailyMetric] = field(default_factory=list)

    working_state: WorkingState = field(init=False)
    opening_organic_n_mass_mg: float = field(init=False)

    def __post_init__(self) -> None:
        """Initialize temporary state and preserve opening Organic-N."""
        self.working_state = WorkingState.from_simulation_state(
            self.previous_state,
        )
        self.opening_organic_n_mass_mg = (
            self.previous_state.organic_n_mass_mg
        )