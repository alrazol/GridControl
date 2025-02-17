import src.rl.reward as reward_module
from src.rl.reward.base import BaseReward
from src.rl.reward.reward_handler import RewardHandler


class DefaultRewardHandler(RewardHandler):
    def __init__(self, aggregator_name: str, rewards: list[str]) -> None:
        super().__init__(aggregator_name=aggregator_name, rewards=rewards)

    def build_reward(self) -> BaseReward:  # TODO: Type as a base aggregator
        reward_aggegator = getattr(reward_module, self.aggregator_name)
        return reward_aggegator(
            rewards=[getattr(reward_module, i) for i in self.rewards]
        )
