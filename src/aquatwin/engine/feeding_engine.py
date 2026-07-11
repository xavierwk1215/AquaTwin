"""Feeding engines for legacy and StepContext pipelines."""

from aquatwin.domain.metrics import DailyMetric
from aquatwin.engine.biomass_calculator import BiomassCalculator
from aquatwin.engine.feed_nitrogen_engine import FeedNitrogenEngine
from aquatwin.engine.step_context import StepContext


class FeedingEngine:
    """Support legacy feed conversion and StepContext feeding metrics."""

    @staticmethod
    def calculate_organic_n(
        food_mass_g: float,
        protein_fraction: float,
        nitrogen_conversion_factor: float,
    ) -> float:
        """Convert supplied food mass into Organic-N mass in milligrams."""
        return (
            food_mass_g
            * protein_fraction
            * nitrogen_conversion_factor
            * 1000.0
        )

    @staticmethod
    def apply(context: StepContext) -> None:
        """Calculate and record daily feeding values."""
        event_plan = context.daily_event_plan

        if not event_plan.feeding:
            return

        fish_cohorts = context.daily_inputs.fish_cohorts
        frozen_parameter_set = context.frozen_parameter_set

        total_biomass_g = BiomassCalculator.calculate_total_biomass_g(
            cohorts=fish_cohorts,
            frozen_parameter_set=frozen_parameter_set,
        )

        total_feed_mass_g = (
            FeedNitrogenEngine.calculate_total_feed_mass_g(
                cohorts=fish_cohorts,
                frozen_parameter_set=frozen_parameter_set,
            )
        )

        total_feed_nitrogen_mg = (
            FeedNitrogenEngine.calculate_total_feed_nitrogen_mg(
                cohorts=fish_cohorts,
                frozen_parameter_set=frozen_parameter_set,
            )
        )

        context.metrics.extend(
            [
                DailyMetric(
                    name="total_biomass_g",
                    value=total_biomass_g,
                    unit="g",
                ),
                DailyMetric(
                    name="total_feed_mass_g",
                    value=total_feed_mass_g,
                    unit="g",
                ),
                DailyMetric(
                    name="total_feed_nitrogen_mg",
                    value=total_feed_nitrogen_mg,
                    unit="mg-N",
                ),
            ]
        )