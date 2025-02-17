from abc import ABC, abstractmethod
from src.core.domain.models.network import Network
from src.rl.action.base import BaseAction


class NetworkTransitionHandler(ABC):
    @staticmethod
    @abstractmethod
    def build_next_network(
        current_network: Network, next_network_no_action: Network, action: BaseAction
    ) -> Network:
        pass
