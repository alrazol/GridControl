import numpy as np
from gym.spaces import Discrete, Box, Dict
from src.rl.action.base import BaseAction


class ActionSpace:
    """
    This class represents a custom action space. It is used to expose
    the valid actions a BaseAgent can take on a given Network. In order
    to filter valid and invalid actions, the network is expected at init.
    In some cases, the action space is independent of the timestamp of the
    network, in this case, it is recommended to build it from the initial
    network.

    The ActionSpace class deals with converting to a gym action_space.
    """

    def __init__(
        self,
        valid_actions: list[BaseAction],
        invalid_actions: list[BaseAction],
    ) -> None:
        self.valid_actions = valid_actions
        self.invalid_actions = invalid_actions

    def to_gym(self):
        """
        Convert the ActionSpace to a gym.Space.
        """
        discrete_actions = [
            action for action in self.valid_actions if action.is_discrete
        ]
        continuous_actions = [
            action for action in self.valid_actions if not action.is_discrete
        ]

        if discrete_actions and not continuous_actions:
            return Discrete(n=len(discrete_actions))

        elif continuous_actions and not discrete_actions:
            param_shapes = [
                len(action.parameters)
                for action in continuous_actions
                if action.parameters
            ]
            max_params = max(param_shapes, default=1)
            return Box(
                low=-np.inf, high=np.inf, shape=(len(continuous_actions), max_params)
            )
        elif discrete_actions and continuous_actions:
            return Dict(
                {
                    "discrete": Discrete(len(discrete_actions)),
                    "continuous": Box(
                        low=-np.inf,
                        high=np.inf,
                        shape=(
                            len(continuous_actions),
                            len(continuous_actions[0].parameters),
                        ),
                    ),
                }
            )
        else:
            raise ValueError("No valid actions available to create a Gym space.")
