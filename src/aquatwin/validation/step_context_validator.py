"""Combined validation for one completed StepContext."""

from aquatwin.engine.step_context import StepContext
from aquatwin.validation.biofilter_capacity_validator import (
    BiofilterCapacityValidator,
)
from aquatwin.validation.feed_nitrogen_conservation_validator import (
    FeedNitrogenConservationValidator,
)
from aquatwin.validation.nitrogen_mass_balance_validator import (
    NitrogenMassBalanceValidator,
)
from aquatwin.validation.simulation_state_validator import (
    SimulationStateValidator,
)
from aquatwin.validation.validation_result import ValidationResult


class StepContextValidator:
    """Run all completed daily-step validation rules."""

    @classmethod
    def validate(
        cls,
        context: StepContext,
    ) -> ValidationResult:
        """Return one combined validation result for the completed step."""
        new_state = context.working_state.to_simulation_state()

        results = (
            SimulationStateValidator().validate(new_state),
            BiofilterCapacityValidator.validate(context),
            FeedNitrogenConservationValidator.validate(context),
            NitrogenMassBalanceValidator.validate(context),
        )

        findings = tuple(
            finding
            for result in results
            for finding in result.findings
        )

        return ValidationResult(findings=findings)