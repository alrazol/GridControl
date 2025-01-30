from sqlite3 import IntegrityError
from src.rl.repositories.experiment_repository import ExperimentRepository
from src.rl.sqlite_client import SQLiteClient
from src.rl.simulation.models import ExperimentRecordsCollection
from src.rl.mappers.experiment_collection import ExperimentRecordsCollectionMapper
from src.rl.schemas import ExperimentRecordsCollectionSchema
from sqlalchemy import select


class SQLiteExperimentRepository(ExperimentRepository):
    """SQLite implementation of a repository to store experiment rollouts."""

    def __init__(self, db_url: str, should_create_tables: bool):
        self.sql_client = SQLiteClient(db_url=db_url)
        self.experiment_collection_mapper = ExperimentRecordsCollectionMapper()

        if should_create_tables:
            table_names = [
                "experiment_record",
                "experiment_records_collection",
            ]
            self.sql_client.drop_tables(table_names=table_names)
            self.sql_client.create_tables(table_names=table_names)

    def get(self, collection_id: str) -> ExperimentRecordsCollection | None:
        """
        Retrieve a single network by ID and map it to the domain model.
        """
        statement = select(ExperimentRecordsCollectionSchema).where(
            ExperimentRecordsCollectionSchema.id == collection_id
        )
        results = self.sql_client.query_with_statement(
            statement=statement, mapper=self.experiment_collection_mapper
        )
        return results

    def add(self, collection: ExperimentRecordsCollection) -> None:
        """
        Add an ExperimentRecordsCollection to the repo.
        """
        try:
            self.sql_client.add_record(
                record=self.experiment_collection_mapper.domain_to_schema(collection)
            )
        except IntegrityError as e:
            print(f"Failed to add collection: {e}")
            raise ValueError("A collection with this ID already exists.") from e
