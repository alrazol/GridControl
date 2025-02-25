from typing import Any
from src.core.domain.models.element import NetworkElement
from src.rl.outage.network_element_outage_handler import NetworkElementOutageHandler
from src.rl.enums import Granularity
from src.rl.repositories.network_element_outage_handler import (
    DefaultNetworkElementOutageHandler,
)
from src.rl.outage.network_element_outage_handler_builder import (
    NetworkElementOutageHandlerBuilder,
)


class DefaultNetworkElementOutageHandlerBuilder(NetworkElementOutageHandlerBuilder):
    @staticmethod
    def from_element(
        element: NetworkElement,
        config: dict[str, Any],  # TODO: This should be a Config object
        granularity: Granularity,
    ) -> NetworkElementOutageHandler:
        return DefaultNetworkElementOutageHandler(
            element=element,
            initial_outage_prob=config.get("initial_outage_prob"),
            initial_remaining_duration=config.get("initial_remaining_duration"),
            initial_usage_time=config.get("initial_usage_time"),
            lambda_factor=config.get("lambda_factor"),
            seed=config.get("seed"),
            granularity=granularity,
        )
