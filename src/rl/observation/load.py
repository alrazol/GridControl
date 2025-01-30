import numpy as np
import pandas as pd
import math
from datetime import datetime
from src.core.constants import State, SupportedNetworkElementTypes
from src.core.domain.models.element import NetworkElement
from typing import Self
from src.core.constants import ElementStatus
from src.rl.observation.base import BaseElementObservation
from src.rl.observation.one_hot_map import OneHotMap


class LoadObservation(BaseElementObservation):
    def __init__(
        self,
        id: str,
        timestamp: datetime,
        type: SupportedNetworkElementTypes,
        status: ElementStatus,
        bus_id: str,
        voltage_level_id: str,
        Pd: float,
        active_power: float,
        reactive_power: float,
    ) -> None:
        super().__init__(
            id=id,
            timestamp=timestamp,
            type=type,
            status=status,
        )
        self.bus_id = bus_id
        self.voltage_level_id = voltage_level_id
        self.Pd = Pd
        self.active_power = active_power
        self.reactive_power = reactive_power

    @classmethod
    def from_element(cls, element: NetworkElement) -> Self:
        if element.type != SupportedNetworkElementTypes.LOAD:
            raise ValueError("Element is not a 'LOAD'")
        if element.element_metadata.state != State.SOLVED:
            raise ValueError("Element of type 'LOAD' can't be observed if not solved.")
        # When disconnected, we get math nan for active and reactive power.
        return cls(
            id=element.id,
            timestamp=element.timestamp,
            type=element.type,
            status=ElementStatus.ON,
            bus_id=element.element_metadata.static.bus_id,
            voltage_level_id=element.element_metadata.static.voltage_level_id,
            Pd=element.element_metadata.dynamic.Pd,
            active_power=0
            if math.isnan(element.element_metadata.solved.p)
            else element.element_metadata.solved.p,
            reactive_power=0
            if math.isnan(element.element_metadata.solved.q)
            else element.element_metadata.solved.q,
        )

    @property
    def is_switchable(self) -> bool:
        return False

    @property
    def bus_ids(self) -> list[str]:
        return [self.bus_id]

    @property
    def voltage_level_ids(self) -> list[str]:
        return [self.voltage_level_id]

    @property
    def uncovered_load(self) -> float:
        return (self.Pd - self.active_power) if self.Pd > self.active_power else 0

    def to_array(self, one_hot_map: OneHotMap) -> np.ndarray:
        """
        This method turns a 'LoadObservation' to an array. It relies
        heavily on the one_hot_map, which allows to map a categorical attr to
        its relevant one-hot encoding.

        Params:
        - one_hot_map (dict[str, dict[str, np.ndarray]]): A dict containing with
        the type of mapping as a key and the category to array mapping as values.

        Returns:
            np.ndarray: The observation as an array.
        """

        return np.concatenate(
            [
                one_hot_map.types.get(self.type),
                one_hot_map.buses.get(self.bus_id),
                one_hot_map.voltage_levels.get(self.voltage_level_id),
                one_hot_map.statuses.get(self.status),
                [
                    self.Pd,
                    self.active_power,
                    self.reactive_power,
                ],
            ]
        )

    def to_dataframe(self) -> pd.DataFrame:
        """
        This method converts a 'LoadObservation' to a pd.DataFrame.
        """
        data = {
            "id": [self.id],
            "timestamp": [self.timestamp],
            "type": [self.type],
            "status": [self.status],
            "bus_id": [self.bus_id],
            "voltage_level_id": [self.voltage_level_id],
            "Pd": [self.Pd],
            "active_power": [self.active_power],
            "reactive_power": [self.reactive_power],
        }
        return pd.DataFrame(data)
