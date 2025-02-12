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
from src.rl.one_hot_map import OneHotMap
from src.core.utils import parse_datetime_to_str


class NetworkSnapshotObservation:
    """
    This class represents an observation of a Network at a single timestamp. See class NetworkHistoryObservation
    for a wrapper that allows keeping track of NetworkSnapshotObservation throughout timestamps.

    NOTE: BaseElementObservation objects in a NetworkSnapshotObservation are alphabetically sorted asc by their id.
    This allows to keep consistent arrays when applying to_array().
    """

    def __init__(
        self, observations: list[BaseElementObservation], timestamp: datetime
    ) -> None:
        self.observations = observations
        # TODO: "timestamp" might not be consistent with the observations?
        self.timestamp = timestamp

    @classmethod
    def from_network(cls, network: Network, timestamp: datetime) -> Self:
        """
        Loop through elements in the network to get a BaseElementObservation per element.
        """
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
        Convert a NetworkSnapshotObservation into a gym Space.
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
        Convert a NetworkSnapshotObservation to np.ndarray.
        """

        return np.concatenate(
            [obs.to_array(one_hot_map=one_hot_map) for obs in self.observations],
        )

    def to_dataframe(self) -> dict[SupportedNetworkElementTypes, pd.DataFrame]:
        """
        Convert a NetworkSnapshotObservation to pd.DataFrame.
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
        Get a BaseElementObservation from the NetworkSnapshotObservation.
        """

        obs = next((obs for obs in self.observations if obs.id == id), None)
        if obs is None:
            raise ValueError("Observation id not found.")
        return obs

    def to_dict(self) -> dict[str, Any]:
        """
        Convert NetworkSnapshotObservation to dict.
        """

        return {
            "observations": [obs.__dict__ for obs in self.observations],
            "timestamp": parse_datetime_to_str(self.timestamp),
        }


class NetworkObservation:
    """
    This class is a wrapper around NetworkSnapshotObservation. It stores a history of NetworkSnapshotObservation
    objects, allowing to augment the observation space with historical data. If history_length is 1, it behaves
    exactly like NetworkSnapshotObservation.
    """

    def __init__(
        self,
        history_length: int,
        network_snapshot_observations: tuple[NetworkSnapshotObservation, ...] = (),
    ):
        self.history_length = history_length
        self.network_snapshot_observations = network_snapshot_observations

    def add_network_snapshot_observation(
        self, network_snapshot_observation: NetworkSnapshotObservation
    ) -> Self:
        """
        Add to the history, removing the oldest observation if it's full.
        """
        return NetworkObservation(
            self.history_length,
            (self.network_snapshot_observations + (network_snapshot_observation,))[
                -self.history_length :
            ],
        )

    def list_network_snapshot_observations(self) -> list[NetworkSnapshotObservation]:
        """
        Get the NetworkSnapshotObservation as a list.
        """
        return list(self.network_snapshot_observations)

    def to_array(self, one_hot_map: OneHotMap) -> np.ndarray:
        """
        Convert a NetworkObservationHistory to np.ndarray.
        """
        if len(self.network_snapshot_observations) == 0:
            raise ValueError("Can't convert to np.ndarray if no snapshots provided.")

        missing = self.history_length - len(self.network_snapshot_observations)
        empty_obs = np.zeros_like(
            self.network_snapshot_observations[0].to_array(one_hot_map)
        )
        history_arrays = [empty_obs] * missing + [
            obs.to_array(one_hot_map) for obs in self.network_snapshot_observations
        ]

        return np.concatenate(history_arrays)

    def to_dict(self) -> dict[str, Any]:
        return {
            "history_length": self.history_length,
            "network_snapshot_observations": [
                obs.to_dict() for obs in self.network_snapshot_observations
            ],
        }

    def to_observation_space(self, one_hot_map: OneHotMap) -> spaces.Space:
        """
        Convert NetworkObservation to a gym Space.
        """
        if not self.network_snapshot_observations:
            raise ValueError("Cannot infer observation space from an empty history.")

        # Ensure all snapshots have the same observation space
        for snapshot in self.network_snapshot_observations:
            snapshot_space = snapshot.to_observation_space(one_hot_map)
            assert (
                snapshot_space.shape
                == self.network_snapshot_observations[0]
                .to_observation_space(one_hot_map)
                .shape
            ), "Mismatch in observation space shape across snapshots."

        # Extend the the observation space * history_length
        return spaces.Box(
            low=self.network_snapshot_observations[0]
            .to_observation_space(one_hot_map)
            .low.repeat(self.history_length, axis=0),
            high=self.network_snapshot_observations[0]
            .to_observation_space(one_hot_map)
            .high.repeat(self.history_length, axis=0),
            dtype=np.float32,
        )
