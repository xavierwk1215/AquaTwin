"""TAN oxidation engine for the StepContext pipeline."""

from aquatwin.domain.metrics import DailyMetric
from aquatwin.engine.step_context import StepContext


class StepContextTANOxidationEngine:
    """Convert TAN-N into nitrite-N within biofilter capacity."""

    @staticmethod
    def apply(context: StepContext) -> None:
        """Oxidize TAN-N using the configured rate and capacity limit."""
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
        potential_tan_oxidized_mg = tan_before_mg * fraction

        capacity_metric = next(
            (
                metric
                for metric in context.metrics
                if metric.name
                == "biofilter_tan_capacity_mg_day"
            ),
            None,
        )

        tan_oxidized_mg = potential_tan_oxidized_mg

        if capacity_metric is not None:
            if capacity_metric.value < 0.0:
                raise ValueError(
                    "Biofilter TAN capacity must be non-negative."
                )

            tan_oxidized_mg = min(
                potential_tan_oxidized_mg,
                capacity_metric.value,
            )

        context.working_state.tan_mass_mg -= tan_oxidized_mg
        context.working_state.nitrite_mass_mg += tan_oxidized_mg

        context.metrics.extend(
            [
                DailyMetric(
                    name="potential_tan_n_oxidized_mg",
                    value=potential_tan_oxidized_mg,
                    unit="mg-N",
                ),
                DailyMetric(
                    name="tan_n_oxidized_mg",
                    value=tan_oxidized_mg,
                    unit="mg-N",
                ),
            ]
        )