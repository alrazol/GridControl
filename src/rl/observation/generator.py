import numpy as np
import pandas as pd
from datetime import datetime
from src.core.constants import State, SupportedNetworkElementTypes
from src.core.domain.models.element import NetworkElement
from typing import Self
from src.core.constants import ElementStatus
from src.rl.one_hot_map import OneHotMap
from src.rl.observation.base import BaseElementObservation
from src.core.utils import parse_datetime_to_str


class GeneratorObservation(BaseElementObservation):
    def __init__(
        self,
        id: str,
        timestamp: datetime,
        type: SupportedNetworkElementTypes,
        status: ElementStatus,
        bus_id: str,
        voltage_level_id: str,
        Ptarget: float,
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
        self.Ptarget = Ptarget
        self.active_power = active_power
        self.reactive_power = reactive_power

    @property
    def is_switchable(self) -> bool:
        return False

    @property
    def bus_ids(self) -> list[str]:
        return [self.bus_id]

    @property
    def voltage_level_ids(self) -> list[str]:
        return [self.voltage_level_id]

    @classmethod
    def from_element(cls, element: NetworkElement) -> Self:
        if element.type != SupportedNetworkElementTypes.GENERATOR:
            raise ValueError("Element is not a 'GENERATOR'")
        if element.element_metadata.state != State.SOLVED:
            raise ValueError(
                "Observation for 'GENERATOR' is only applicable to a 'SOLVED' element."
            )
        return cls(
            id=element.id,
            timestamp=element.timestamp,
            type=element.type,
            status=element.element_metadata.static.status,
            bus_id=element.element_metadata.static.bus_id,
            voltage_level_id=element.element_metadata.static.voltage_level_id,
            Ptarget=element.element_metadata.dynamic.Ptarget,
            active_power=element.element_metadata.solved.p,
            reactive_power=element.element_metadata.solved.q,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": parse_datetime_to_str(self.timestamp),
            "type": self.type,
            "status": self.status,
            "bus_id": self.bus_id,
            "voltage_level_id": self.voltage_level_id,
            "Ptarget": self.Ptarget,
            "active_power": self.active_power,
            "reactive_power": self.reactive_power,
        }

    def to_array(self, one_hot_map: "OneHotMap") -> np.ndarray:
        """
        This method turns a 'GeneratorObservation' to an array. It relies
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
                np.array([self.active_power, self.reactive_power, self.Ptarget]),
            ]
        )

    def to_dataframe(self) -> pd.DataFrame:
        """
        This method converts a 'GeneratorObservation' to a pd.DataFrame.
        """
        data = {
            "id": [self.id],
            "timestamp": [self.timestamp],
            "type": [self.type],
            "status": [self.status],
            "bus_id": [self.bus_id],
            "voltage_level_id": [self.voltage_level_id],
            "Ptarget": [self.Ptarget],
            "active_power": [self.active_power],
            "reactive_power": [self.reactive_power],
        }
        return pd.DataFrame(data)


class GeneratorObservationWithOutage(BaseElementObservation):
    def __init__(
        self, base_observation: GeneratorObservation, outage_probability: float
    ):
        self.base_observation = base_observation
        self.outage_probability = outage_probability

    @property
    def is_switchable(self) -> bool:
        return self.base_observation.is_switchable

    @property
    def bus_ids(self) -> list[str]:
        return self.base_observation.bus_ids

    @property
    def voltage_level_ids(self) -> list[str]:
        return self.base_observation.voltage_level_ids

    @classmethod
    def from_element(cls, element: NetworkElement, outage_probability: float) -> Self:
        base_observation = GeneratorObservation.from_element(element)
        return cls(base_observation, outage_probability)

    def to_dict(self) -> dict:
        base_dict = self.base_observation.to_dict()
        base_dict["outage_probability"] = self.outage_probability
        return base_dict

    def to_array(self, one_hot_map: OneHotMap) -> np.ndarray:
        base_array = self.base_observation.to_array(one_hot_map)
        return np.concatenate([base_array, [self.outage_probability]])

    def to_dataframe(self) -> pd.DataFrame:
        df = self.base_observation.to_dataframe()
        df["outage_probability"] = self.outage_probability
        return df
