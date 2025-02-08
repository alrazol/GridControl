import pypowsybl as pp
from pypowsybl.network import Network as PypowsyblNetwork
from typing import Literal
from src.core.domain.models.network import Network
#from src.core.infrastructure.services.converters.pypowsybl_methods.network import network_from_pypowsybl


class ImportBenchmarkNetworkFromPyPowsyblPipeline:
    """
    This pipeline allows to load from Pypowsybl some benchmark networks.
    """

    def __init__(self, network_name: Literal["ieee14"]) -> None:
        self.network_name = network_name

    def extract(self) -> PypowsyblNetwork:
        """Load the network."""
        return pp.network.create_ieee14()

    def transform(network: PypowsyblNetwork) -> Network:
        """Turn the PyPowsybl network into a Network."""
        return network
