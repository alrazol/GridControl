from src.core.domain.models.network import Network
from src.rl.action.base import BaseAction
from src.core.constants import ElementStatus, SupportedNetworkElementTypes
from src.rl.environment_helpers import NetworkTransitionHandler
from src.rl.outage.outage_handler import OutageHandler


class WithOutageNetworkTransitionHandler(NetworkTransitionHandler):
    @staticmethod
    def build_next_network(
        current_network: Network,
        next_network_no_action: Network,
        action: BaseAction,
        outage_handler: OutageHandler,
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
            network_element_outage_handler = (
                outage_handler.get_network_element_outage_handler(element_id=element.id)
            )
            if (
                network_element_outage_handler
                and network_element_outage_handler.status
                in [ElementStatus.OUTAGE, ElementStatus.MAINTENANCE]
            ):
                element.element_metadata.static.status = (
                    network_element_outage_handler.status
                )
            else:
                continue
        outage_handler.step()
        return out
