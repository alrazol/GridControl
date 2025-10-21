from sqlite3 import IntegrityError
from src.core.domain.mappers.network import NetworkMapper
from src.core.domain.mappers.element import NetworkElementMapper
from src.core.infrastructure.sqlite_client import SQLiteClient
from src.core.domain.models.network import Network
from src.core.domain.models.element import NetworkElement
from sqlalchemy import select, distinct
from src.core.infrastructure.schemas import NetworkSchema, NetworkElementSchema
from datetime import datetime
from src.core.domain.ports.network_repository import DatabaseNetworkRepository


class SQLiteNetworkRepository(DatabaseNetworkRepository):
    """SQLite implementation of a repository to access networks."""

    def __init__(self, db_url: str, should_create_tables: bool):
        self.sql_client = SQLiteClient(db_url=db_url)
        self.network_mapper = NetworkMapper()
        self.element_mapper = NetworkElementMapper()

        if should_create_tables:
            table_names = [
                "network_element",
                "network",
                "network_element_operational_constraint",
            ]
            self.sql_client.drop_tables(table_names=table_names)
            self.sql_client.create_tables(table_names=table_names)

    def get(self, network_id: str) -> Network | None:
        """
        Retrieve a single network by ID and map it to the domain model.
        """
        statement = select(NetworkSchema).where(NetworkSchema.id == network_id)
        results = self.sql_client.query_with_statement(
            statement=statement, mapper=NetworkMapper()
        )
        if results:
            return results[0]
        return None

    def get_elements(
        self,
        network_id: str,
        timestamp: datetime | None = None,
    ) -> list[NetworkElement]:
        """
        Retrieve network elements and map them to domain models.
        """
        statement = select(NetworkElementSchema).where(
            NetworkElementSchema.network_id == network_id
        )
        if timestamp:
            statement = statement.where(NetworkElementSchema.timestamp == timestamp)
        results = self.sql_client.query_with_statement(
            statement=statement, mapper=NetworkElementMapper()
        )
        if results:
            return results
        return None

    def list_available_networks(self) -> list[str]:
        """
        List available network IDs.
        """
        statement = select(distinct(NetworkSchema.id))
        results = self.sql_client.query_with_statement(statement=statement)
        return [row[0] for row in results]  # Ensure a flat list of IDs

    def add(self, network: Network) -> None:
        """
        Add a network to the database by mapping the domain model to the schema.
        """
        try:
            self.sql_client.add_record(
                record=self.network_mapper.domain_to_schema(network)
            )
        except IntegrityError as e:
            print(f"Failed to add network: {e}")
            raise ValueError("A network with this ID already exists.") from e

    def add_elements(self, elements: NetworkElement) -> None:
        """
        Add elements to the database by mapping the domain model to the schema.
        """
        try:
            for element in elements:
                self.sql_client.add_record(
                    record=self.element_mapper.domain_to_schema(element)
                )
        except IntegrityError as e:
            print(f"Failed to add network: {e}")
            raise ValueError("A network with this ID already exists.") from e
