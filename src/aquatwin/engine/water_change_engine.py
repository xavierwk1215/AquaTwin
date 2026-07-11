"""Water-change engine for the daily simulation pipeline."""

from aquatwin.domain.metrics import DailyMetric
from aquatwin.engine.step_context import StepContext


class WaterChangeEngine:
    """Apply a beginning-of-day water change to dissolved nitrogen."""

    @staticmethod
    def apply(context: StepContext) -> None:
        """Apply the resolved water-change event to WorkingState.

        Organic-N is not removed by routine water changes in the MVP.
        Only dissolved TAN-N, nitrite-N, and nitrate-N are adjusted.

        The engine mutates only ``context.working_state`` and appends
        explanatory daily metrics.
        """
        event_plan = context.daily_event_plan

        if not event_plan.water_change:
            return

        water_change_fraction = event_plan.water_change_fraction

        if not 0.0 <= water_change_fraction <= 1.0:
            raise ValueError(
                "water_change_fraction must be between 0.0 and 1.0.",
            )

        tank_volume_l = context.daily_inputs.tank_volume_l

        if tank_volume_l <= 0.0:
            raise ValueError(
                "tank_volume_l must be greater than 0.0 "
                "when applying a water change.",
            )

        remaining_fraction = 1.0 - water_change_fraction
        replacement_volume_l = tank_volume_l * water_change_fraction

        working_state = context.working_state
        daily_inputs = context.daily_inputs

        tan_before_mg = working_state.tan_mass_mg
        nitrite_before_mg = working_state.nitrite_mass_mg
        nitrate_before_mg = working_state.nitrate_mass_mg

        tan_removed_mg = tan_before_mg * water_change_fraction
        nitrite_removed_mg = (
            nitrite_before_mg * water_change_fraction
        )
        nitrate_removed_mg = (
            nitrate_before_mg * water_change_fraction
        )

        source_tan_input_mg = (
            replacement_volume_l
            * daily_inputs.source_tan_mg_n_l
        )
        source_nitrite_input_mg = (
            replacement_volume_l
            * daily_inputs.source_nitrite_mg_n_l
        )
        source_nitrate_input_mg = (
            replacement_volume_l
            * daily_inputs.source_nitrate_mg_n_l
        )

        working_state.tan_mass_mg = (
            tan_before_mg * remaining_fraction
            + source_tan_input_mg
        )
        working_state.nitrite_mass_mg = (
            nitrite_before_mg * remaining_fraction
            + source_nitrite_input_mg
        )
        working_state.nitrate_mass_mg = (
            nitrate_before_mg * remaining_fraction
            + source_nitrate_input_mg
        )

        total_removal_mg = (
            tan_removed_mg
            + nitrite_removed_mg
            + nitrate_removed_mg
        )
        total_source_input_mg = (
            source_tan_input_mg
            + source_nitrite_input_mg
            + source_nitrate_input_mg
        )

        context.metrics.extend(
            (
                DailyMetric(
                    name="water_change_n_removal_mg",
                    value=total_removal_mg,
                    unit="mg-N",
                ),
                DailyMetric(
                    name="source_water_n_input_mg",
                    value=total_source_input_mg,
                    unit="mg-N",
                ),
                DailyMetric(
                    name="water_change_fraction",
                    value=water_change_fraction,
                    unit="fraction",
                ),
            )
        )