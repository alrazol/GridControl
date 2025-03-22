from abc import ABC, abstractmethod
from src.rl.outage.outage_handler import OutageHandler
from src.rl.action.enums import DiscreteActionTypes
from src.rl.action_space import ActionSpace
from src.core.domain.models.network import Network


class ActionSpaceBuilder(ABC):
    @staticmethod
    @abstractmethod
    def from_action_types(
        cls,
        action_types: list[DiscreteActionTypes],
        network: Network,
        outage_handler: OutageHandler,
    ) -> ActionSpace:
        """
        Build an ActionSpace from a list of BaseAction.
        """
        pass
