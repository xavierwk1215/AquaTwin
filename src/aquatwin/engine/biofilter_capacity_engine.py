"""Biofilter capacity engine for the StepContext pipeline."""

from aquatwin.domain.filter_unit import FilterUnit
from aquatwin.domain.metrics import DailyMetric
from aquatwin.engine.step_context import StepContext


class BiofilterCapacityEngine:
    """Calculate biological filter processing capacity."""

    @staticmethod
    def calculate_tan_capacity_mg_n_day(
        filter_unit: FilterUnit,
    ) -> float:
        """Return daily TAN processing capacity."""

        total_capacity = 0.0

        for media in filter_unit.media:
            total_capacity += (
                media.media_volume_l
                * media.tan_capacity_mg_n_l_media_day
                * media.usable_fraction
            )

        total_capacity *= filter_unit.maturity_fraction
        total_capacity *= (1.0 - filter_unit.fouling_fraction)

        return total_capacity

    @staticmethod
    def calculate_nitrite_capacity_mg_n_day(
        filter_unit: FilterUnit,
    ) -> float:
        """Return daily nitrite processing capacity."""

        total_capacity = 0.0

        for media in filter_unit.media:
            total_capacity += (
                media.media_volume_l
                * media.nitrite_capacity_mg_n_l_media_day
                * media.usable_fraction
            )

        total_capacity *= filter_unit.maturity_fraction
        total_capacity *= (1.0 - filter_unit.fouling_fraction)

        return total_capacity

    @staticmethod
    def apply(
        context: StepContext,
        filter_unit: FilterUnit,
    ) -> None:
        """Record current biofilter capacities."""

        tan_capacity = (
            BiofilterCapacityEngine.calculate_tan_capacity_mg_n_day(
                filter_unit
            )
        )

        nitrite_capacity = (
            BiofilterCapacityEngine.calculate_nitrite_capacity_mg_n_day(
                filter_unit
            )
        )

        context.metrics.extend(
            [
                DailyMetric(
                    name="biofilter_tan_capacity_mg_day",
                    value=tan_capacity,
                    unit="mg-N/day",
                ),
                DailyMetric(
                    name="biofilter_nitrite_capacity_mg_day",
                    value=nitrite_capacity,
                    unit="mg-N/day",
                ),
            ]
        )