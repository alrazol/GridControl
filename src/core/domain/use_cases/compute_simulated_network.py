from datetime import timedelta
from functools import reduce
from click import Path
import numpy as np
from src.core.domain.models.config_loaders.time_series_simulator import Config
from src.core.domain.models.network import Network
from src.core.domain.models.element import NetworkElement

from src.core.domain.models.elements_metadata import MetadataRegistry
import src.core.domain.models.simulators as sim
from src.core.constants import DATETIME_FORMAT, State, DEFAULT_TIMEZONE
from src.core.utils import parse_datetime
from src.core.domain.ports.network_repository import DatabaseNetworkRepository
from src.core.domain.models.operational_constraint import OperationalConstraint
from src.core.domain.ports.network_builder import NetworkBuilder


class SimulationPipeline:
    """
    This class is used to run a simulation on a Network. This basically implies
    to generate synthetic data for the physical characteristics of the different
    NetworkElement of our Network.
    Not all NetworkElement s support dynamic attributes, only the ones that do will
    see those attributes being set with synthetic data.
    """

    def __init__(
        self,
        config_path: Path,
        network_repository: DatabaseNetworkRepository,
        network_builder: NetworkBuilder,
    ) -> None:
        self.config_path = config_path
        self.config = Config.from_yaml(path=config_path)
        self._elements = network_repository.get_elements(
            network_id=self.config.network_id,
        )
        self.network_repository = network_repository
        self.network_builder = network_builder

    def apply_pipeline(
        self,
        start: str,
        end: str,
        time_step: int,
    ) -> Network:
        """
        Apply simulation pipeline. NetworkElement s for which a dynamic state is supported will
        get synthetic values for their dynamic attributes.

        Params:
        - start (str): The starting timestamp for sinumation (format '2024-01-02T00:00:00+0000')
        - end (str): The ending timestamp for sinumation (format '2024-01-02T00:00:00+0000')
        - time_step (int): Timestep in hour. TODO: Get rid of this

        Returns:
            None: The simulated Network is added to repo.
        """

        start_dt = parse_datetime(start, format=DATETIME_FORMAT, tz=DEFAULT_TIMEZONE)
        end_dt = parse_datetime(end, format=DATETIME_FORMAT, tz=DEFAULT_TIMEZONE)
        timestamps = [
            start_dt + timedelta(hours=i)
            for i in range(
                0, int((end_dt - start_dt).total_seconds() / 3600), time_step
            )
        ]

        elements = []

        for element in self._elements:
            if element.element_metadata.state != State.STATIC:
                raise ValueError(
                    f"Element must be static. Element {element.id} is {element.element_metadata.state}."
                )

            is_dynamic_supported = (
                True
                if State.DYNAMIC in element.element_metadata.supported_states
                else False
            )

            # Generate simulated metadata from element
            if is_dynamic_supported:
                if element.id not in [i.id for i in self.config.elements]:
                    raise ValueError(
                        f"{element.id} from network does not have a ts_gen config associated in {self.config_path}"
                    )
                # No duplicates comes from validation on config model
                element_config = next(
                    (i for i in self.config.elements if i.id == element.id)
                )

                initialised_generators = {
                    param: [
                        getattr(sim, step.name)(**step.parameters)
                        for step in param_config.steps
                    ]
                    for param, param_config in element_config.parameters.items()
                }

                simulated_data = {
                    param: reduce(
                        lambda array, generator: generator.generate(array),
                        initialised_generators[param],
                        np.zeros(len(timestamps)),
                    )
                    for param in initialised_generators.keys()
                }

            # Update for each ts the element if new metadata is available, else repeat with new ts
            for idx, ts in enumerate(timestamps):
                # Update constraint uid based on new ts
                constraints_updated = (
                    [
                        OperationalConstraint.from_element(
                            element_id=element.id,
                            timestamp=ts,
                            element_type=element.type,
                            side=c.get("side"),
                            name=c.get("name"),
                            type=c.get("type"),
                            value=c.get("value"),
                            acceptable_duration=c.get("acceptable_duration"),
                        )
                        for c in [
                            i.model_dump() for i in element.operational_constraints
                        ]
                    ]
                    if element.operational_constraints
                    else []
                )

                # Prepare simualated data
                if is_dynamic_supported:
                    element_metadata: dict = (
                        element.model_dump().get("element_metadata", {}).copy()
                    )

                    element_metadata["state"] = State.DYNAMIC
                    element_metadata["dynamic"] = {}

                    for param, data in simulated_data.items():
                        element_metadata["dynamic"][param] = float(round(data[idx], 2))

                    element_metadata_parsed = MetadataRegistry[element.type](
                        **element_metadata
                    )
                else:
                    element_metadata_parsed = element.element_metadata

                simulated_element = NetworkElement.from_metadata(
                    id=element.id,
                    timestamp=ts,
                    type=element.type,
                    element_metadata=element_metadata_parsed,
                    network_id=f"{self.config.network_id}_simulated",
                    operational_constraints=constraints_updated,
                )
                elements.append(simulated_element)

        network = self.network_builder.from_elements(
            id=f"{self.config.network_id}_simulated",
            elements=elements,
        )

        self.network_repository.add(network=network)
