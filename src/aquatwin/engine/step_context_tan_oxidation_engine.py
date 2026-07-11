"""TAN oxidation engine for the StepContext pipeline."""

from aquatwin.domain.metrics import DailyMetric
from aquatwin.engine.step_context import StepContext


class StepContextTANOxidationEngine:
    """Convert TAN-N into nitrite-N in the working state."""

    @staticmethod
    def apply(context: StepContext) -> None:
        """Oxidize the configured fraction of current TAN-N."""
        fraction = (
            context.frozen_parameter_set
            .tan_oxidation_fraction_per_day
        )

        if not 0.0 <= fraction <= 1.0:
            raise ValueError(
                "tan_oxidation_fraction_per_day must be "
                "between 0.0 and 1.0."
            )

        tan_before_mg = context.working_state.tan_mass_mg
        tan_oxidized_mg = tan_before_mg * fraction

        context.working_state.tan_mass_mg -= tan_oxidized_mg
        context.working_state.nitrite_mass_mg += tan_oxidized_mg

        context.metrics.append(
            DailyMetric(
                name="tan_n_oxidized_mg",
                value=tan_oxidized_mg,
                unit="mg-N",
            )
        )