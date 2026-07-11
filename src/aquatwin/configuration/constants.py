from enum import Enum


class NitrogenPool(Enum):
    """Official tracked nitrogen pools."""

    ORGANIC = "Organic-N"
    TAN = "TAN-N"
    NITRITE = "Nitrite-N"
    NITRATE = "Nitrate-N"


# Unit conversion
MG_PER_G = 1000.0