"""Species domain model."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Species:
    """Represent the biological properties of an aquarium species."""

    species_id: str
    common_name: str
    scientific_name: str
    adult_length_cm: float
    adult_weight_g: float
    bioload_factor: float