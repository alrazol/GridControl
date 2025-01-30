from abc import ABC, abstractmethod
from src.core.domain.models.network import Network


class NetworkRepository(ABC):
    """Will only need a get in the RL package."""

    @abstractmethod
    def get(self, network_id: str) -> Network:
        pass
