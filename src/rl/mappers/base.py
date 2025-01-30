from abc import ABC, abstractmethod
from typing import Generic, TypeVar

SchemaT = TypeVar("SchemaT")
DomainT = TypeVar("DomainT")


class BaseMapper(ABC, Generic[SchemaT, DomainT]):
    """
    Abstract base class for mappers between schemas and domain models.
    """

    @abstractmethod
    def schema_to_domain(self, schema: SchemaT) -> DomainT:
        """Map a schema object to a domain model."""
        pass

    @abstractmethod
    def domain_to_schema(self, domain: DomainT) -> SchemaT:
        """Map a domain model to a schema object."""
        pass
