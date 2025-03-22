from typing import Self
from src.rl.outage.outage_handler import OutageHandler
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
    def validate(
        network: Network,
        element_id: str,
        outage_handler: OutageHandler,
    ) -> None:
        """
        Perform checks to validate that a SwitchAction is valid upon
        an element_id and on a given Network.
        """

        # The element should have info about how long maintenance
        # has been going on for, so we can look up in case it's under
        # maintenance. Or we pass the outage hander to not touch the base
        # object.

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

        if network.get_element(
            id=element_id, timestamp=network.elements[0].timestamp
        ).element_metadata.static.status in [
            ElementStatus.MAINTENANCE,
        ]:
            element_outage_handler = outage_handler.get_network_element_outage_handler(
                element_id=element_id
            )
            if element_outage_handler:
                if element_outage_handler.remaining_duration > 0:
                    raise ValueError(
                        "Can't switch an element that is still under maintenance."
                    )
            else:
                # NOTE: This is weird, it can't be just excepted when building the action space.
                raise ValueError(
                    "Can't switch an element that is under maintenance without an outage handler."
                )

        if network.get_element(
            id=element_id, timestamp=network.elements[0].timestamp
        ).element_metadata.static.status in [
            ElementStatus.OUTAGE,
        ]:
            element_outage_handler = outage_handler.get_network_element_outage_handler(
                element_id=element_id
            )
            if element_outage_handler:
                if element_outage_handler.remaining_duration > 0:
                    raise ValueError(
                        "Can't switch an element that is still under outage."
                    )
            else:
                # NOTE: This is weird, it can't be just excepted when building the action space.
                raise ValueError(
                    "Can't switch an element that is under outage without an outage handler."
                )

    @classmethod
    def from_network(
        cls, network: Network, element_id: str, outage_handler: OutageHandler
    ) -> Self:
        """
        Instanciate a valid SwitchAction.
        """
        cls.validate(
            network=network, element_id=element_id, outage_handler=outage_handler
        )
        return cls(element_id=element_id)

    def execute(self, network: Network) -> Network:
        """
        Switch the ElementStatus of the self.element_id in the Network.
        Modifies the input network in-place and returns it.
        """
        element = [i for i in network.elements if i.id == self.element_id][0]

        element.element_metadata.static.status = (
            ElementStatus.OFF
            if element.element_metadata.static.status == ElementStatus.ON
            else ElementStatus.ON
        )

        return network
