import requests
from src.core.domain.enums import BranchSide, OperationalConstraintType
from src.core.domain.models.operational_constraint import OperationalConstraint
from src.core.domain.models.elements_metadata import MetadataRegistry
from src.core.utils import parse_datetime
from src.rl.repositories.network_repository import NetworkRepository
from src.core.domain.models.network import Network
from src.core.domain.models.element import NetworkElement
from src.rl.repositories.network_builder import NetworkBuilder
from typing import Any
from src.core.constants import (
    DATETIME_FORMAT,
    DEFAULT_TIMEZONE,
    SupportedNetworkElementTypes,
)


class HttpNetworkRepository(NetworkRepository):
    def __init__(self, baseurl: str, network_builder: NetworkBuilder):
        self.baseurl = baseurl
        self.network_builder = network_builder

    def get(self, network_id: str) -> Network:
        endpoint = "get-network"
        headers = {
            "Accept": "application/json",
        }
        params = {"network_id": network_id}
        response_data = requests.get(
            url=f"{self.baseurl}/{endpoint}",
            params=params,
            headers=headers,
        )
        response_data.raise_for_status()
        return self.process_data(data=response_data.json())

    def process_data(self, data: dict[str, Any]) -> Network:
        elements = [
            NetworkElement.from_metadata(
                id=element.get("id"),
                timestamp=parse_datetime(
                    element.get("timestamp"),
                    format=DATETIME_FORMAT,
                    tz=DEFAULT_TIMEZONE,
                ),
                type=SupportedNetworkElementTypes(element.get("type")),
                element_metadata=MetadataRegistry[element.get("type")](
                    **element.get("element_metadata")
                ),
                network_id=element.get("network_id"),
                operational_constraints=[
                    OperationalConstraint(
                        uid=constraint.get("uid"),
                        element_uid=constraint.get("element_uid"),
                        element_id=constraint.get("element_id"),
                        side=BranchSide(constraint.get("side")),
                        name=constraint.get("name"),
                        type=OperationalConstraintType(constraint.get("type")),
                        value=constraint.get("value"),
                        acceptable_duration=constraint.get("acceptable_duration"),
                    )
                    for constraint in element.get("operational_constraints")
                ],
            )
            for element in data.get("elements")
        ]

        return self.network_builder.from_elements(id=data.get("id"), elements=elements)
