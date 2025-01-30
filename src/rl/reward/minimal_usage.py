from src.core.constants import ElementStatus
from src.rl.reward.base import BaseReward
from src.rl.observation.network import NetworkObservation


class MinimalUsageReward(BaseReward):
    """
    This class is used to build reward from saving some NetworkElement from
    being used at a timestamp. The greater the difference btw num_elements
    and num_elements_on at a timestamp, the greater the reward.
    """

    @staticmethod
    def compute_reward(network_observation: NetworkObservation) -> float:
        """
        Params:
        - network_observation (NetworkObservation): The network observed.
        Returns:
            float: The reward
        """
        num_elements = len(network_observation.observations)
        num_elements_used = len(
            [
                i
                for i in network_observation.observations
                if i.status == ElementStatus.ON
            ]
        )
        return float(num_elements - num_elements_used)**2
