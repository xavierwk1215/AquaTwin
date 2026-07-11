"""Stocking status levels for aquarium evaluation."""

from enum import Enum


class StockingStatus(Enum):
    """Represent the evaluated aquarium stocking level."""

    LIGHT = "light"
    BALANCED = "balanced"
    HIGH = "high"
    OVERSTOCKED = "overstocked"