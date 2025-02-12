import numpy as np
import pandas as pd
from typing import Self, Any
from datetime import datetime

from numpy import ndarray
from src.core.constants import SupportedNetworkElementTypes, ElementStatus
from src.core.domain.models.element import NetworkElement
from src.rl.observation.base import BaseElementObservation
from src.rl.one_hot_map import OneHotMap


class LineObservation(BaseElementObservation):
    def __init__(
        self,
        id: str,
        timestamp: datetime,
        type: SupportedNetworkElementTypes,
        status: ElementStatus,
        bus1_id: str,
        bus2_id: str,
        voltage_level1_id: str,
        voltage_level2_id: str,
        b1: float,
        b2: float,
        g1: float,
        g2: float,
        r: float,
        x: float,
        p1: float,
        p2: float,
        operational_constraints: list[dict[str, Any]],  # TODO: define better
    ) -> None:
        super().__init__(
            id=id,
            timestamp=timestamp,
            type=type,
            status=status,
        )
        self.bus1_id = bus1_id
        self.bus2_id = bus2_id
        self.voltage_level1_id = voltage_level1_id
        self.voltage_level2_id = voltage_level2_id
        self.b1 = b1
        self.b2 = b2
        self.g1 = g1
        self.g2 = g2
        self.r = r
        self.x = x
        self.p1 = p1
        self.p2 = p2
        self.operational_constraints = operational_constraints

    @classmethod
    def from_element(cls, element: NetworkElement) -> Self:
        if element.type != SupportedNetworkElementTypes.LINE:
            raise ValueError("Element is not a 'LINE'")
        # if element.element_metadata.state != State.SOLVED:
        #    raise ValueError(
        #        "Element of type 'LINE' has to be solved to build observation."
        #    )
        return cls(
            id=element.id,
            timestamp=element.timestamp,
            type=element.type,
            status=element.element_metadata.static.status,
            bus1_id=element.element_metadata.static.bus1_id,
            bus2_id=element.element_metadata.static.bus2_id,
            voltage_level1_id=element.element_metadata.static.voltage_level1_id,
            voltage_level2_id=element.element_metadata.static.voltage_level2_id,
            b1=element.element_metadata.static.b1,
            b2=element.element_metadata.static.b2,
            g1=element.element_metadata.static.g1,
            g2=element.element_metadata.static.g2,
            r=element.element_metadata.static.r,
            x=element.element_metadata.static.x,
            p1=element.element_metadata.solved.p1
            if element.element_metadata.solved is not None  # TODO: update tests
            else 0,
            p2=element.element_metadata.solved.p2
            if element.element_metadata.solved is not None
            else 0,
            operational_constraints=[
                {
                    "affected_element": constraint.element_id,
                    "side": constraint.side,
                    "type": constraint.type,
                    "value": constraint.value,
                }
                for constraint in element.operational_constraints
            ],
        )

    @property
    def is_switchable(self) -> bool:
        return True

    @property
    def bus_ids(self) -> list[str]:
        return [self.bus1_id, self.bus2_id]

    @property
    def voltage_level_ids(self) -> list[str]:
        return [self.voltage_level1_id, self.voltage_level2_id]

    def to_array(self, one_hot_map: OneHotMap) -> ndarray:
        """
        This method turns a 'LineObservation' to an array. It relies
        heavily on the one_hot_map, which allows to map a categorical attr to
        its relevant one-hot encoding.

        Params:
        - one_hot_map (dict[str, dict[str, np.ndarray]]): A dict containing with
        the type of mapping as a key and the category to array mapping as values.

        Returns:
            np.ndarray: The observation as an array.
        """
        base_array = np.concatenate(
            [
                one_hot_map.types.get(self.type),
                one_hot_map.statuses.get(self.status),
                one_hot_map.buses.get(self.bus1_id),
                one_hot_map.buses.get(self.bus2_id),
                one_hot_map.voltage_levels.get(self.voltage_level1_id),
                one_hot_map.voltage_levels.get(self.voltage_level2_id),
                [
                    self.p1,
                    self.p2,
                ],
            ]
        )

        if len(self.operational_constraints) > 0:
            array = np.concatenate(
                [
                    base_array,
                    np.concatenate(
                        [
                            one_hot_map.constraint_sides.get(i.get("side"))
                            for i in self.operational_constraints
                        ]
                    ),
                    np.concatenate(
                        [
                            one_hot_map.constraint_types.get(i.get("type"))
                            for i in self.operational_constraints
                        ]
                    ),
                    np.concatenate(
                        [
                            one_hot_map.affected_elements.get(i.get("affected_element"))
                            for i in self.operational_constraints
                        ]
                    ),
                    [
                        constraint.get("value")
                        for constraint in self.operational_constraints
                    ],
                ],
            )
        else:
            array = base_array
        return array

    def to_dataframe(self) -> pd.DataFrame:
        """
        This method converts a 'LineObservation' to a pd.DataFrame.
        """
        data = {
            "id": [self.id],
            "timestamp": [self.timestamp],
            "type": [self.type],
            "status": [self.status],
            "bus1_id": [self.bus1_id],
            "bus2_id": [self.bus2_id],
            "voltage_level1_id": [self.voltage_level1_id],
            "voltage_level2_id": [self.voltage_level2_id],
            "p1": [self.p1],
            "p2": [self.p2],
        }
        for i, constraint in enumerate(self.operational_constraints):
            data[f"constraint_{i}_type"] = [constraint.get("type")]
            data[f"constraint_{i}_value"] = [constraint.get("value")]
        return pd.DataFrame(data)
