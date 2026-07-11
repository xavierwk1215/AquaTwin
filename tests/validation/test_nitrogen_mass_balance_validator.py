"""Tests for NitrogenMassBalanceValidator."""

from math import inf, nan

import pytest

from aquatwin.domain.daily_event_plan import DailyEventPlan
from aquatwin.domain.daily_inputs import DailyInputs
from aquatwin.domain.frozen_parameter_set import FrozenParameterSet
from aquatwin.domain.metrics import DailyMetric
from aquatwin.domain.state import SimulationState
from aquatwin.engine.step_context import StepContext
from aquatwin.validation.nitrogen_mass_balance_validator import (
    NitrogenMassBalanceValidator,
)
from aquatwin.validation.validation_error import ValidationSeverity


def make_context(
    *,
    opening_state: SimulationState | None = None,
    closing_state: SimulationState | None = None,
    metrics: list[DailyMetric] | None = None,
) -> StepContext:
    """Create a StepContext for mass-balance validation tests."""
    context = StepContext(
        previous_state=opening_state
        or SimulationState(
            organic_n_mass_mg=40.0,
            tan_mass_mg=20.0,
            nitrite_mass_mg=10.0,
            nitrate_mass_mg=30.0,
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

    if closing_state is not None:
        context.working_state.organic_n_mass_mg = (
            closing_state.organic_n_mass_mg
        )
        context.working_state.tan_mass_mg = (
            closing_state.tan_mass_mg
        )
        context.working_state.nitrite_mass_mg = (
            closing_state.nitrite_mass_mg
        )
        context.working_state.nitrate_mass_mg = (
            closing_state.nitrate_mass_mg
        )

    if metrics is not None:
        context.metrics.extend(metrics)

    return context


def metric(
    name: str,
    value: float,
) -> DailyMetric:
    """Create one nitrogen mass metric."""
    return DailyMetric(
        name=name,
        value=value,
        unit="mg-N",
    )


def test_unchanged_total_nitrogen_returns_valid_result() -> None:
    """Accept internal nitrogen transformations that preserve total mass."""
    context = make_context(
        closing_state=SimulationState(
            organic_n_mass_mg=20.0,
            tan_mass_mg=25.0,
            nitrite_mass_mg=15.0,
            nitrate_mass_mg=40.0,
        )
    )

    result = NitrogenMassBalanceValidator.validate(context)

    assert result.is_valid
    assert result.findings == ()


def test_external_inputs_increase_expected_closing_total() -> None:
    """Include feed, metabolism, and source-water nitrogen inputs."""
    context = make_context(
        closing_state=SimulationState(
            organic_n_mass_mg=50.0,
            tan_mass_mg=23.0,
            nitrite_mass_mg=10.0,
            nitrate_mass_mg=32.0,
        ),
        metrics=[
            metric("feed_organic_n_input_mg", 10.0),
            metric("metabolic_tan_input_mg", 3.0),
            metric("source_water_n_input_mg", 2.0),
        ],
    )

    result = NitrogenMassBalanceValidator.validate(context)

    assert result.is_valid
    assert result.findings == ()


def test_external_removals_reduce_expected_closing_total() -> None:
    """Include water-change and maintenance nitrogen removals."""
    context = make_context(
        closing_state=SimulationState(
            organic_n_mass_mg=35.0,
            tan_mass_mg=17.0,
            nitrite_mass_mg=8.0,
            nitrate_mass_mg=25.0,
        ),
        metrics=[
            metric("water_change_n_removal_mg", 10.0),
            metric("maintenance_n_removal_mg", 5.0),
        ],
    )

    result = NitrogenMassBalanceValidator.validate(context)

    assert result.is_valid
    assert result.findings == ()


def test_inputs_and_removals_are_combined() -> None:
    """Balance simultaneous external inputs and removals."""
    context = make_context(
        closing_state=SimulationState(
            organic_n_mass_mg=42.0,
            tan_mass_mg=20.0,
            nitrite_mass_mg=10.0,
            nitrate_mass_mg=30.0,
        ),
        metrics=[
            metric("feed_organic_n_input_mg", 8.0),
            metric("metabolic_tan_input_mg", 4.0),
            metric("water_change_n_removal_mg", 7.0),
            metric("maintenance_n_removal_mg", 3.0),
        ],
    )

    result = NitrogenMassBalanceValidator.validate(context)

    assert result.is_valid
    assert result.findings == ()


def test_mass_balance_violation_returns_error() -> None:
    """Reject unexplained nitrogen creation or disappearance."""
    context = make_context(
        closing_state=SimulationState(
            organic_n_mass_mg=40.0,
            tan_mass_mg=20.0,
            nitrite_mass_mg=10.0,
            nitrate_mass_mg=31.0,
        )
    )

    result = NitrogenMassBalanceValidator.validate(context)

    assert not result.is_valid
    assert len(result.findings) == 1

    finding = result.findings[0]

    assert finding.code == "NITROGEN_MASS_BALANCE_VIOLATION"
    assert finding.field == "closing_total_n_mg"
    assert finding.severity is ValidationSeverity.ERROR


@pytest.mark.parametrize(
    "invalid_value",
    [nan, inf, -inf],
)
def test_non_finite_mass_balance_metric_returns_error(
    invalid_value: float,
) -> None:
    """Reject non-finite input or removal metrics."""
    context = make_context(
        metrics=[
            metric(
                "feed_organic_n_input_mg",
                invalid_value,
            )
        ]
    )

    result = NitrogenMassBalanceValidator.validate(context)

    assert not result.is_valid
    assert len(result.findings) == 1

    finding = result.findings[0]

    assert finding.code == "NON_FINITE_MASS_BALANCE_METRIC"
    assert finding.field == "feed_organic_n_input_mg"
    assert finding.severity is ValidationSeverity.ERROR


def test_negative_mass_balance_metric_returns_error() -> None:
    """Reject negative external nitrogen metrics."""
    context = make_context(
        metrics=[
            metric(
                "water_change_n_removal_mg",
                -1.0,
            )
        ]
    )

    result = NitrogenMassBalanceValidator.validate(context)

    assert not result.is_valid
    assert len(result.findings) == 1

    finding = result.findings[0]

    assert finding.code == "NEGATIVE_MASS_BALANCE_METRIC"
    assert finding.field == "water_change_n_removal_mg"
    assert finding.severity is ValidationSeverity.ERROR


def test_latest_duplicate_metric_is_used() -> None:
    """Use the latest metric when the same name is recorded repeatedly."""
    context = make_context(
        closing_state=SimulationState(
            organic_n_mass_mg=45.0,
            tan_mass_mg=20.0,
            nitrite_mass_mg=10.0,
            nitrate_mass_mg=30.0,
        ),
        metrics=[
            metric("feed_organic_n_input_mg", 20.0),
            metric("feed_organic_n_input_mg", 5.0),
        ],
    )

    result = NitrogenMassBalanceValidator.validate(context)

    assert result.is_valid
    assert result.findings == ()


def test_small_floating_point_difference_is_allowed() -> None:
    """Allow insignificant floating-point rounding differences."""
    context = make_context(
        closing_state=SimulationState(
            organic_n_mass_mg=40.0,
            tan_mass_mg=20.0,
            nitrite_mass_mg=10.0,
            nitrate_mass_mg=30.00000000005,
        )
    )

    result = NitrogenMassBalanceValidator.validate(context)

    assert result.is_valid
    assert result.findings == ()