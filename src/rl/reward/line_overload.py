from src.rl.reward.base import BaseReward
from src.rl.observation.network import NetworkObservation
from src.core.domain.enums import OperationalConstraintType, BranchSide
from src.core.constants import ElementStatus


class LineOverloadReward(BaseReward):
    """
    This class is used to compute a reward based on line overloading.
    Lines affected by active power operational contraints for which the
    observed active power is > than the limit will generate negative reward.
    """

    @property
    def is_upper_bounded(self):
        return True

    @staticmethod
    def compute_reward(network_observation: NetworkObservation) -> float:
        """
        For now, only considering active power and constraints of type 'TWO'.

        Params:
        - network_observation (NetworkObservation): The network observed.
        Returns:
            float: The reward
        """

        total_reward = 0.0
        for observation in network_observation.observations:
            if hasattr(observation, "operational_constraints"):
                if len(observation.operational_constraints) == 0:
                    continue
                for constraint in observation.operational_constraints:
                    if (
                        constraint.get("type") == OperationalConstraintType.ACTIVE_POWER
                        and constraint.get("side") == BranchSide.TWO
                    ):
                        if observation.status == ElementStatus.ON:
                            limit = constraint.get("value")
                            if (
                                abs(observation.p1) > limit
                                or abs(observation.p2) > limit
                            ):
                                total_reward -= 5

        return total_reward
