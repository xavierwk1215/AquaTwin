"""Maintenance engine for the daily simulation pipeline."""

from aquatwin.domain.metrics import DailyMetric
from aquatwin.engine.step_context import StepContext


class MaintenanceEngine:
    """Remove modelled Organic-N through an explicit maintenance event."""

    @staticmethod
    def apply(context: StepContext) -> None:
        """Apply the resolved maintenance event to WorkingState.

        Maintenance represents physical removal of settled organic material,
        such as substrate cleaning or waste siphoning.

        Only modelled Organic-N is removed. Dissolved TAN-N, nitrite-N,
        and nitrate-N are not changed by this engine.

        The engine mutates only ``context.working_state`` and appends an
        explanatory daily metric.
        """
        event_plan = context.daily_event_plan

        if not event_plan.maintenance:
            return

        maintenance_fraction = event_plan.maintenance_fraction

        if not 0.0 <= maintenance_fraction <= 1.0:
            raise ValueError(
                "maintenance_fraction must be between 0.0 and 1.0.",
            )

        working_state = context.working_state
        organic_n_before_mg = working_state.organic_n_mass_mg

        maintenance_n_removal_mg = (
            organic_n_before_mg * maintenance_fraction
        )

        working_state.organic_n_mass_mg = (
            organic_n_before_mg - maintenance_n_removal_mg
        )

        context.metrics.append(
            DailyMetric(
                name="maintenance_n_removal_mg",
                value=maintenance_n_removal_mg,
                unit="mg-N",
            )
        )