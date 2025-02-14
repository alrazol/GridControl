from src.rl.observation.network_observation_handler import NetworkObservationHandler
from src.rl.observation.network import NetworkObservation, NetworkSnapshotObservation


class DefaultNetworkObservationHandler(NetworkObservationHandler):
    @staticmethod
    def add_network_snapshot_observation(
        network_observation: NetworkObservation,
        network_snapshot_observation: NetworkSnapshotObservation,
    ) -> NetworkSnapshotObservation:
        """
        Add to the history, removing the oldest observation if it's full.
        """
        return NetworkObservation(
            network_observation.history_length,
            (
                network_observation.network_snapshot_observations
                + (network_snapshot_observation,)
            )[-network_observation.history_length :],
        )
