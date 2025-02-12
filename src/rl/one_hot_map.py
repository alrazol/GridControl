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
        network_observation: Any,  # TODO: find way to type here
        types: dict[SupportedNetworkElementTypes, np.ndarray],
        buses: dict[str, np.ndarray],
        voltage_levels: dict[str, np.ndarray],
        statuses: dict[ElementStatus, np.ndarray],
        constraint_sides: dict[BranchSide, np.ndarray],
        constraint_types: dict[OperationalConstraintType, np.ndarray],
        affected_elements: dict[str, np.ndarray],
    ):
        self.network_observation = network_observation
        self.types = types
        self.buses = buses
        self.voltage_levels = voltage_levels
        self.statuses = statuses
        self.constraint_sides = constraint_sides
        self.constraint_types = constraint_types
        self.affected_elements = affected_elements

    @classmethod
    def from_network_observation(cls, network_observation: Any) -> Self:
        """
        Create and fit a OneHotMap instance from a list of observations.
        """
        types = cls._build_mapping(
            sorted(set([i.type for i in network_observation.observations]))
        )
        buses = cls._build_mapping(
            sorted(
                set(
                    [
                        bus_id
                        for v in network_observation.observations
                        for bus_id in v.bus_ids
                    ]
                )
            )
        )
        voltage_levels = cls._build_mapping(
            sorted(
                set(
                    [
                        voltage_id
                        for v in network_observation.observations
                        for voltage_id in v.voltage_level_ids
                    ]
                )
            )
        )
        statuses = cls._build_mapping(sorted([ElementStatus.ON, ElementStatus.OFF]))
        constraint_sides = cls._build_mapping(
            sorted(
                set(
                    [
                        constraint.get("side")
                        for s in network_observation.observations
                        if hasattr(s, "operational_constraints")
                        for constraint in s.operational_constraints
                    ]
                )
            )
        )
        constraint_types = cls._build_mapping(
            sorted(
                set(
                    [
                        constraint.get("type")
                        for s in network_observation.observations
                        if hasattr(s, "operational_constraints")
                        for constraint in s.operational_constraints
                    ]
                )
            )
        )
        affected_elements = cls._build_mapping(
            sorted(
                set(
                    [
                        constraint.get("affected_element")
                        for s in network_observation.observations
                        if hasattr(s, "operational_constraints")
                        for constraint in s.operational_constraints
                    ]
                )
            )
        )
        return cls(
            network_observation=network_observation,
            types=types,
            buses=buses,
            voltage_levels=voltage_levels,
            statuses=statuses,
            constraint_sides=constraint_sides,
            constraint_types=constraint_types,
            affected_elements=affected_elements,
        )

    @staticmethod
    def _build_mapping(unique_values: list[Any]) -> dict[Any, np.ndarray]:
        """
        Build a one-hot mapping based on provided unique values.
        """
        return {
            value: np.eye(len(unique_values))[i]
            for i, value in enumerate(unique_values)
        }
