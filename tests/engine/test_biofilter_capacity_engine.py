"""Tests for BiofilterCapacityEngine."""

import pytest

from aquatwin.domain.daily_event_plan import DailyEventPlan
from aquatwin.domain.daily_inputs import DailyInputs
from aquatwin.domain.filter_media import FilterMedia
from aquatwin.domain.filter_unit import FilterUnit
from aquatwin.domain.frozen_parameter_set import FrozenParameterSet
from aquatwin.domain.state import SimulationState
from aquatwin.engine.biofilter_capacity_engine import (
    BiofilterCapacityEngine,
)
from aquatwin.engine.step_context import StepContext


def make_filter_unit(
    *,
    maturity_fraction: float = 0.8,
    fouling_fraction: float = 0.1,
) -> FilterUnit:
    return FilterUnit(
        filter_id="filter_1",
        filter_type="canister",
        rated_flow_l_h=1000.0,
        actual_flow_l_h=700.0,
        maturity_fraction=maturity_fraction,
        fouling_fraction=fouling_fraction,
        media=(
            FilterMedia(
                media_type="ceramic_ring",
                media_volume_l=2.0,
                tan_capacity_mg_n_l_media_day=100.0,
                nitrite_capacity_mg_n_l_media_day=80.0,
                usable_fraction=0.75,
            ),
            FilterMedia(
                media_type="sintered_glass",
                media_volume_l=1.0,
                tan_capacity_mg_n_l_media_day=200.0,
                nitrite_capacity_mg_n_l_media_day=150.0,
                usable_fraction=0.5,
            ),
        ),
    )


def make_context() -> StepContext:
    return StepContext(
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
            feeding=False,
            water_change=False,
            maintenance=False,
        ),
        frozen_parameter_set=FrozenParameterSet(
            model_version="test-model",
            parameter_set_version="test-parameters",
        ),
    )


def test_calculate_tan_capacity() -> None:
    filter_unit = make_filter_unit()

    result = (
        BiofilterCapacityEngine.calculate_tan_capacity_mg_n_day(
            filter_unit
        )
    )

    assert result == pytest.approx(180.0)


def test_calculate_nitrite_capacity() -> None:
    filter_unit = make_filter_unit()

    result = (
        BiofilterCapacityEngine
        .calculate_nitrite_capacity_mg_n_day(
            filter_unit
        )
    )

    assert result == pytest.approx(140.4)


def test_apply_records_capacity_metrics() -> None:
    context = make_context()
    filter_unit = make_filter_unit()

    BiofilterCapacityEngine.apply(
        context=context,
        filter_unit=filter_unit,
    )

    assert len(context.metrics) == 2

    assert (
        context.metrics[0].name
        == "biofilter_tan_capacity_mg_day"
    )
    assert context.metrics[0].value == pytest.approx(180.0)
    assert context.metrics[0].unit == "mg-N/day"

    assert (
        context.metrics[1].name
        == "biofilter_nitrite_capacity_mg_day"
    )
    assert context.metrics[1].value == pytest.approx(140.4)
    assert context.metrics[1].unit == "mg-N/day"


def test_zero_maturity_produces_zero_capacity() -> None:
    filter_unit = make_filter_unit(
        maturity_fraction=0.0,
    )

    tan_capacity = (
        BiofilterCapacityEngine.calculate_tan_capacity_mg_n_day(
            filter_unit
        )
    )
    nitrite_capacity = (
        BiofilterCapacityEngine
        .calculate_nitrite_capacity_mg_n_day(
            filter_unit
        )
    )

    assert tan_capacity == pytest.approx(0.0)
    assert nitrite_capacity == pytest.approx(0.0)


def test_full_fouling_produces_zero_capacity() -> None:
    filter_unit = make_filter_unit(
        fouling_fraction=1.0,
    )

    tan_capacity = (
        BiofilterCapacityEngine.calculate_tan_capacity_mg_n_day(
            filter_unit
        )
    )
    nitrite_capacity = (
        BiofilterCapacityEngine
        .calculate_nitrite_capacity_mg_n_day(
            filter_unit
        )
    )

    assert tan_capacity == pytest.approx(0.0)
    assert nitrite_capacity == pytest.approx(0.0)