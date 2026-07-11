"""Simulation run identity and reproducibility metadata."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationRun:
    """Identify one reproducible multi-day simulation run."""

    run_id: str
    tank_id: str
    model_version: str
    parameter_set_version: str
    total_days: int

    def __post_init__(self) -> None:
        """Validate required simulation-run metadata."""
        self._validate_required_text("run_id", self.run_id)
        self._validate_required_text("tank_id", self.tank_id)
        self._validate_required_text(
            "model_version",
            self.model_version,
        )
        self._validate_required_text(
            "parameter_set_version",
            self.parameter_set_version,
        )

        if isinstance(self.total_days, bool) or not isinstance(
            self.total_days,
            int,
        ):
            raise TypeError("total_days must be an integer.")

        if self.total_days < 1:
            raise ValueError(
                "total_days must be greater than or equal to 1."
            )

    @staticmethod
    def _validate_required_text(
        field_name: str,
        value: str,
    ) -> None:
        """Require a non-empty text value."""
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string.")

        if not value.strip():
            raise ValueError(f"{field_name} must not be empty.")