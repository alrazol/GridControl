from src.core.utils import parse_datetime
from src.core.domain.models.network import Network
from src.core.domain.models.element import NetworkElement
import pypowsybl as pp
import pandas as pd

from src.core.constants import SupportedNetworkElementTypes
from src.core.domain.enums import LoadFlowType
from src.core.infrastructure.services import PyPowsyblCompatService
from src.core.constants import DATETIME_FORMAT, DEFAULT_TIMEZONE
from src.core.domain.ports.loadflow_solver import LoadFlowSolver


class PyPowSyblLoadFlowSolver(LoadFlowSolver):
    """Pypowsybl implementation of a loadflow solver"""

    def __init__(self, to_pypowsybl_converter_service: PyPowsyblCompatService) -> None:
        self.to_pypowsybl_converter_service = to_pypowsybl_converter_service

    def solve(
        self, network: Network, loadflow_type: LoadFlowType
    ) -> Network:  # TODO: Better manage cases where the loadflow does not converge.
        """This takes an obj 'Network', formats to a Pypowsybl network, queries the loadflow solver for a response and format back to 'Network'."""
        pypowsybl_network_wrapper = (
            self.to_pypowsybl_converter_service.network_to_pypowsybl(network=network)
        )

        pypowsybl_network = pypowsybl_network_wrapper.get_active_network()

        loadflow_func = (
            pp.loadflow.run_dc
            if loadflow_type == LoadFlowType.DC
            else pp.loadflow.run_ac
        )
        elements = []
        for timestamp in pypowsybl_network:
            loadflow_func(pypowsybl_network[timestamp])

            # TODO: Make more generic
            # voltage_levels = pypowsybl_network[timestamp].get_voltage_levels()
            # buses = pypowsybl_network[timestamp].get_buses()
            loads = pypowsybl_network[timestamp].get_loads()
            lines = pypowsybl_network[timestamp].get_lines()
            generators = pypowsybl_network[timestamp].get_generators()

            # Helper function to process the elements
            def process_elements(
                elements: pd.DataFrame,
                element_type: SupportedNetworkElementTypes,
                network_id: str,
            ) -> list[NetworkElement]:
                return [
                    self.to_pypowsybl_converter_service.element_from_pypowsybl(
                        element_id=i,
                        element_type=element_type,
                        network_id=network_id,
                        timestamp=parse_datetime(
                            timestamp, format=DATETIME_FORMAT, tz=DEFAULT_TIMEZONE
                        ),
                        element_metadata_pypowsybl=row,
                        operational_constraints=[],  # Will be updated later in pipeline
                    )
                    for i, row in elements.iterrows()
                ]

            # Process loads, lines, and generators
            solved_loads = process_elements(
                elements=loads,
                element_type=SupportedNetworkElementTypes.LOAD,
                network_id=network.id,
            )
            solved_lines = process_elements(
                elements=lines,
                element_type=SupportedNetworkElementTypes.LINE,
                network_id=network.id,
            )
            solved_generators = process_elements(
                elements=generators,
                element_type=SupportedNetworkElementTypes.GENERATOR,
                network_id=network.id,
            )

            for element in solved_generators + solved_lines + solved_loads:
                # Retrieve the constraints for element
                for n in network.elements:
                    if n.timestamp == timestamp and n.id == element.id:
                        constraint_data = []
                        for constraint in n.operational_constraints:
                            constraint_data.append(constraint)

                elements.append(
                    NetworkElement.from_metadata(
                        id=element.id,
                        timestamp=parse_datetime(
                            timestamp, format=DATETIME_FORMAT, tz=DEFAULT_TIMEZONE
                        ),
                        element_metadata=element.element_metadata,
                        type=element.type,
                        network_id=network.id,
                        operational_constraints=constraint_data,
                    )
                )

            for element in pypowsybl_network_wrapper.data[
                parse_datetime(d=timestamp, format=DATETIME_FORMAT, tz=DEFAULT_TIMEZONE)
            ][1]:
                elements.append(element)

        return Network.from_elements(
            id=network.id,
            elements=elements,
        )
