"""Nitrite oxidation engine for the StepContext pipeline."""

from aquatwin.domain.metrics import DailyMetric
from aquatwin.engine.step_context import StepContext


class StepContextNitriteOxidationEngine:
    """Convert nitrite-N into nitrate-N within biofilter capacity."""

    @staticmethod
    def apply(context: StepContext) -> None:
        """Oxidize nitrite-N using the configured rate and capacity limit."""
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
        potential_nitrite_oxidized_mg = (
            nitrite_before_mg * fraction
        )

        capacity_metric = next(
            (
                metric
                for metric in context.metrics
                if metric.name
                == "biofilter_nitrite_capacity_mg_day"
            ),
            None,
        )

        nitrite_oxidized_mg = potential_nitrite_oxidized_mg

        if capacity_metric is not None:
            if capacity_metric.value < 0.0:
                raise ValueError(
                    "Biofilter nitrite capacity must be non-negative."
                )

            nitrite_oxidized_mg = min(
                potential_nitrite_oxidized_mg,
                capacity_metric.value,
            )

        context.working_state.nitrite_mass_mg -= (
            nitrite_oxidized_mg
        )
        context.working_state.nitrate_mass_mg += (
            nitrite_oxidized_mg
        )

        context.metrics.extend(
            [
                DailyMetric(
                    name="potential_nitrite_n_oxidized_mg",
                    value=potential_nitrite_oxidized_mg,
                    unit="mg-N",
                ),
                DailyMetric(
                    name="nitrite_n_oxidized_mg",
                    value=nitrite_oxidized_mg,
                    unit="mg-N",
                ),
            ]
        )