from datetime import datetime
from src.rl.observation.network_snapshot_observation_builder import (
    NetworkSnapshotObservationBuilder,
)
from src.core.domain.models.network import Network
from src.core.constants import SupportedNetworkElementTypes
from src.rl.observation.line import LineObservationWithOutage
from src.rl.observation.generator import GeneratorObservation
from src.rl.observation.load import LoadObservation
from src.rl.observation.network import NetworkSnapshotObservation
from src.rl.outage.outage_handler import OutageHandler


class WithOutageNetworkSnapshotObservationBuilder(NetworkSnapshotObservationBuilder):
    @staticmethod
    def from_network(
        network: Network,
        outage_handler: OutageHandler,
        timestamp: datetime,
    ) -> NetworkSnapshotObservation:
        """
        Loop through elements in the network to get a BaseElementObservation per element.
        """
        observations = []
        for element in sorted(network.elements, key=lambda e: e.id):
            if element.type == SupportedNetworkElementTypes.LINE:
                observations.append(
                    LineObservationWithOutage.from_element(
                        element,
                        outage_probability=outage_handler.get_network_element_outage_handler(
                            element_id=element.id
                        ).outage_prob,
                    )
                )
            elif element.type == SupportedNetworkElementTypes.LOAD:
                observations.append(LoadObservation.from_element(element))
            elif element.type == SupportedNetworkElementTypes.GENERATOR:
                observations.append(GeneratorObservation.from_element(element))
        return NetworkSnapshotObservation(
            observations=observations, timestamp=timestamp
        )
