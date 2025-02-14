from abc import ABC, abstractmethod
from src.rl.observation.network import NetworkSnapshotObservation, NetworkObservation


class NetworkObservationHandler(ABC):
    @staticmethod
    @abstractmethod
    def add_network_snapshot_observation(
        network_observation: NetworkObservation,
        network_snapshot_observation: NetworkSnapshotObservation,
    ) -> NetworkSnapshotObservation:
        pass
