from typing import Self
from abc import ABC, abstractmethod
from src.rl.action.enums import DiscreteActionTypes, ContinuousActionTypes
from src.core.domain.models.network import Network


class BaseAction(ABC):
    def __init__(
        self,
        action_type: DiscreteActionTypes | ContinuousActionTypes,
        element_id: str | None = None,
        parameters: dict | None = None,
    ) -> None:
        self.element_id = element_id
        self.action_type = action_type
        self.is_discrete = isinstance(action_type, DiscreteActionTypes)
        self.parameters = parameters or {}

    @abstractmethod
    def validate(self, network: Network) -> bool:
        """Raises on violation."""
        pass

    @abstractmethod
    def execute(self, network: Network) -> Network:
        """Execute the action on a Network. Should return the 'new' Network."""
        pass

    @classmethod
    @abstractmethod
    def from_network(
        cls,
        element_id: str | None,
        network: Network,
        parameters: dict | None = None,
    ) -> Self:
        """Raises on violation."""
        pass

    def __repr__(self):
        return f"Action(type={self.action_type}, component={self.element_id}, params={self.parameters})"
