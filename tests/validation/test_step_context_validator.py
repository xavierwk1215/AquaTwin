"""Tests for StepContextValidator."""

from aquatwin.domain.daily_event_plan import DailyEventPlan
from aquatwin.domain.daily_inputs import DailyInputs
from aquatwin.domain.frozen_parameter_set import FrozenParameterSet
from aquatwin.domain.metrics import DailyMetric
from aquatwin.domain.state import SimulationState
from aquatwin.engine.step_context import StepContext
from aquatwin.validation.step_context_validator import (
    StepContextValidator,
)


def make_context(
    *,
    feeding: bool = False,
    metrics: list[DailyMetric] | None = None,
) -> StepContext:
    """Create a StepContext for combined validation tests."""
    context = StepContext(
        previous_state=SimulationState(
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
            feeding=feeding,
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
    """Create one daily simulation metric."""
    return DailyMetric(
        name=name,
        value=value,
        unit=unit,
    )


def test_valid_context_returns_valid_result() -> None:
    """Accept a completed context that satisfies all validators."""
    context = make_context()

    result = StepContextValidator.validate(context)

    assert result.is_valid
    assert result.findings == ()


def test_state_validation_findings_are_included() -> None:
    """Include findings from SimulationStateValidator."""
    context = make_context()
    context.working_state.tan_mass_mg = -1.0
    context.working_state.nitrate_mass_mg = 31.0

    result = StepContextValidator.validate(context)

    assert not result.is_valid
    assert any(
        finding.code == "NEGATIVE_NITROGEN_MASS"
        and finding.field == "tan_mass_mg"
        for finding in result.findings
    )


def test_biofilter_capacity_findings_are_included() -> None:
    """Include findings from BiofilterCapacityValidator."""
    context = make_context(
        metrics=[
            metric(
                "potential_tan_n_oxidized_mg",
                5.0,
            ),
            metric(
                "biofilter_tan_capacity_mg_day",
                4.0,
                "mg-N/day",
            ),
            metric(
                "tan_n_oxidized_mg",
                6.0,
            ),
        ]
    )

    result = StepContextValidator.validate(context)

    assert not result.is_valid

    finding_codes = {
        finding.code
        for finding in result.findings
    }

    assert "OXIDATION_EXCEEDS_POTENTIAL" in finding_codes
    assert "OXIDATION_EXCEEDS_BIOFILTER_CAPACITY" in finding_codes


def test_feed_conservation_findings_are_included() -> None:
    """Include findings from FeedNitrogenConservationValidator."""
    context = make_context(
        feeding=True,
        metrics=[
            metric(
                "total_feed_nitrogen_mg",
                10.0,
            ),
            metric(
                "feed_organic_n_input_mg",
                8.0,
            ),
        ],
    )
    context.working_state.organic_n_mass_mg = 48.0

    result = StepContextValidator.validate(context)

    assert not result.is_valid
    assert any(
        finding.code == "FEED_NITROGEN_NOT_CONSERVED"
        for finding in result.findings
    )


def test_mass_balance_findings_are_included() -> None:
    """Include findings from NitrogenMassBalanceValidator."""
    context = make_context()
    context.working_state.nitrate_mass_mg = 31.0

    result = StepContextValidator.validate(context)

    assert not result.is_valid
    assert any(
        finding.code == "NITROGEN_MASS_BALANCE_VIOLATION"
        for finding in result.findings
    )


def test_findings_from_multiple_validators_are_combined() -> None:
    """Combine findings from every failing validator."""
    context = make_context(
        feeding=True,
        metrics=[
            metric(
                "total_feed_nitrogen_mg",
                10.0,
            ),
            metric(
                "feed_organic_n_input_mg",
                8.0,
            ),
            metric(
                "potential_tan_n_oxidized_mg",
                5.0,
            ),
            metric(
                "biofilter_tan_capacity_mg_day",
                4.0,
                "mg-N/day",
            ),
            metric(
                "tan_n_oxidized_mg",
                6.0,
            ),
        ],
    )

    context.working_state.organic_n_mass_mg = 48.0
    context.working_state.tan_mass_mg = -1.0
    context.working_state.nitrate_mass_mg = 33.0

    result = StepContextValidator.validate(context)

    assert not result.is_valid

    finding_codes = {
        finding.code
        for finding in result.findings
    }

    assert "NEGATIVE_NITROGEN_MASS" in finding_codes
    assert "OXIDATION_EXCEEDS_POTENTIAL" in finding_codes
    assert "OXIDATION_EXCEEDS_BIOFILTER_CAPACITY" in finding_codes
    assert "FEED_NITROGEN_NOT_CONSERVED" in finding_codes
    assert "NITROGEN_MASS_BALANCE_VIOLATION" in finding_codes