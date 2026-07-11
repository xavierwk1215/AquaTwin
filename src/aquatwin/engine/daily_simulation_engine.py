"""Daily simulation orchestration."""

from aquatwin.domain.daily_simulation_result import (
    DailySimulationResult,
)
from aquatwin.domain.filter_unit import FilterUnit
from aquatwin.engine.biofilter_capacity_engine import (
    BiofilterCapacityEngine,
)
from aquatwin.engine.feed_nitrogen_distribution_engine import (
    FeedNitrogenDistributionEngine,
)
from aquatwin.engine.feeding_engine import FeedingEngine
from aquatwin.engine.fish_metabolism_engine import (
    FishMetabolismEngine,
)
from aquatwin.engine.maintenance_engine import MaintenanceEngine
from aquatwin.engine.mineralization_engine import MineralizationEngine
from aquatwin.engine.step_context import StepContext
from aquatwin.engine.step_context_nitrite_oxidation_engine import (
    StepContextNitriteOxidationEngine,
)
from aquatwin.engine.step_context_tan_oxidation_engine import (
    StepContextTANOxidationEngine,
)
from aquatwin.engine.water_change_engine import WaterChangeEngine
from aquatwin.validation.step_context_validator import (
    StepContextValidator,
)


class DailySimulationEngine:
    """Execute one complete simulation day."""

    @classmethod
    def run(
        cls,
        context: StepContext,
        filter_unit: FilterUnit,
    ) -> DailySimulationResult:
        """Execute one complete simulation step."""
        WaterChangeEngine.apply(context)
        MaintenanceEngine.apply(context)
        FeedingEngine.apply(context)
        FeedNitrogenDistributionEngine.apply(context)
        MineralizationEngine.apply(context)
        FishMetabolismEngine.apply(context)

        BiofilterCapacityEngine.apply(
            context=context,
            filter_unit=filter_unit,
        )

        StepContextTANOxidationEngine.apply(context)
        StepContextNitriteOxidationEngine.apply(context)

        validation_result = StepContextValidator.validate(context)
        new_state = context.working_state.to_simulation_state()

        return DailySimulationResult(
            simulation_day=context.daily_inputs.day,
            new_state=new_state,
            metrics=tuple(context.metrics),
            validation_result=validation_result,
        )