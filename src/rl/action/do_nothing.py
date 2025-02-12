from src.rl.action.enums import DiscreteActionTypes
from src.core.domain.models.network import Network
from src.rl.action.base import BaseAction
from typing import Self


class DoNothingAction(BaseAction):
    """An action that performs no changes."""

    def __init__(self) -> None:
        super().__init__(
            action_type=DiscreteActionTypes.DO_NOTHING,
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, DoNothingAction)

    def __hash__(self) -> int:
        return hash("DoNothingAction")

    @staticmethod
    def validate() -> None:
        """
        Always valid, as this action performs no operation.
        """
        pass

    def execute(self, network: "Network") -> "Network":
        """
        Perform no operation on the network and return it unchanged.
        """
        return network

    @classmethod
    def from_network(cls) -> Self:
        cls.validate()
        return cls()
