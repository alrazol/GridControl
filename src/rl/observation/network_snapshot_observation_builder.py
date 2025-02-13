from abc import ABC, abstractmethod
from datetime import datetime
from src.core.domain.models.network import Network
from src.rl.observation.network import NetworkSnapshotObservation


class NetworkSnapshotObservationBuilder(ABC):
    @staticmethod
    @abstractmethod
    def from_network(
        network: Network,
        timestamp: datetime,
    ) -> NetworkSnapshotObservation:
        pass
