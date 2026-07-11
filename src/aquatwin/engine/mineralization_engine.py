"""Mineralization engine for the StepContext pipeline."""

from aquatwin.domain.metrics import DailyMetric
from aquatwin.engine.step_context import StepContext


class MineralizationEngine:
    """Convert opening Organic-N into TAN-N."""

    @staticmethod
    def apply(context: StepContext) -> None:
        """Mineralize only the opening Organic-N present at day start."""
        fraction = (
            context.frozen_parameter_set
            .organic_n_mineralization_fraction_per_day
        )

        if not 0.0 <= fraction <= 1.0:
            raise ValueError(
                "organic_n_mineralization_fraction_per_day "
                "must be between 0.0 and 1.0."
            )

        opening_organic_n_mg = context.opening_organic_n_mass_mg

        mineralized_n_mg = opening_organic_n_mg * fraction

        context.working_state.organic_n_mass_mg -= mineralized_n_mg
        context.working_state.tan_mass_mg += mineralized_n_mg

        context.metrics.append(
            DailyMetric(
                name="organic_n_mineralized_mg",
                value=mineralized_n_mg,
                unit="mg-N",
            )
        )