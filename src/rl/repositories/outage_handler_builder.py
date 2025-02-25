from src.rl.repositories.outage_handler import DefaultOutageHandler
from src.rl.outage.outage_handler import OutageHandler
from src.rl.outage.network_element_outage_handler import NetworkElementOutageHandler
from src.rl.outage.outage_handler_builder import OutageHandlerBuilder


class DefaultOutageHandlerBuilder(OutageHandlerBuilder):
    @staticmethod
    def from_network_element_outage_handlers(
        network_element_outage_handlers: list[NetworkElementOutageHandler],
    ) -> OutageHandler:
        return DefaultOutageHandler(
            network_element_outage_handlers=network_element_outage_handlers,
        )
