from abc import ABC, abstractmethod
from src.core.domain.models.network import Network
from src.core.domain.models.element import NetworkElement
from datetime import datetime


class DatabaseNetworkRepository(ABC):
    @abstractmethod
    def get(self, network_id: str) -> Network:
        pass

    @abstractmethod
    def get_elements(
        self, network_id: str, timestamp: datetime | None = None
    ) -> list[NetworkElement]:
        pass

    def list_available_networks(self) -> list[str]:
        pass

    @abstractmethod
    def add(self, network: Network) -> None:
        pass

    @abstractmethod
    def add_elements(self, elements: list[NetworkElement]) -> None:
        pass
