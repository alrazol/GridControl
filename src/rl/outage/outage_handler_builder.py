from abc import ABC, abstractmethod
from src.rl.outage.network_element_outage_handler import NetworkElementOutageHandler
from src.rl.outage.outage_handler import OutageHandler


class OutageHandlerBuilder(ABC):
    @staticmethod
    @abstractmethod
    def from_network_element_outage_handlers(
        network_element_outage_handlers: list[NetworkElementOutageHandler],
    ) -> OutageHandler:
        pass
