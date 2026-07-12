from dataclasses import FrozenInstanceError

import pytest

from aquatwin.domain.simulation_run import SimulationRun


def test_create_simulation_run() -> None:
    run = SimulationRun(
        run_id="run-001",
        tank_id="tank-001",
        model_version="1.0.0",
        parameter_set_version="2026.07",
        total_days=30,
    )

    assert run.run_id == "run-001"
    assert run.tank_id == "tank-001"
    assert run.model_version == "1.0.0"
    assert run.parameter_set_version == "2026.07"
    assert run.total_days == 30


def test_simulation_run_is_immutable() -> None:
    run = SimulationRun(
        run_id="run-001",
        tank_id="tank-001",
        model_version="1.0.0",
        parameter_set_version="2026.07",
        total_days=30,
    )

    with pytest.raises(FrozenInstanceError):
        run.total_days = 60  # type: ignore[misc]


@pytest.mark.parametrize(
    "field_name",
    [
        "run_id",
        "tank_id",
        "model_version",
        "parameter_set_version",
    ],
)
def test_reject_empty_required_text(field_name: str) -> None:
    values = {
        "run_id": "run-001",
        "tank_id": "tank-001",
        "model_version": "1.0.0",
        "parameter_set_version": "2026.07",
        "total_days": 30,
    }
    values[field_name] = "   "

    with pytest.raises(
        ValueError,
        match=rf"{field_name} must not be empty\.",
    ):
        SimulationRun(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "field_name, invalid_value",
    [
        ("run_id", None),
        ("tank_id", 101),
        ("model_version", 1.0),
        ("parameter_set_version", False),
    ],
)
def test_reject_non_string_required_text(
    field_name: str,
    invalid_value: object,
) -> None:
    values = {
        "run_id": "run-001",
        "tank_id": "tank-001",
        "model_version": "1.0.0",
        "parameter_set_version": "2026.07",
        "total_days": 30,
    }
    values[field_name] = invalid_value

    with pytest.raises(
        TypeError,
        match=rf"{field_name} must be a string\.",
    ):
        SimulationRun(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "invalid_total_days",
    [True, 1.5, "30", None],
)
def test_reject_non_integer_total_days(
    invalid_total_days: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=r"total_days must be an integer\.",
    ):
        SimulationRun(
            run_id="run-001",
            tank_id="tank-001",
            model_version="1.0.0",
            parameter_set_version="2026.07",
            total_days=invalid_total_days,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "invalid_total_days",
    [0, -1, -30],
)
def test_reject_total_days_below_one(
    invalid_total_days: int,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            r"total_days must be greater than or equal to 1\."
        ),
    ):
        SimulationRun(
            run_id="run-001",
            tank_id="tank-001",
            model_version="1.0.0",
            parameter_set_version="2026.07",
            total_days=invalid_total_days,
        )