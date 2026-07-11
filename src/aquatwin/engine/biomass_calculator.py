"""Biomass calculator for simulation fish cohorts."""

from collections.abc import Iterable

from aquatwin.domain.fish_cohort import FishCohort
from aquatwin.domain.frozen_parameter_set import FrozenParameterSet


class BiomassCalculator:
    """Calculate total fish biomass from frozen simulation parameters."""

    @staticmethod
    def calculate_total_biomass_g(
        cohorts: Iterable[FishCohort],
        frozen_parameter_set: FrozenParameterSet,
    ) -> float:
        """Return the total estimated adult biomass in grams."""
        profiles_by_id = {
            profile.profile_id: profile
            for profile in frozen_parameter_set.simulation_profiles
        }
        profile_ids_by_species_id = {
            mapping.species_id: mapping.simulation_profile_id
            for mapping in (
                frozen_parameter_set.species_simulation_mappings
            )
        }

        total_biomass_g = 0.0

        for cohort in cohorts:
            if cohort.count < 0:
                raise ValueError(
                    "Fish cohort count must be non-negative."
                )

            profile_id = profile_ids_by_species_id.get(
                cohort.species_id
            )

            if profile_id is None:
                raise ValueError(
                    "No simulation profile mapping found for "
                    f"species_id: {cohort.species_id}"
                )

            profile = profiles_by_id.get(profile_id)

            if profile is None:
                raise ValueError(
                    "Simulation profile not found for "
                    f"profile_id: {profile_id}"
                )

            adult_weight_g = profile.adult_weight.value

            if adult_weight_g < 0.0:
                raise ValueError(
                    "Adult weight must be non-negative."
                )

            total_biomass_g += adult_weight_g * cohort.count

        return total_biomass_g