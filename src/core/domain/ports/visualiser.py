from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
from src.core.domain.models.network import Network


class Visualiser(ABC):
    @abstractmethod
    def get_single_line_diagram_per_voltage_level(
        network: Network, solved: bool, timestamp: datetime
    ) -> list[dict[str, Any]]:
        """This returns a dict which maps an image to each voltage level."""
        pass
