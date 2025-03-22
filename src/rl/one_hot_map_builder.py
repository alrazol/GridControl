from abc import ABC, abstractmethod
from src.rl.observation.network import NetworkSnapshotObservation
from src.rl.one_hot_map import OneHotMap


class OneHotMapBuilder(ABC):
    """
    Class to build a OneHotMap instance from a list of observations.
    """

    @staticmethod
    @abstractmethod
    def from_network_snapshot_observation(
        network_snapshot_observation: NetworkSnapshotObservation,
    ) -> OneHotMap:
        """
        Create and fit a OneHotMap instance from a list of observations.
        """
        pass
