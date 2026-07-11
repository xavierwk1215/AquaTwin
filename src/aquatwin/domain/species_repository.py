"""Repository for aquarium species."""

from aquatwin.domain.species import Species


class SpeciesRepository:
    """Store and provide aquarium species."""

    def __init__(
        self,
        species: tuple[Species, ...] = (),
    ) -> None:
        """Initialize the repository."""
        self._species = {
            item.species_id: item
            for item in species
        }

    def get(
        self,
        species_id: str,
    ) -> Species:
        """Return a species by its identifier."""
        return self._species[species_id]

    def exists(
        self,
        species_id: str,
    ) -> bool:
        """Return whether a species exists."""
        return species_id in self._species

    def all(
        self,
    ) -> tuple[Species, ...]:
        """Return every stored species."""
        return tuple(
            self._species.values()
        )