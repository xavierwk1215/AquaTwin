"""Feed nitrogen calculator for simulation fish cohorts."""

from collections.abc import Iterable

from aquatwin.domain.fish_cohort import FishCohort
from aquatwin.domain.frozen_parameter_set import FrozenParameterSet


class FeedNitrogenEngine:
    """Calculate daily feed mass and feed nitrogen from frozen parameters."""

    @staticmethod
    def calculate_total_feed_mass_g(
        cohorts: Iterable[FishCohort],
        frozen_parameter_set: FrozenParameterSet,
    ) -> float:
        """Return the total daily feed mass in grams."""
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

        total_feed_mass_g = 0.0

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
            daily_feed_ratio = profile.daily_feed_ratio.value

            if adult_weight_g < 0.0:
                raise ValueError(
                    "Adult weight must be non-negative."
                )

            if daily_feed_ratio < 0.0:
                raise ValueError(
                    "Daily feed ratio must be non-negative."
                )

            cohort_biomass_g = adult_weight_g * cohort.count
            total_feed_mass_g += (
                cohort_biomass_g * daily_feed_ratio
            )

        return total_feed_mass_g

    @staticmethod
    def calculate_total_feed_nitrogen_mg(
        cohorts: Iterable[FishCohort],
        frozen_parameter_set: FrozenParameterSet,
    ) -> float:
        """Return the total nitrogen supplied by daily feed in mg-N."""
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

        total_feed_nitrogen_mg = 0.0

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
            daily_feed_ratio = profile.daily_feed_ratio.value
            nitrogen_fraction = profile.nitrogen_fraction.value

            if adult_weight_g < 0.0:
                raise ValueError(
                    "Adult weight must be non-negative."
                )

            if daily_feed_ratio < 0.0:
                raise ValueError(
                    "Daily feed ratio must be non-negative."
                )

            if not 0.0 <= nitrogen_fraction <= 1.0:
                raise ValueError(
                    "Nitrogen fraction must be between "
                    "0.0 and 1.0."
                )

            cohort_biomass_g = adult_weight_g * cohort.count
            cohort_feed_mass_g = (
                cohort_biomass_g * daily_feed_ratio
            )
            cohort_feed_nitrogen_mg = (
                cohort_feed_mass_g
                * nitrogen_fraction
                * 1000.0
            )

            total_feed_nitrogen_mg += cohort_feed_nitrogen_mg

        return total_feed_nitrogen_mg