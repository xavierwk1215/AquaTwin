"""Repository for species simulation mappings."""

from aquatwin.domain.species_simulation_mapping import (
    SpeciesSimulationMapping,
)


class SpeciesSimulationMappingRepository:
    """Store and retrieve species-to-profile mappings."""

    def __init__(
        self,
        mappings: tuple[SpeciesSimulationMapping, ...] = (),
    ) -> None:
        """Initialize the repository with species mappings."""
        self._mappings = mappings
        self._mappings_by_species_id = {
            mapping.species_id: mapping
            for mapping in mappings
        }

    def get(
        self,
        species_id: str,
    ) -> SpeciesSimulationMapping:
        """Return the simulation mapping for a species."""
        try:
            return self._mappings_by_species_id[species_id]
        except KeyError as error:
            raise KeyError(
                f"Unknown species simulation mapping: {species_id}",
            ) from error

    def exists(
        self,
        species_id: str,
    ) -> bool:
        """Return whether a mapping exists for a species."""
        return species_id in self._mappings_by_species_id

    def all(
        self,
    ) -> tuple[SpeciesSimulationMapping, ...]:
        """Return every mapping in insertion order."""
        return self._mappings