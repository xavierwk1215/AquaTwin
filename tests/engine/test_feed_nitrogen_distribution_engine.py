"""Tests for FeedNitrogenDistributionEngine."""

import pytest

from aquatwin.domain.daily_event_plan import DailyEventPlan
from aquatwin.domain.daily_inputs import DailyInputs
from aquatwin.domain.frozen_parameter_set import FrozenParameterSet
from aquatwin.domain.metrics import DailyMetric
from aquatwin.domain.state import SimulationState
from aquatwin.engine.feed_nitrogen_distribution_engine import (
    FeedNitrogenDistributionEngine,
)
from aquatwin.engine.step_context import StepContext


def make_context(
    *,
    feeding: bool,
    feed_nitrogen_mg: float | None,
) -> StepContext:
    context = StepContext(
        previous_state=SimulationState(
            organic_n_mass_mg=100.0,
            tan_mass_mg=20.0,
            nitrite_mass_mg=10.0,
            nitrate_mass_mg=50.0,
        ),
        daily_inputs=DailyInputs(
            day=1,
            water_temperature_c=25.0,
            tank_volume_l=100.0,
        ),
        daily_event_plan=DailyEventPlan(
            feeding=feeding,
            water_change=False,
            maintenance=False,
        ),
        frozen_parameter_set=FrozenParameterSet(
            model_version="test-model",
            parameter_set_version="test-parameters",
        ),
    )

    if feed_nitrogen_mg is not None:
        context.metrics.append(
            DailyMetric(
                name="total_feed_nitrogen_mg",
                value=feed_nitrogen_mg,
                unit="mg-N",
            )
        )

    return context


def test_no_feeding_event_does_not_change_state() -> None:
    context = make_context(
        feeding=False,
        feed_nitrogen_mg=80.0,
    )

    FeedNitrogenDistributionEngine.apply(context)

    assert context.working_state.organic_n_mass_mg == pytest.approx(
        100.0
    )
    assert len(context.metrics) == 1


def test_feed_nitrogen_is_added_to_organic_n() -> None:
    context = make_context(
        feeding=True,
        feed_nitrogen_mg=80.0,
    )

    FeedNitrogenDistributionEngine.apply(context)

    assert context.working_state.organic_n_mass_mg == pytest.approx(
        180.0
    )
    assert context.metrics[-1].name == "feed_organic_n_input_mg"
    assert context.metrics[-1].value == pytest.approx(80.0)
    assert context.metrics[-1].unit == "mg-N"


def test_missing_feed_nitrogen_metric_raises() -> None:
    context = make_context(
        feeding=True,
        feed_nitrogen_mg=None,
    )

    with pytest.raises(
        ValueError,
        match=(
            "total_feed_nitrogen_mg metric is required before "
            "feed nitrogen distribution."
        ),
    ):
        FeedNitrogenDistributionEngine.apply(context)


def test_negative_feed_nitrogen_raises() -> None:
    context = make_context(
        feeding=True,
        feed_nitrogen_mg=-1.0,
    )

    with pytest.raises(
        ValueError,
        match="Feed nitrogen input must be non-negative.",
    ):
        FeedNitrogenDistributionEngine.apply(context)


def test_distribution_does_not_change_dissolved_nitrogen() -> None:
    context = make_context(
        feeding=True,
        feed_nitrogen_mg=80.0,
    )

    FeedNitrogenDistributionEngine.apply(context)

    assert context.working_state.tan_mass_mg == pytest.approx(20.0)
    assert context.working_state.nitrite_mass_mg == pytest.approx(
        10.0
    )
    assert context.working_state.nitrate_mass_mg == pytest.approx(
        50.0
    )