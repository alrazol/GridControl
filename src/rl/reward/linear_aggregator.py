from src.rl.reward.base import BaseReward
from src.rl.observation.network import NetworkSnapshotObservation


class LinearRewardAggregator:
    def __init__(self, rewards: list[BaseReward], weights: list[float] = None) -> None:
        """
        Initialize the RewardHandler with a list of rewards and their respective weights.

        Params:
        - rewards (List[BaseReward]): List of reward components.
        - weights (List[float]): Weights for each reward component. Defaults to equal weights.
        """
        self.rewards = rewards
        self.weights = weights if weights else [1.0] * len(rewards)
        assert len(self.rewards) == len(
            self.weights
        ), "Rewards and weights must match in length."

    def compute_reward(
        self, network_snapshot_observation: NetworkSnapshotObservation
    ) -> float:
        """
        Compute the total reward as a weighted sum of individual rewards.

        Params:
        - network_state (NetworkState): The current state of the network.

        Returns:
            float: The total computed reward.
        """
        total_reward = 0.0
        for reward, weight in zip(self.rewards, self.weights):
            total_reward += weight * reward.compute_reward(
                next_snapshot_observation=network_snapshot_observation,
            )
        return total_reward
