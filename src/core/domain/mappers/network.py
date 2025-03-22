from src.core.domain.models.network import Network
from src.core.infrastructure.schemas import NetworkSchema
from src.core.domain.mappers.base import BaseMapper
from src.core.domain.mappers.element import NetworkElementMapper


class NetworkMapper(BaseMapper):
    """
    Mapper for Network schema and domain model.
    """

    def __init__(self) -> None:
        self.element_mapper = NetworkElementMapper()

    def schema_to_domain(self, schema: NetworkSchema) -> Network:
        domain_elements = [
            self.element_mapper.schema_to_domain(element) for element in schema.elements
        ]
        return Network(
            uid=schema.uid,
            id=schema.id,
            elements=domain_elements,
        )

    def domain_to_schema(self, domain: Network) -> NetworkSchema:
        schema_elements = [
            self.element_mapper.domain_to_schema(element) for element in domain.elements
        ]
        return NetworkSchema(
            uid=domain.uid,
            id=domain.id,
            elements=schema_elements,
        )
