"""Feed nitrogen distribution for the StepContext pipeline."""

from aquatwin.domain.metrics import DailyMetric
from aquatwin.engine.step_context import StepContext


class FeedNitrogenDistributionEngine:
    """Transfer today's feed nitrogen into modelled Organic-N."""

    @staticmethod
    def apply(context: StepContext) -> None:
        """Add today's feed nitrogen to WorkingState Organic-N."""
        if not context.daily_event_plan.feeding:
            return

        feed_nitrogen_metric = next(
            (
                metric
                for metric in context.metrics
                if metric.name == "total_feed_nitrogen_mg"
            ),
            None,
        )

        if feed_nitrogen_metric is None:
            raise ValueError(
                "total_feed_nitrogen_mg metric is required before "
                "feed nitrogen distribution."
            )

        feed_organic_n_input_mg = feed_nitrogen_metric.value

        if feed_organic_n_input_mg < 0.0:
            raise ValueError(
                "Feed nitrogen input must be non-negative."
            )

        context.working_state.organic_n_mass_mg += (
            feed_organic_n_input_mg
        )

        context.metrics.append(
            DailyMetric(
                name="feed_organic_n_input_mg",
                value=feed_organic_n_input_mg,
                unit="mg-N",
            )
        )