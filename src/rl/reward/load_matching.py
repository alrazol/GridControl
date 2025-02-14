from src.rl.observation.network import NetworkSnapshotObservation
from src.rl.reward.base import BaseReward
from src.rl.observation.load import LoadObservation


class LoadMatchingReward(BaseReward):
    """
    This class is used to compute the reward from matching the load
    active power to the load target power at a timestamp. Ensuring
    loads are provided what they need.
    """

    @property
    def is_upper_bounded(self):
        return True

    @staticmethod
    def compute_reward(
        network_snapshot_observation: NetworkSnapshotObservation,
    ) -> float:
        """
        Params:
        - network_observation (NetworkObservation): The network observed.
        Returns:
            float: The reward
        """
        total_reward = 0.0
        for observation in network_snapshot_observation.observations:
            if isinstance(observation, LoadObservation):
                total_reward -= observation.uncovered_load
        return total_reward
