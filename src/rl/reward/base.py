from abc import ABC, abstractmethod
from src.rl.observation.network import NetworkSnapshotObservation


class BaseReward(ABC):
    """
    Base class for rewards.

    NOTE: In theory - rewards should be computed on states, while
    the agent acts on observations, here the agent observes the state.
    """

    @staticmethod
    @abstractmethod
    def compute_reward(
        network_snapshot_observation: NetworkSnapshotObservation,
    ) -> float:
        pass
