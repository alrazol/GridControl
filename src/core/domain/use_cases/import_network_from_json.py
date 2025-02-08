import json
from pathlib import Path
from src.core.domain.models.network import Network
from src.core.domain.models.element import NetworkElement
from src.core.domain.ports.network_repository import DatabaseNetworkRepository
from src.core.domain.models.operational_constraint import OperationalConstraint
from src.core.utils import parse_datetime
from src.core.constants import DATETIME_FORMAT, DEFAULT_TIMEZONE
from src.core.domain.models.elements_metadata import MetadataRegistry
from src.core.constants import SupportedNetworkElementTypes
from src.core.domain.enums import BranchSide, OperationalConstraintType

# TODO: Add logger in core


class ETLPipeline:
    """
    This pipeline ingests data from Json files into the NetworkElement table in the database.
    """

    # TODO: MetadataRegistry as a dependency
    def __init__(self, network_repository: DatabaseNetworkRepository) -> None:
        """
        Initialize the ETL pipeline.

        Args:
            db_client (SQLClient): An instance of the SQL client to interact with the database.
        """
        self.network_repository = network_repository

    def load_json(self, file_path: Path) -> None:
        """
        Load a Json file.

        Args:
            file_path (str | Path): Path to the JSon file.

        Returns:
            dict: Loaded data as a dict.
        """
        try:
            with open(str(file_path), "r") as f:
                return json.load(f)
        except FileNotFoundError as e:
            raise ValueError(f"File not found: {file_path}") from e

    def validate_and_transform(self, data: dict) -> Network:
        """
        Validate and transform the data into a list of NetworkElement objects.

        Args:
            data (dict): Input data as a dict.

        Returns:
            Tuple[dict[str, str], dict[str, list[NetworkElement]]]: A tuple with the collection metadata at position
            0 and the a dict mapping timestamps to corresponding netwotks at position 1.
        """

        # collection_metadata = data["networks_collection_metadata"]
        if set(data.keys()) != set(["network_metadata", "network_data"]):
            raise ValueError(
                "A json entry point must contain data for a single network over time, with keys: 'network_metadata' and 'network_data'"
            )
        elements = []
        for element in data["network_data"]:
            timestamp_datetime = (
                parse_datetime(
                    element.get("timestamp"),
                    format=DATETIME_FORMAT,
                    tz=DEFAULT_TIMEZONE,
                )
                if element.get("timestamp") is not None
                else None
            )
            metadata = MetadataRegistry[element.get("type")](
                **element.get("element_metadata")
            )
            operational_constraints = [
                OperationalConstraint.from_element(
                    element_id=element.get("id"),
                    timestamp=timestamp_datetime,
                    element_type=SupportedNetworkElementTypes(element.get("type")),
                    side=BranchSide(op.get("side")),
                    name=op.get("name"),
                    type=OperationalConstraintType(op.get("type")),
                    value=op.get("value"),
                    acceptable_duration=op.get("acceptable_duration"),
                )
                for op in element.get("operational_constraints")
            ]

            elements.append(
                NetworkElement.from_metadata(
                    id=element.get("id"),
                    timestamp=timestamp_datetime,
                    type=SupportedNetworkElementTypes(element.get("type")),
                    element_metadata=metadata,
                    network_id=data["network_metadata"].get("name"),
                    operational_constraints=operational_constraints,
                )
            )

        network = Network.from_elements(
            id=data["network_metadata"].get("name"),
            elements=elements,
        )

        return network

    def insert_into_db(
        self, network: Network, network_repository: DatabaseNetworkRepository
    ) -> None:
        """
        Insert a collection of networks into the database.

        Args:
            collection (NetworkCollection): A network collection.
        """
        # try:
        network_repository.add(network=network)
        # network_repository.add_elements(elements=network.elements)

        # except Exception as e:
        #    print(e)

    def run(self, file_path: Path) -> None:
        """
        Run the ETL pipeline.

        Args:
            file_path (Path): Path to the input CSV file.
        """
        print("Starting ETL pipeline...")
        # Step 1: Load Json
        data = self.load_json(file_path)

        # Step 2: Validate and Transform
        network = self.validate_and_transform(data=data)
        print(f"Validated {len(network.elements)} records.")

        # Step 3: Insert into DB
        self.insert_into_db(network=network, network_repository=self.network_repository)
        print("ETL pipeline completed successfully.")
