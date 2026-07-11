"""Daily simulation inputs."""

from dataclasses import dataclass

from aquatwin.domain.fish_cohort import FishCohort


@dataclass(frozen=True)
class DailyInputs:
    """Represent all external inputs for one simulation day."""

    day: int
    water_temperature_c: float

    tank_volume_l: float = 0.0
    source_tan_mg_n_l: float = 0.0
    source_nitrite_mg_n_l: float = 0.0
    source_nitrate_mg_n_l: float = 0.0

    fish_cohorts: tuple[FishCohort, ...] = ()