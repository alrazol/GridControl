from src.rl.observation.base import BaseElementObservation
from gym.spaces import Space
from src.core.domain.models.network import Network
from src.core.constants import SupportedNetworkElementTypes
from src.rl.observation.line import LineObservation
from src.rl.observation.generator import GeneratorObservation
from src.rl.observation.load import LoadObservation
from typing import Self
from gym import spaces
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Any
from src.rl.observation.one_hot_map import OneHotMap
from src.core.utils import parse_datetime_to_str


class NetworkObservation:
    """
    This class represents what the agent is able to observe from the Network at a timestamp.
    At this early stage, this is assumed to be the aggregation of what it can observe from
    each element in the Network, nothing less and nothing more.

    Observations in a NetworkObervation are sorted by their id (referring to the element id).
    This allows to keep consistent arrays when turning the NetworkObservation into an array.
    """

    def __init__(
        self, observations: list[BaseElementObservation], timestamp: datetime
    ) -> None:
        self.observations = observations
        self.timestamp = timestamp  # TODO: Not completely clear

    @classmethod
    def from_network(cls, network: Network, timestamp: datetime) -> Self:
        """
        Build a NetworkObservation by observing each element of a Network.
        """
        # Sort elements by their id to ensure consistency across NetworkObservation from same Network
        observations = []
        for element in sorted(network.elements, key=lambda e: e.id):
            if element.type == SupportedNetworkElementTypes.LINE:
                observations.append(LineObservation.from_element(element))
            elif element.type == SupportedNetworkElementTypes.LOAD:
                observations.append(LoadObservation.from_element(element))
            elif element.type == SupportedNetworkElementTypes.GENERATOR:
                observations.append(GeneratorObservation.from_element(element))

        return cls(observations, timestamp)

    def to_observation_space(self, one_hot_map: OneHotMap) -> Space:
        """
        Converts a NetworkObservation into a gym observation space. The Space is
        a continuous space with the dimension of the array representing the NetworkObservation.
        """

        observation_array = np.concatenate(
            [
                observation.to_array(one_hot_map=one_hot_map)
                for observation in self.observations
            ]
        )

        return spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(observation_array.size,),
            dtype=np.float32,
        )

    def to_array(self, one_hot_map: OneHotMap) -> np.ndarray:
        """
        Turns a NetworkObservation into an array, iterating through element
        observations and concatenating their array representations.
        """

        return np.concatenate(
            [obs.to_array(one_hot_map=one_hot_map) for obs in self.observations],
        )

    def to_dataframe(self) -> dict[SupportedNetworkElementTypes, pd.DataFrame]:
        """
        Turns a network observation into a dict that maps types to pd.DataFrame.
        """
        res = {}
        all_types = sorted(set([t.type.value for t in self.observations]))
        for t in all_types:
            res[t] = pd.concat(
                [obs.to_dataframe() for obs in self.observations if obs.type == t]
            )

        return res

    def get_observation(self, id: str) -> BaseElementObservation:
        """
        Get a single element observation from the NetworkObservation.
        """

        obs = next((obs for obs in self.observations if obs.id == id), None)
        if obs is None:
            raise ValueError("Observation id not found.")
        return obs

    def to_dict(self) -> dict[str, Any]:
        """
        Convert NetworkObservation to a dict to be used for ex in
        building a schema from the object.
        """

        return {
            "observations": [obs.__dict__ for obs in self.observations],
            "timestamp": parse_datetime_to_str(self.timestamp),
        }
