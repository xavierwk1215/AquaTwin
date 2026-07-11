"""Official multi-day StepContext simulation runner."""

from collections.abc import Callable

from aquatwin.domain.daily_event_plan import DailyEventPlan
from aquatwin.domain.daily_inputs import DailyInputs
from aquatwin.domain.daily_simulation_result import (
    DailySimulationResult,
)
from aquatwin.domain.filter_unit import FilterUnit
from aquatwin.domain.frozen_parameter_set import FrozenParameterSet
from aquatwin.domain.state import SimulationState
from aquatwin.engine.daily_simulation_engine import (
    DailySimulationEngine,
)
from aquatwin.engine.step_context import StepContext

DailyInputsFactory = Callable[[int], DailyInputs]
DailyEventPlanFactory = Callable[[int], DailyEventPlan]


class DailySimulationRunner:
    """Run the official StepContext simulation for consecutive days."""

    def __init__(
        self,
        initial_state: SimulationState,
        frozen_parameter_set: FrozenParameterSet,
        filter_unit: FilterUnit,
        daily_inputs_factory: DailyInputsFactory,
        daily_event_plan_factory: DailyEventPlanFactory,
    ) -> None:
        self._initial_state = initial_state
        self._frozen_parameter_set = frozen_parameter_set
        self._filter_unit = filter_unit
        self._daily_inputs_factory = daily_inputs_factory
        self._daily_event_plan_factory = daily_event_plan_factory

    def run(self, days: int) -> list[DailySimulationResult]:
        """Run the official simulation pipeline for multiple days."""
        self._validate_days(days)

        current_state = self._initial_state
        results: list[DailySimulationResult] = []

        for simulation_day in range(1, days + 1):
            daily_inputs = self._daily_inputs_factory(simulation_day)
            daily_event_plan = self._daily_event_plan_factory(
                simulation_day
            )

            if daily_inputs.day != simulation_day:
                raise ValueError(
                    "daily_inputs_factory must return DailyInputs "
                    "with a day matching the requested simulation day."
                )

            context = StepContext(
                previous_state=current_state,
                daily_inputs=daily_inputs,
                daily_event_plan=daily_event_plan,
                frozen_parameter_set=self._frozen_parameter_set,
            )

            result = DailySimulationEngine.run(
                context=context,
                filter_unit=self._filter_unit,
            )

            results.append(result)
            current_state = result.new_state

        return results

    @staticmethod
    def _validate_days(days: int) -> None:
        """Validate simulation duration."""
        if isinstance(days, bool) or not isinstance(days, int):
            raise TypeError("days must be an integer.")

        if days < 1:
            raise ValueError(
                "days must be greater than or equal to 1."
            )