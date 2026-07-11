"""Fish cohort domain model."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FishCohort:
    """Represent one species population included in a simulation run."""

    species_id: str
    count: int