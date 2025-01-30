from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, inspect, Select
from src.core.infrastructure.database_base import Base
from src.core.domain.mappers.base import BaseMapper


class SQLiteClient:
    """
    A simpler SQL client to interact with a SQL database using SQLModel.
    """

    def __init__(self, db_url: str):
        """
        Initialize the SQL client.

        Args:
        - db_url (str): The database URL (e.g., "sqlite:///example.db").
        """
        self.engine = create_engine(
            db_url, echo=False
        )  # `echo=True` logs all SQL queries
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    @contextmanager
    def get_db(self):
        """
        Context manager to create and close database sessions.
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def create_tables(self, table_names: list[str] = None) -> None:
        """
        Create specified tables based on the Base metadata.
        If no table names are provided, all tables are created.

        Args:
        - table_names (list[str], optional): Names of the tables to create. If None, creates all tables.
        """
        if table_names:
            tables_to_create = [
                Base.metadata.tables[table_name]
                for table_name in table_names
                if table_name in Base.metadata.tables
            ]
            if not tables_to_create:
                print("No matching tables found to create.")
                return
            print(f"Creating tables: {', '.join(table_names)}")
            Base.metadata.create_all(bind=self.engine, tables=tables_to_create)
        else:
            print(f"Creating all tables: {', '.join(Base.metadata.tables.keys())}")
            Base.metadata.create_all(bind=self.engine)

        print("Tables created successfully.")

    def drop_tables(self, table_names: list[str] = None) -> None:
        """
        Drop specified tables based on the Base metadata.
        If no table names are provided, all tables are dropped.

        Args:
        - table_names (list[str], optional): Names of the tables to drop. If None, drops all tables.
        """
        if table_names:
            tables_to_drop = [
                Base.metadata.tables[table_name]
                for table_name in table_names
                if table_name in Base.metadata.tables
            ]
            if not tables_to_drop:
                print("No matching tables found to drop.")
                return
            print(f"Dropping tables: {', '.join(table_names)}")
            Base.metadata.drop_all(bind=self.engine, tables=tables_to_drop)
        else:
            print(f"Dropping all tables: {', '.join(Base.metadata.tables.keys())}")
            Base.metadata.drop_all(bind=self.engine)

        print("Tables dropped successfully.")

    def add_record(self, record: Base) -> None:
        """
        Add a single record to the database.

        Args:
        - record (Base): An instance of a SQLAlchemy declarative model to insert into the database.
        """
        with self.get_db() as session:
            session.add(record)

    def bulk_insert(self, records: list[Base]) -> None:
        """
        Add multiple records to the database.

        Args:
        - records (list[Base]): List of SQLAlchemy declarative model instances to insert into the database.
        """
        with self.get_db() as session:
            session.add_all(records)

    def query_with_statement(
        self,
        statement: Select,
        mapper: BaseMapper | None = None,
    ) -> list[Base]:
        """
        Execute a generic SQLAlchemy statement and return the results.

        Args:
        - statement (Select): A SQLAlchemy-compatible select statement.

        Returns:
        - list[Base]: A list of results matching the statement.
        """
        with self.get_db() as session:
            results = session.execute(statement).scalars().all()
            return (
                [mapper.schema_to_domain(result) for result in results]
                if mapper
                else results
            )

    def query_with_raw_sql(
        self,
        raw_sql: str,
        params: dict | None = None,
        mapper: BaseMapper | None = None,
    ) -> list[Base] | list[tuple]:
        """
        Execute a raw SQL query and return the results.

        Args:
        - raw_sql (str): The raw SQL query to execute.
        - params (dict, optional): Parameters to bind to the raw SQL query.
        - mapper (BaseMapper, optional): A mapper to transform raw results into domain models.

        Returns:
        - list[Base] | list[tuple]: A list of mapped results or tuples from the raw query.
        """
        with self.get_db() as session:
            # Execute raw SQL with optional parameters
            results = session.execute(raw_sql, params or {}).fetchall()

            # Map results if a mapper is provided
            if mapper:
                return [mapper.schema_to_domain(result) for result in results]

            return results

    def list_tables(self) -> list[str]:
        """
        List all tables currently in the database.

        Returns:
        - list[str]: A list of table names in the database.
        """
        return inspect(self.engine).get_table_names()
