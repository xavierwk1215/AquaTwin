"""Tests for FishCohort."""

import pytest

from aquatwin.domain.fish_cohort import FishCohort


def test_create_valid_fish_cohort() -> None:
    """Create a valid fish cohort."""
    cohort = FishCohort(
        species_id="neon_tetra",
        count=20,
    )

    assert cohort.species_id == "neon_tetra"
    assert cohort.count == 20


@pytest.mark.parametrize(
    "count",
    [
        0,
        1,
        50,
        500,
    ],
)
def test_fish_cohort_accepts_non_negative_count(
    count: int,
) -> None:
    """Fish cohort stores non-negative population counts."""
    cohort = FishCohort(
        species_id="test_species",
        count=count,
    )

    assert cohort.count == count