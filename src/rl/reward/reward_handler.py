from abc import ABC, abstractmethod
from src.rl.reward.base import BaseReward


class RewardHandler(ABC):
    def __init__(self, aggregator_name: str, rewards: list[str]) -> None:
        self.aggregator_name = aggregator_name
        self.rewards = rewards

    @abstractmethod
    def build_reward(self) -> BaseReward:
        pass
