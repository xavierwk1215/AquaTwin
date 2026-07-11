"""Fish metabolism engine for the StepContext pipeline."""

from aquatwin.domain.metrics import DailyMetric
from aquatwin.engine.biomass_calculator import BiomassCalculator
from aquatwin.engine.step_context import StepContext


class FishMetabolismEngine:
    """Apply basal fish metabolism independent of feeding."""

    @staticmethod
    def apply(context: StepContext) -> None:
        """Generate metabolic TAN and oxygen consumption."""
        fish_cohorts = context.daily_inputs.fish_cohorts

        if not fish_cohorts:
            return

        frozen = context.frozen_parameter_set

        total_biomass_g = BiomassCalculator.calculate_total_biomass_g(
            cohorts=fish_cohorts,
            frozen_parameter_set=frozen,
        )

        profiles = {
            profile.profile_id: profile
            for profile in frozen.simulation_profiles
        }

        mappings = {
            mapping.species_id: mapping.simulation_profile_id
            for mapping in frozen.species_simulation_mappings
        }

        total_metabolic_tan_mg = 0.0
        total_oxygen_consumption_mg = 0.0

        for cohort in fish_cohorts:
            profile = profiles[mappings[cohort.species_id]]

            biomass_g = (
                profile.adult_weight.value
                * cohort.count
            )

            oxygen_rate = profile.oxygen_consumption.value

            tan_rate = (
                profile.metabolic_tan_excretion.value
                if profile.metabolic_tan_excretion is not None
                else 0.0
            )

            total_oxygen_consumption_mg += (
                biomass_g * oxygen_rate
            )

            total_metabolic_tan_mg += (
                biomass_g * tan_rate
            )

        context.working_state.tan_mass_mg += (
            total_metabolic_tan_mg
        )

        context.metrics.extend(
            [
                DailyMetric(
                    name="fish_biomass_g",
                    value=total_biomass_g,
                    unit="g",
                ),
                DailyMetric(
                    name="fish_oxygen_consumption_mg",
                    value=total_oxygen_consumption_mg,
                    unit="mg-O2",
                ),
                DailyMetric(
                    name="metabolic_tan_input_mg",
                    value=total_metabolic_tan_mg,
                    unit="mg-N",
                ),
            ]
        )