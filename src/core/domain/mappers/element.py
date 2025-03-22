from enum import Enum
from src.core.domain.models.element import NetworkElement
from src.core.infrastructure.schemas import NetworkElementSchema
from src.core.domain.mappers.base import BaseMapper
from src.core.domain.mappers.operational_constraints import OperationalConstraintsMapper
from src.core.utils import parse_datetime, parse_datetime_to_str
from src.core.constants import (
    DATETIME_FORMAT,
    DEFAULT_TIMEZONE,
    SupportedNetworkElementTypes,
)
from src.core.domain.models.elements_metadata import MetadataRegistry


class NetworkElementMapper(BaseMapper[NetworkElementSchema, NetworkElement]):
    """
    Mapper for NetworkElement schema and domain model.
    """

    def __init__(self) -> None:
        self.operational_constraints_mapper = OperationalConstraintsMapper()

    def schema_to_domain(self, schema: NetworkElementSchema) -> NetworkElement:
        return NetworkElement.from_metadata(
            id=schema.id,
            timestamp=parse_datetime(
                schema.timestamp, format=DATETIME_FORMAT, tz=DEFAULT_TIMEZONE
            )
            if schema.timestamp is not None
            else schema.timestamp,
            type=SupportedNetworkElementTypes(schema.type),
            element_metadata=MetadataRegistry[schema.type](**schema.element_metadata),
            network_id=schema.network_id,
            operational_constraints=[
                self.operational_constraints_mapper.schema_to_domain(constraint)
                for constraint in schema.operational_constraints
            ],
        )

    def domain_to_schema(self, domain: NetworkElement) -> NetworkElementSchema:
        schema_operational_constraints = [
            self.operational_constraints_mapper.domain_to_schema(constraint)
            for constraint in domain.operational_constraints
        ]

        # Convert Enums to str in metadata which has no to_schema method
        converted = {}
        for key, value in domain.element_metadata.model_dump().items():
            if isinstance(value, Enum):  # If it's a top-level Enum
                converted[key] = value.value
            elif isinstance(value, dict):  # If it's a nested dictionary
                converted[key] = {
                    sub_key: (
                        sub_value.value if isinstance(sub_value, Enum) else sub_value
                    )
                    for sub_key, sub_value in value.items()
                }
            else:  # For other data types, keep as is
                converted[key] = value

        return NetworkElementSchema(
            uid=domain.uid,
            id=domain.id,
            timestamp=parse_datetime_to_str(domain.timestamp)
            if domain.timestamp
            else None,
            type=domain.type.value,
            element_metadata=converted,
            network_id=domain.network_id,
            operational_constraints=schema_operational_constraints,
        )
