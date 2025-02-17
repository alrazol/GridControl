from datetime import datetime
from src.rl.observation.network_snapshot_observation_builder import (
    NetworkSnapshotObservationBuilder,
)
from src.core.domain.models.network import Network
from src.core.constants import SupportedNetworkElementTypes
from src.rl.observation.line import LineObservation
from src.rl.observation.generator import GeneratorObservation
from src.rl.observation.load import LoadObservation
from src.rl.observation.network import NetworkSnapshotObservation


class DefaultNetworkSnapshotObservationBuilder(NetworkSnapshotObservationBuilder):
    @staticmethod
    def from_network(
        network: Network,
        timestamp: datetime,
    ) -> NetworkSnapshotObservation:
        """
        Loop through elements in the network to get a BaseElementObservation per element.
        """
        observations = []
        for element in sorted(network.elements, key=lambda e: e.id):
            if element.type == SupportedNetworkElementTypes.LINE:
                observations.append(LineObservation.from_element(element))
            elif element.type == SupportedNetworkElementTypes.LOAD:
                observations.append(LoadObservation.from_element(element))
            elif element.type == SupportedNetworkElementTypes.GENERATOR:
                observations.append(GeneratorObservation.from_element(element))
        return NetworkSnapshotObservation(
            observations=observations, timestamp=timestamp
        )
