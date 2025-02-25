from abc import ABC, abstractmethod
from src.rl.outage.network_element_outage_handler import NetworkElementOutageHandler


class OutageHandler(ABC):
    @abstractmethod
    def reset(self) -> None:
        pass

    @abstractmethod
    def step(self) -> None:
        pass

    @abstractmethod
    def get_network_element_outage_handler(element_id: str) -> NetworkElementOutageHandler:
        pass
