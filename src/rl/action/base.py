from typing import Self
from abc import ABC, abstractmethod
from src.rl.action.enums import DiscreteActionTypes, ContinuousActionTypes
from src.core.domain.models.network import Network


class BaseAction(ABC):
    def __init__(
        self,
        action_type: DiscreteActionTypes | ContinuousActionTypes,
    ) -> None:
        self.action_type = action_type
        self.is_discrete = isinstance(action_type, DiscreteActionTypes)

    @staticmethod
    @abstractmethod
    def validate() -> None:
        """
        Some validation logic to be used when instanciating the
        BaseAction from a Network.
        """
        pass

    @abstractmethod
    def execute(self, network: Network) -> Network:
        """
        Execute the action on a Network. Return a new Network.
        """
        pass

    @classmethod
    @abstractmethod
    def from_network(cls, network: Network) -> Self:
        """
        Instanciate the action, allowing to run custom validation on Network.
        Should use the validate() method to check legality at instanciation.
        """
        pass
