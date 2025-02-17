import numpy as np
from src.rl.observation.network import NetworkSnapshotObservation
from src.rl.one_hot_map import OneHotMap
from typing import Any
from src.core.constants import ElementStatus
from src.rl.one_hot_map_builder import OneHotMapBuilder


class DefaultOneHotMapBuilder(OneHotMapBuilder):
    """
    Class to build a OneHotMap instance from a list of observations.
    """

    @staticmethod
    def from_network_snapshot_observation(
        network_snapshot_observation: NetworkSnapshotObservation,
    ) -> OneHotMap:
        """
        Create and fit a OneHotMap instance from a list of observations.
        """

        def _build_mapping(unique_values: list[Any]) -> dict[Any, np.ndarray]:
            """
            Build a one-hot mapping based on provided unique values.
            """
            return {
                value: np.eye(len(unique_values))[i]
                for i, value in enumerate(unique_values)
            }

        types = _build_mapping(
            sorted(set([i.type for i in network_snapshot_observation.observations]))
        )
        buses = _build_mapping(
            sorted(
                set(
                    [
                        bus_id
                        for v in network_snapshot_observation.observations
                        for bus_id in v.bus_ids
                    ]
                )
            )
        )
        voltage_levels = _build_mapping(
            sorted(
                set(
                    [
                        voltage_id
                        for v in network_snapshot_observation.observations
                        for voltage_id in v.voltage_level_ids
                    ]
                )
            )
        )
        statuses = _build_mapping(sorted([ElementStatus.ON, ElementStatus.OFF]))
        constraint_sides = _build_mapping(
            sorted(
                set(
                    [
                        constraint.get("side")
                        for s in network_snapshot_observation.observations
                        if hasattr(s, "operational_constraints")
                        for constraint in s.operational_constraints
                    ]
                )
            )
        )
        constraint_types = _build_mapping(
            sorted(
                set(
                    [
                        constraint.get("type")
                        for s in network_snapshot_observation.observations
                        if hasattr(s, "operational_constraints")
                        for constraint in s.operational_constraints
                    ]
                )
            )
        )
        affected_elements = _build_mapping(
            sorted(
                set(
                    [
                        constraint.get("affected_element")
                        for s in network_snapshot_observation.observations
                        if hasattr(s, "operational_constraints")
                        for constraint in s.operational_constraints
                    ]
                )
            )
        )

        return OneHotMap(
            #network_snapshot_observation=network_snapshot_observation,
            types=types,
            buses=buses,
            voltage_levels=voltage_levels,
            statuses=statuses,
            constraint_sides=constraint_sides,
            constraint_types=constraint_types,
            affected_elements=affected_elements,
        )
