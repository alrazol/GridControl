import pypowsybl as pp
from src.core.constants import LoadFlowType
from src.core.domain.models.network import Network
from typing import Any
from src.core.infrastructure.services import PyPowsyblCompatService
from src.core.domain.ports.visualiser import Visualiser


class PyPowSyblVisualiserRepository(Visualiser):  # TODO: Finish the single line diagram visualisation.
    """This will gather methods, relying on PyPowSybl, to visualise a 'Network'."""

    def __init__(self, to_pypowsybl_converter_service: PyPowsyblCompatService) -> None:
        self.to_pypowsybl_converter_service = to_pypowsybl_converter_service

    def get_single_line_diagram_per_voltage_level(
        self,
        network: Network,
        timestamp: str,
        loadflow_type: LoadFlowType | None = None,
    ) -> dict[str, Any]:
        """Returns a dict with the each voltage level as keys and associated image as values."""
        pypowsybl_network = self.to_pypowsybl_converter_service.network_to_pypowsybl(
            network=network
        ).get_active_network()[timestamp]
        if loadflow_type is not None:
            if loadflow_type == LoadFlowType.AC:
                _ = pp.loadflow.run_ac(network=pypowsybl_network)
            elif loadflow_type == LoadFlowType.DC:
                _ = pp.loadflow.run_dc(network=pypowsybl_network)
        return {
            f"{voltage_level}": pypowsybl_network.get_single_line_diagram(
                container_id=voltage_level
            )
            for voltage_level in set(pypowsybl_network.get_voltage_levels().index)
        }
