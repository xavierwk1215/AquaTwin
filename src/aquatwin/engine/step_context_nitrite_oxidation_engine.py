"""Nitrite oxidation engine for the StepContext pipeline."""

from aquatwin.domain.metrics import DailyMetric
from aquatwin.engine.step_context import StepContext


class StepContextNitriteOxidationEngine:
    """Convert nitrite-N into nitrate-N in the working state."""

    @staticmethod
    def apply(context: StepContext) -> None:
        """Oxidize the configured fraction of current nitrite-N."""
        fraction = (
            context.frozen_parameter_set
            .nitrite_oxidation_fraction_per_day
        )

        if not 0.0 <= fraction <= 1.0:
            raise ValueError(
                "nitrite_oxidation_fraction_per_day must be "
                "between 0.0 and 1.0."
            )

        nitrite_before_mg = context.working_state.nitrite_mass_mg
        nitrite_oxidized_mg = nitrite_before_mg * fraction

        context.working_state.nitrite_mass_mg -= nitrite_oxidized_mg
        context.working_state.nitrate_mass_mg += nitrite_oxidized_mg

        context.metrics.append(
            DailyMetric(
                name="nitrite_n_oxidized_mg",
                value=nitrite_oxidized_mg,
                unit="mg-N",
            )
        )