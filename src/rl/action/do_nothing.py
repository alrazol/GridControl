from src.rl.action.enums import DiscreteActionTypes
from src.core.domain.models.network import Network
from src.rl.action.base import BaseAction
from typing import Self


class DoNothingAction(BaseAction):
    """An action that performs no operation."""

    def __init__(self) -> None:
        super().__init__(
            action_type=DiscreteActionTypes.DO_NOTHING,
        )

    def validate(self, network: Network) -> bool:
        """
        Always valid, as this action performs no operation.
        """
        return True

    def execute(self, network: "Network") -> "Network":
        """
        Perform no operation on the network and return it unchanged.

        :param network: The current network.
        :return: The unchanged network.
        """
        #print("Executing DoNothingAction: No changes made to the network.")
        return network

    @classmethod
    def from_network(
        cls,
        network: Network,
        element_id: str | None = None,
        parameters: dict | None = None,
    ) -> Self:
        return cls()
