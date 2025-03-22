from src.rl.outage.network_element_outage_handler import NetworkElementOutageHandler
from src.rl.outage.outage_handler import OutageHandler


class DefaultOutageHandler(OutageHandler):
    def __init__(
        self, network_element_outage_handlers: list[NetworkElementOutageHandler]
    ) -> None:
        self.network_element_outage_handlers = network_element_outage_handlers

    def reset(self) -> None:
        for i in self.network_element_outage_handlers:
            i.reset()

    def step(self) -> None:
        for i in self.network_element_outage_handlers:
            i.step()

    def get_network_element_outage_handler(
        self, element_id: str
    ) -> NetworkElementOutageHandler:
        matching_elements = [
            i
            for i in self.network_element_outage_handlers
            if i.element_id == element_id
        ]
        if len(matching_elements) == 1:
            return matching_elements[0]
        return None
