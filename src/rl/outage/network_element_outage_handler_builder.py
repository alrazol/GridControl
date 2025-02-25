from abc import ABC, abstractmethod
from typing import Any
from src.rl.enums import Granularity
from src.core.domain.models.element import NetworkElement
from src.rl.outage.network_element_outage_handler import NetworkElementOutageHandler


class NetworkElementOutageHandlerBuilder(ABC):
    @staticmethod
    @abstractmethod
    def from_element(
        element: NetworkElement,
        config: dict[str, Any],
        granularity: Granularity,
    ) -> NetworkElementOutageHandler:
        pass
