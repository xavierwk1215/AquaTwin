"""Tests for StockingEvaluationEngine."""

import pytest

from aquatwin.domain.species import Species
from aquatwin.domain.stocking import Stocking
from aquatwin.domain.stocking_evaluation_engine import (
    StockingEvaluationEngine,
)
from aquatwin.domain.stocking_status import StockingStatus


def _create_stocking(
    adult_weight_g: float,
    count: int,
    bioload_factor: float = 1.0,
) -> Stocking:
    """Create stocking data for testing."""
    species = Species(
        species_id="test-species",
        common_name="Test Fish",
        scientific_name="Testus piscis",
        adult_length_cm=5.0,
        adult_weight_g=adult_weight_g,
        bioload_factor=bioload_factor,
    )

    return Stocking(
        species=species,
        count=count,
    )


def test_calculates_combined_stocking_values() -> None:
    """Calculate total weight and adjusted bioload."""
    engine = StockingEvaluationEngine()

    result = engine.evaluate(
        stockings=(
            _create_stocking(
                adult_weight_g=2.0,
                count=10,
                bioload_factor=1.2,
            ),
            _create_stocking(
                adult_weight_g=5.0,
                count=2,
                bioload_factor=0.8,
            ),
        ),
        estimated_capacity_g=100.0,
    )

    assert result.total_adult_weight_g == pytest.approx(30.0)
    assert result.adjusted_bioload_g == pytest.approx(32.0)
    assert result.capacity_usage_ratio == pytest.approx(0.32)


def test_returns_light_status_at_fifty_percent_capacity() -> None:
    """Return light status at the upper light boundary."""
    engine = StockingEvaluationEngine()

    result = engine.evaluate(
        stockings=(
            _create_stocking(
                adult_weight_g=5.0,
                count=10,
            ),
        ),
        estimated_capacity_g=100.0,
    )

    assert result.status is StockingStatus.LIGHT


def test_returns_balanced_status_above_fifty_percent() -> None:
    """Return balanced status above the light boundary."""
    engine = StockingEvaluationEngine()

    result = engine.evaluate(
        stockings=(
            _create_stocking(
                adult_weight_g=6.0,
                count=10,
            ),
        ),
        estimated_capacity_g=100.0,
    )

    assert result.status is StockingStatus.BALANCED


def test_returns_high_status_above_eighty_percent() -> None:
    """Return high status above the balanced boundary."""
    engine = StockingEvaluationEngine()

    result = engine.evaluate(
        stockings=(
            _create_stocking(
                adult_weight_g=9.0,
                count=10,
            ),
        ),
        estimated_capacity_g=100.0,
    )

    assert result.status is StockingStatus.HIGH


def test_returns_overstocked_status_above_capacity() -> None:
    """Return overstocked status above estimated capacity."""
    engine = StockingEvaluationEngine()

    result = engine.evaluate(
        stockings=(
            _create_stocking(
                adult_weight_g=11.0,
                count=10,
            ),
        ),
        estimated_capacity_g=100.0,
    )

    assert result.status is StockingStatus.OVERSTOCKED
    assert result.capacity_usage_ratio == pytest.approx(1.1)
    assert "110.0%" in result.reason