"""Tests for Stocking."""

from dataclasses import FrozenInstanceError

import pytest

from aquatwin.domain.species import Species
from aquatwin.domain.stocking import Stocking


def _create_species() -> Species:
    """Create a species for testing."""
    return Species(
        species_id="guppy",
        common_name="Guppy",
        scientific_name="Poecilia reticulata",
        adult_length_cm=4.0,
        adult_weight_g=2.0,
        bioload_factor=1.2,
    )


def test_calculates_total_adult_weight() -> None:
    """Calculate total adult weight from species weight and count."""
    stocking = Stocking(
        species=_create_species(),
        count=10,
    )

    assert stocking.total_adult_weight_g == pytest.approx(20.0)


def test_calculates_adjusted_bioload() -> None:
    """Calculate bioload adjusted by the species factor."""
    stocking = Stocking(
        species=_create_species(),
        count=10,
    )

    assert stocking.adjusted_bioload_g == pytest.approx(24.0)


def test_stocking_is_immutable() -> None:
    """Prevent stocking data from changing after creation."""
    stocking = Stocking(
        species=_create_species(),
        count=10,
    )

    with pytest.raises(FrozenInstanceError):
        stocking.count = 20  # type: ignore[misc]