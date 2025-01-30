from datetime import datetime
from src.core.infrastructure.services.converters.pypowsybl_methods.element import (
    element_to_pypowsybl,
    element_from_pypowsybl,
)
from src.core.infrastructure.services.converters.pypowsybl_methods.network import (
    network_to_pypowsybl,
)
from src.core.domain.models.network import Network
from src.core.domain.models.element import NetworkElement
from src.core.constants import SupportedNetworkElementTypes
from src.core.domain.models.operational_constraint import OperationalConstraint
from src.core.infrastructure.services.converters.pypowsybl_methods.models.pypowsybl_network_wrapper import (
    PyPowSyblNetworkWrapper,
)


class PyPowsyblCompatService:  # TODO: The reverse, pypowsybl_to_network
    @staticmethod
    def network_to_pypowsybl(network: Network) -> PyPowSyblNetworkWrapper:
        return network_to_pypowsybl(network=network)

    @staticmethod
    def element_to_pypowsybl(element: NetworkElement) -> dict:
        return element_to_pypowsybl(element=element)

    @staticmethod
    def element_from_pypowsybl(
        element_id: str,
        element_type: SupportedNetworkElementTypes,
        network_id: str,
        timestamp: datetime | None,
        element_metadata_pypowsybl: dict,
        operational_constraints: list[OperationalConstraint],
    ) -> NetworkElement:
        return element_from_pypowsybl(
            element_id=element_id,
            element_type=element_type,
            network_id=network_id,
            timestamp=timestamp,
            element_metadata_pypowsybl=element_metadata_pypowsybl,
            operational_constraints=operational_constraints,
        )
