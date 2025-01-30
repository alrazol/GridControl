from enum import Enum


class State(str, Enum):  # NOTE: Could be tight to the NetworkElement def.
    """Gives the 'state' of a network element according to its metadata."""

    STATIC = "STATIC"
    DYNAMIC = "DYNAMIC"
    SOLVED = "SOLVED"


class LoadFlowType(str, Enum):
    AC = "AC"
    DC = "DC"


class OperationalConstraintType(str, Enum):
    APPARENT_POWER = "APPARENT_POWER"
    ACTIVE_POWER = "ACTIVE_POWER"
    CURRENT = "CURRENT"


class BranchSide(str, Enum):
    ONE = "ONE"
    TWO = "TWO"
    THREE = "THREE"
