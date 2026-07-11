"""Origin types for quantitative AquaTwin data values."""

from enum import StrEnum


class ValueOrigin(StrEnum):
    """Describe how a quantitative simulation value was obtained."""

    OBSERVED = "observed"
    DERIVED = "derived"
    ASSUMED = "assumed"
    USER_INPUT = "user_input"