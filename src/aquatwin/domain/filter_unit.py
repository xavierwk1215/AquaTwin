"""Filter unit model for biological filtration capacity."""

from dataclasses import dataclass

from aquatwin.domain.filter_media import FilterMedia


@dataclass(frozen=True)
class FilterUnit:
    """Represent one aquarium filter and its biological media."""

    filter_id: str
    filter_type: str

    rated_flow_l_h: float
    actual_flow_l_h: float

    maturity_fraction: float = 1.0
    fouling_fraction: float = 0.0

    media: tuple[FilterMedia, ...] = ()