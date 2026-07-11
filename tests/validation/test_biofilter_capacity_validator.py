"""Tests for BiofilterCapacityValidator."""

from math import inf, nan

import pytest

from aquatwin.domain.daily_event_plan import DailyEventPlan
from aquatwin.domain.daily_inputs import DailyInputs
from aquatwin.domain.frozen_parameter_set import FrozenParameterSet
from aquatwin.domain.metrics import DailyMetric
from aquatwin.domain.state import SimulationState
from aquatwin.engine.step_context import StepContext
from aquatwin.validation.biofilter_capacity_validator import (
    BiofilterCapacityValidator,
)
from aquatwin.validation.validation_error import ValidationSeverity


def make_context(
    metrics: list[DailyMetric] | None = None,
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
            feeding=False,
            water_change=False,
            maintenance=False,
        ),
        frozen_parameter_set=FrozenParameterSet(
            model_version="test-model",
            parameter_set_version="test-parameters",
        ),
    )

    if metrics is not None:
        context.metrics.extend(metrics)

    return context


def metric(
    name: str,
    value: float,
    unit: str = "mg-N",
) -> DailyMetric:
    return DailyMetric(
        name=name,
        value=value,
        unit=unit,
    )


def test_valid_oxidation_metrics_return_valid_result() -> None:
    context = make_context(
        [
            metric(
                "potential_tan_n_oxidized_mg",
                20.0,
            ),
            metric(
                "biofilter_tan_capacity_mg_day",
                15.0,
                "mg-N/day",
            ),
            metric(
                "tan_n_oxidized_mg",
                15.0,
            ),
            metric(
                "potential_nitrite_n_oxidized_mg",
                10.0,
            ),
            metric(
                "biofilter_nitrite_capacity_mg_day",
                8.0,
                "mg-N/day",
            ),
            metric(
                "nitrite_n_oxidized_mg",
                8.0,
            ),
        ]
    )

    result = BiofilterCapacityValidator.validate(context)

    assert result.is_valid
    assert result.findings == ()


def test_tan_oxidation_exceeding_potential_returns_error() -> None:
    context = make_context(
        [
            metric(
                "potential_tan_n_oxidized_mg",
                10.0,
            ),
            metric(
                "tan_n_oxidized_mg",
                11.0,
            ),
        ]
    )

    result = BiofilterCapacityValidator.validate(context)

    assert not result.is_valid
    assert len(result.findings) == 1

    finding = result.findings[0]

    assert finding.code == "OXIDATION_EXCEEDS_POTENTIAL"
    assert finding.field == "tan_n_oxidized_mg"
    assert finding.severity is ValidationSeverity.ERROR


def test_tan_oxidation_exceeding_capacity_returns_error() -> None:
    context = make_context(
        [
            metric(
                "potential_tan_n_oxidized_mg",
                20.0,
            ),
            metric(
                "biofilter_tan_capacity_mg_day",
                10.0,
                "mg-N/day",
            ),
            metric(
                "tan_n_oxidized_mg",
                11.0,
            ),
        ]
    )

    result = BiofilterCapacityValidator.validate(context)

    assert not result.is_valid
    assert len(result.findings) == 1

    finding = result.findings[0]

    assert (
        finding.code
        == "OXIDATION_EXCEEDS_BIOFILTER_CAPACITY"
    )
    assert finding.field == "tan_n_oxidized_mg"
    assert finding.severity is ValidationSeverity.ERROR


def test_nitrite_oxidation_exceeding_potential_returns_error() -> None:
    context = make_context(
        [
            metric(
                "potential_nitrite_n_oxidized_mg",
                5.0,
            ),
            metric(
                "nitrite_n_oxidized_mg",
                6.0,
            ),
        ]
    )

    result = BiofilterCapacityValidator.validate(context)

    assert not result.is_valid
    assert len(result.findings) == 1

    finding = result.findings[0]

    assert finding.code == "OXIDATION_EXCEEDS_POTENTIAL"
    assert finding.field == "nitrite_n_oxidized_mg"
    assert finding.severity is ValidationSeverity.ERROR


def test_nitrite_oxidation_exceeding_capacity_returns_error() -> None:
    context = make_context(
        [
            metric(
                "potential_nitrite_n_oxidized_mg",
                10.0,
            ),
            metric(
                "biofilter_nitrite_capacity_mg_day",
                4.0,
                "mg-N/day",
            ),
            metric(
                "nitrite_n_oxidized_mg",
                5.0,
            ),
        ]
    )

    result = BiofilterCapacityValidator.validate(context)

    assert not result.is_valid
    assert len(result.findings) == 1

    finding = result.findings[0]

    assert (
        finding.code
        == "OXIDATION_EXCEEDS_BIOFILTER_CAPACITY"
    )
    assert finding.field == "nitrite_n_oxidized_mg"
    assert finding.severity is ValidationSeverity.ERROR


def test_oxidation_exceeding_both_limits_returns_two_errors() -> None:
    context = make_context(
        [
            metric(
                "potential_tan_n_oxidized_mg",
                8.0,
            ),
            metric(
                "biofilter_tan_capacity_mg_day",
                7.0,
                "mg-N/day",
            ),
            metric(
                "tan_n_oxidized_mg",
                9.0,
            ),
        ]
    )

    result = BiofilterCapacityValidator.validate(context)

    assert not result.is_valid
    assert len(result.findings) == 2

    assert {
        finding.code
        for finding in result.findings
    } == {
        "OXIDATION_EXCEEDS_POTENTIAL",
        "OXIDATION_EXCEEDS_BIOFILTER_CAPACITY",
    }


@pytest.mark.parametrize(
    "invalid_value",
    [nan, inf, -inf],
)
def test_non_finite_metric_returns_error(
    invalid_value: float,
) -> None:
    context = make_context(
        [
            metric(
                "tan_n_oxidized_mg",
                invalid_value,
            ),
        ]
    )

    result = BiofilterCapacityValidator.validate(context)

    assert not result.is_valid
    assert len(result.findings) == 1

    finding = result.findings[0]

    assert finding.code == "NON_FINITE_BIOFILTER_METRIC"
    assert finding.field == "tan_n_oxidized_mg"
    assert finding.severity is ValidationSeverity.ERROR


def test_negative_metric_returns_error() -> None:
    context = make_context(
        [
            metric(
                "biofilter_tan_capacity_mg_day",
                -1.0,
                "mg-N/day",
            ),
        ]
    )

    result = BiofilterCapacityValidator.validate(context)

    assert not result.is_valid
    assert len(result.findings) == 1

    finding = result.findings[0]

    assert finding.code == "NEGATIVE_BIOFILTER_METRIC"
    assert finding.field == "biofilter_tan_capacity_mg_day"
    assert finding.severity is ValidationSeverity.ERROR


def test_missing_metrics_are_allowed_for_legacy_compatibility() -> None:
    context = make_context()

    result = BiofilterCapacityValidator.validate(context)

    assert result.is_valid
    assert result.findings == ()


def test_latest_duplicate_metric_is_used() -> None:
    context = make_context(
        [
            metric(
                "potential_tan_n_oxidized_mg",
                5.0,
            ),
            metric(
                "tan_n_oxidized_mg",
                10.0,
            ),
            metric(
                "potential_tan_n_oxidized_mg",
                10.0,
            ),
        ]
    )

    result = BiofilterCapacityValidator.validate(context)

    assert result.is_valid
    assert result.findings == ()