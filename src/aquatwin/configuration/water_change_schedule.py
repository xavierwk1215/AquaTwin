"""Water change schedule configuration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class WaterChangeSchedule:
    """Define when scheduled water changes should occur.

    A disabled schedule never applies a water change.

    An enabled schedule applies a water change beginning on
    ``first_water_change_day`` and repeats every ``interval_days``.

    Example:
        interval_days=7
        first_water_change_day=7

        Water changes occur on simulation days:
        7, 14, 21, 28, ...
    """

    interval_days: int | None = None
    first_water_change_day: int = 1

    def __post_init__(self) -> None:
        """Validate the schedule configuration."""
        if self.interval_days is not None:
            if isinstance(self.interval_days, bool) or not isinstance(
                self.interval_days,
                int,
            ):
                raise TypeError("interval_days must be an integer or None.")

            if self.interval_days < 1:
                raise ValueError(
                    "interval_days must be greater than or equal to 1.",
                )

        if isinstance(self.first_water_change_day, bool) or not isinstance(
            self.first_water_change_day,
            int,
        ):
            raise TypeError("first_water_change_day must be an integer.")

        if self.first_water_change_day < 1:
            raise ValueError(
                "first_water_change_day must be greater than or equal to 1.",
            )

    @property
    def is_enabled(self) -> bool:
        """Return whether scheduled water changes are enabled."""
        return self.interval_days is not None

    def should_apply(self, simulation_day: int) -> bool:
        """Return whether a water change should occur on a simulation day.

        Args:
            simulation_day:
                One-based simulation day number.

        Returns:
            True when a scheduled water change should be applied.
            False when the schedule is disabled or the day does not match.

        Raises:
            TypeError:
                If simulation_day is not an integer.

            ValueError:
                If simulation_day is less than one.
        """
        self._validate_simulation_day(simulation_day)

        if not self.is_enabled:
            return False

        if simulation_day < self.first_water_change_day:
            return False

        days_since_first_change = (
            simulation_day - self.first_water_change_day
        )

        return days_since_first_change % self.interval_days == 0

    @staticmethod
    def _validate_simulation_day(simulation_day: int) -> None:
        """Validate a one-based simulation day number."""
        if isinstance(simulation_day, bool) or not isinstance(
            simulation_day,
            int,
        ):
            raise TypeError("simulation_day must be an integer.")

        if simulation_day < 1:
            raise ValueError(
                "simulation_day must be greater than or equal to 1.",
            )