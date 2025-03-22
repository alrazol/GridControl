from abc import ABC, abstractmethod
from src.core.domain.models.network import Network
from src.core.domain.models.element import NetworkElement


class NetworkBuilder(ABC):
    @staticmethod
    @abstractmethod
    def from_elements(id: str, elements: list[NetworkElement]) -> Network:
        pass
