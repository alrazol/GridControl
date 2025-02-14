from src.core.domain.models.network import Network
from src.rl.action.base import BaseAction
from src.core.constants import SupportedNetworkElementTypes
from src.rl.repositories.network_transition_handler import NetworkTransitionHandler


class DefaultNetworkTransitionHandler(NetworkTransitionHandler):
    @staticmethod
    def build_next_network(
        current_network: Network,
        next_network_no_action: Network,
        action: BaseAction,
    ) -> Network:
        """
        Build next Network by inplacing dynamic attributes of elements, and applying action.
        """
        out = action.execute(current_network)
        next_timestamp = next_network_no_action.elements[0].timestamp
        out.id = next_network_no_action.id
        for element in out.elements:
            element.timestamp = next_timestamp
            if element.type in [
                SupportedNetworkElementTypes.GENERATOR,
                SupportedNetworkElementTypes.LOAD,
            ]:
                element.element_metadata.dynamic = next_network_no_action.get_element(
                    id=element.id, timestamp=next_timestamp
                ).element_metadata.dynamic
        return out
