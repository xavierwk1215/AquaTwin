"""Tests for SpeciesRepository."""

import pytest

from aquatwin.domain.species import Species
from aquatwin.domain.species_repository import SpeciesRepository


def _create_species(
    species_id: str,
    common_name: str,
) -> Species:
    """Create a species for repository testing."""
    return Species(
        species_id=species_id,
        common_name=common_name,
        scientific_name="Testus aquaticus",
        adult_length_cm=5.0,
        adult_weight_g=2.0,
        bioload_factor=1.0,
    )


def test_get_returns_species_by_identifier() -> None:
    """Return the requested species."""
    guppy = _create_species(
        species_id="guppy",
        common_name="Guppy",
    )

    repository = SpeciesRepository(
        species=(guppy,),
    )

    assert repository.get("guppy") is guppy


def test_exists_returns_true_for_stored_species() -> None:
    """Confirm that a stored species exists."""
    repository = SpeciesRepository(
        species=(
            _create_species(
                species_id="guppy",
                common_name="Guppy",
            ),
        ),
    )

    assert repository.exists("guppy") is True


def test_exists_returns_false_for_unknown_species() -> None:
    """Return false for an unknown species."""
    repository = SpeciesRepository()

    assert repository.exists("unknown") is False


def test_all_returns_every_stored_species() -> None:
    """Return every species in insertion order."""
    guppy = _create_species(
        species_id="guppy",
        common_name="Guppy",
    )
    betta = _create_species(
        species_id="betta",
        common_name="Betta",
    )

    repository = SpeciesRepository(
        species=(
            guppy,
            betta,
        ),
    )

    assert repository.all() == (
        guppy,
        betta,
    )


def test_get_raises_key_error_for_unknown_species() -> None:
    """Raise an error when the species identifier is unknown."""
    repository = SpeciesRepository()

    with pytest.raises(KeyError):
        repository.get("unknown")