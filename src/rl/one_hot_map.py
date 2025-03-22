import numpy as np
from typing import Self, Any
from src.core.constants import SupportedNetworkElementTypes
from src.core.constants import ElementStatus
from src.core.domain.enums import BranchSide, OperationalConstraintType


class OneHotMap:
    """
    This class is used to build one hot encodings. Those encodings
    are then used by the agent when building a NetworkObservation.
    Each attribute the one hot encoding mappings for a type of info.
    Each attribute is a dict btw each possible value of that type and
    the one hot encoding for it.

    To build the map, you need to rely on a NetworkObservation, usually
    the initial obs when you assume the obs space is constant throughout
    timesteps.
    """

    def __init__(
        self,
        types: dict[SupportedNetworkElementTypes, np.ndarray],
        buses: dict[str, np.ndarray],
        voltage_levels: dict[str, np.ndarray],
        statuses: dict[ElementStatus, np.ndarray],
        constraint_sides: dict[BranchSide, np.ndarray],
        constraint_types: dict[OperationalConstraintType, np.ndarray],
        affected_elements: dict[str, np.ndarray],
    ):
        self.types = types
        self.buses = buses
        self.voltage_levels = voltage_levels
        self.statuses = statuses
        self.constraint_sides = constraint_sides
        self.constraint_types = constraint_types
        self.affected_elements = affected_elements
