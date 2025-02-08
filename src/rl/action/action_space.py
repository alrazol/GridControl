import numpy as np
from gym.spaces import Discrete, Box, Dict
from typing import Self
from src.core.domain.models.network import Network
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
        network: Network,
        valid_actions: list[BaseAction],
        invalid_actions: list[BaseAction],
    ) -> None:
        self.network = network
        self.valid_actions = valid_actions
        self.invalid_actions = invalid_actions

    @classmethod
    def from_actions(cls, actions: list[BaseAction], network: Network) -> Self:
        """Build an ActionSpace instance from a list of BaseActions."""

        if len(set(actions)) != len(actions):
            raise ValueError("Some actions in the list are duplicated.")

        if len(set([i.timestamp for i in network.elements])) > 1:
            raise ValueError("Can't have more than one timestamp for an ActionSpace.")

        valid_actions = []
        invalid_actions = []

        for action in actions:
            try:
                action.validate(network=network)
                valid_actions.append(action)
            except ValueError as _:
                invalid_actions.append(action)

        return cls(
            network=network,
            valid_actions=valid_actions,
            invalid_actions=invalid_actions,
        )

    def to_gym(self):
        """Creates a flexible Gym-compatible action space for the valid actions."""
        discrete_actions = [
            action for action in self.valid_actions if action.is_discrete
        ]
        continuous_actions = [
            action for action in self.valid_actions if not action.is_discrete
        ]

        if discrete_actions and not continuous_actions:
            # All actions are discrete
            return Discrete(n=len(discrete_actions))
        elif continuous_actions and not discrete_actions:
            # All actions are continuous, use Box
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
            # Mixed discrete and continuous, use Dict
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
