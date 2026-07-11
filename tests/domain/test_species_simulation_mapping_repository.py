"""Tests for SpeciesSimulationMappingRepository."""

import pytest

from aquatwin.domain.species_simulation_mapping import (
    SpeciesSimulationMapping,
)
from aquatwin.domain.species_simulation_mapping_repository import (
    SpeciesSimulationMappingRepository,
)


def _mapping(
    species_id: str,
    simulation_profile_id: str,
) -> SpeciesSimulationMapping:
    """Create a species simulation mapping for testing."""
    return SpeciesSimulationMapping(
        species_id=species_id,
        simulation_profile_id=simulation_profile_id,
    )


def test_get_returns_mapping_by_species_identifier() -> None:
    """Return the requested species simulation mapping."""
    mapping = _mapping(
        species_id="neon-tetra",
        simulation_profile_id="small-tetra-v1",
    )

    repository = SpeciesSimulationMappingRepository(
        mappings=(mapping,),
    )

    assert repository.get("neon-tetra") is mapping


def test_exists_returns_true_for_stored_mapping() -> None:
    """Confirm that a mapping exists for a stored species."""
    repository = SpeciesSimulationMappingRepository(
        mappings=(
            _mapping(
                species_id="neon-tetra",
                simulation_profile_id="small-tetra-v1",
            ),
        ),
    )

    assert repository.exists("neon-tetra") is True


def test_exists_returns_false_for_unknown_species() -> None:
    """Return false when no mapping exists for a species."""
    repository = SpeciesSimulationMappingRepository()

    assert repository.exists("unknown") is False


def test_all_returns_every_mapping_in_insertion_order() -> None:
    """Return every mapping in insertion order."""
    neon_tetra = _mapping(
        species_id="neon-tetra",
        simulation_profile_id="small-tetra-v1",
    )
    guppy = _mapping(
        species_id="guppy",
        simulation_profile_id="livebearer-v1",
    )

    repository = SpeciesSimulationMappingRepository(
        mappings=(
            neon_tetra,
            guppy,
        ),
    )

    assert repository.all() == (
        neon_tetra,
        guppy,
    )


def test_get_raises_key_error_for_unknown_species() -> None:
    """Raise KeyError when no mapping exists for a species."""
    repository = SpeciesSimulationMappingRepository()

    with pytest.raises(KeyError):
        repository.get("unknown")