"""Stocking domain model."""

from dataclasses import dataclass

from aquatwin.domain.species import Species


@dataclass(frozen=True)
class Stocking:
    """Represent one species population in an aquarium."""

    species: Species
    count: int

    @property
    def total_adult_weight_g(self) -> float:
        """Return the total estimated adult weight of the population."""
        return self.species.adult_weight_g * self.count

    @property
    def adjusted_bioload_g(self) -> float:
        """Return the population weight adjusted by its bioload factor."""
        return self.total_adult_weight_g * self.species.bioload_factor