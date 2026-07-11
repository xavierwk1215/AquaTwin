"""Filter media model for biological filtration capacity."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FilterMedia:
    """Represent one biological filter media component."""

    media_type: str
    media_volume_l: float

    tan_capacity_mg_n_l_media_day: float
    nitrite_capacity_mg_n_l_media_day: float

    usable_fraction: float = 1.0