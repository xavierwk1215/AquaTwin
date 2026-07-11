"""Tests for SimulationProfileRepository."""

import pytest

from aquatwin.domain.simulation_parameter import SimulationParameter
from aquatwin.domain.simulation_profile import SimulationProfile
from aquatwin.domain.simulation_profile_repository import (
    SimulationProfileRepository,
)
from aquatwin.domain.value_origin import ValueOrigin


def _parameter(
    name: str,
    value: float,
) -> SimulationParameter:
    """Create a simulation parameter for testing."""
    return SimulationParameter(
        name=name,
        value=value,
        unit="unit",
        origin=ValueOrigin.OBSERVED,
    )


def _profile(
    profile_id: str,
    name: str,
) -> SimulationProfile:
    """Create a simulation profile for testing."""
    return SimulationProfile(
        profile_id=profile_id,
        name=name,
        adult_weight=_parameter("adult_weight", 2.0),
        daily_feed_ratio=_parameter("daily_feed_ratio", 0.02),
        digestibility=_parameter("digestibility", 0.85),
        nitrogen_fraction=_parameter("nitrogen_fraction", 0.16),
        oxygen_consumption=_parameter("oxygen_consumption", 1.0),
        waste_factor=_parameter("waste_factor", 1.0),
    )


def test_get_returns_profile_by_identifier() -> None:
    """Return the requested profile."""
    profile = _profile(
        profile_id="small_tetra",
        name="Small Tetra",
    )

    repository = SimulationProfileRepository(
        profiles=(profile,),
    )

    assert repository.get("small_tetra") is profile


def test_exists_returns_true_for_stored_profile() -> None:
    """Confirm that a stored profile exists."""
    repository = SimulationProfileRepository(
        profiles=(
            _profile(
                profile_id="small_tetra",
                name="Small Tetra",
            ),
        ),
    )

    assert repository.exists("small_tetra") is True


def test_exists_returns_false_for_unknown_profile() -> None:
    """Return False for an unknown profile."""
    repository = SimulationProfileRepository()

    assert repository.exists("unknown") is False


def test_all_returns_every_profile() -> None:
    """Return every stored profile."""
    first = _profile(
        profile_id="small_tetra",
        name="Small Tetra",
    )
    second = _profile(
        profile_id="livebearer",
        name="Livebearer",
    )

    repository = SimulationProfileRepository(
        profiles=(
            first,
            second,
        ),
    )

    assert repository.all() == (
        first,
        second,
    )


def test_get_raises_key_error_for_unknown_profile() -> None:
    """Raise KeyError for an unknown profile."""
    repository = SimulationProfileRepository()

    with pytest.raises(KeyError):
        repository.get("unknown")