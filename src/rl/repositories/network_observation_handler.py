from src.rl.observation.network_observation_handler import NetworkObservationHandler
from src.rl.observation.network import NetworkObservation, NetworkSnapshotObservation


class DefaultNetworkObservationHandler(NetworkObservationHandler):
    @staticmethod
    def init_network_observation(
        history_length: int,
        network_snapshot_observations: tuple[NetworkSnapshotObservation, ...] = (),
    ) -> NetworkObservation:
        """
        Initialize a new NetworkObservation instance.
        """
        return NetworkObservation(
            history_length=history_length,
            network_snapshot_observations=network_snapshot_observations,
        )

    @staticmethod
    def add_network_snapshot_observation(
        network_observation: NetworkObservation,
        network_snapshot_observation: NetworkSnapshotObservation,
    ) -> NetworkObservation:
        """
        Add to the history, removing the oldest observation if it's full.
        """
        new_obs = NetworkObservation(
            network_observation.history_length,
            (
                network_observation.network_snapshot_observations
                + (network_snapshot_observation,)
            )[-network_observation.history_length :],
        )
        del network_observation
        return new_obs
