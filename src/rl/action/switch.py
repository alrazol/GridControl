import copy
from typing import Self
from src.core.domain.models.network import Network
from src.rl.action.base import BaseAction
from src.core.constants import ElementStatus, SupportedNetworkElementTypes
from src.rl.action.enums import DiscreteActionTypes


class SwitchAction(BaseAction):
    """
    This class represents the action of switching (changing the ElementStatus)
    of a NetworkElement.
    """

    def __init__(self, element_id: str) -> None:
        super().__init__(
            action_type=DiscreteActionTypes.SWITCH,
        )
        self.element_id = element_id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SwitchAction):
            return False
        return self.element_id == other.element_id

    def __hash__(self) -> int:
        return hash(self.element_id)

    @staticmethod
    def validate(network: Network, element_id: str) -> None:
        """
        Perform checks to validate that a SwitchAction is valid upon
        an element_id and on a given Network.
        """
        elements = [i for i in network.elements]
        if element_id not in [i.id for i in elements]:
            raise ValueError(
                f"Element ID {element_id} does not exist in the network state."
            )

        if [i for i in elements if i.id == element_id][0].type not in [
            SupportedNetworkElementTypes.LINE,
        ]:
            raise ValueError("Switch action only applied to 'LINE' and 'GENERATOR'.")

        if isinstance(network, Network):
            if len(network.list_timestamps()) > 1:
                raise ValueError("Action can only apply to single timstamp Network.")

    @classmethod
    def from_network(cls, network: Network, element_id: str) -> Self:
        """
        Instanciate a valid SwitchAction.
        """
        cls.validate(network=network, element_id=element_id)
        return cls(element_id=element_id)

    def execute(self, network: Network) -> Network:
        """
        Switch the ElementStatus of the self.element_id in the Network.
        Returns a copy of the original Network (no inplace).
        """
        network_copy = copy.deepcopy(network)
        element, index = network_copy.pop_element(element_id=self.element_id)
        to_status = (
            ElementStatus.OFF
            if element.element_metadata.static.status == ElementStatus.ON
            else ElementStatus.ON
        )
        element.element_metadata.static.status = to_status
        network_copy.insert_element(element=element, index=index)
        return network_copy
