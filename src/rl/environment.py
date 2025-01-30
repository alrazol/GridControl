import gym
from gym.spaces import Space
from typing import Self
from src.rl.action.do_nothing import DoNothingAction
from src.core.domain.ports import LoadFlowSolver
from src.rl.repositories.network_repository import NetworkRepository
from src.core.constants import LoadFlowType
from src.core.domain.models.network import Network
from src.rl.observation.network import NetworkObservation
from src.core.utils import parse_datetime, parse_datetime_to_str
from src.core.constants import DATETIME_FORMAT, DEFAULT_TIMEZONE
from src.rl.action.base import BaseAction
from src.rl.reward.base import BaseReward
from src.rl.action.action_space import ActionSpace
import src.rl.action as action
from src.rl.action.enums import DiscreteActionTypes
from src.rl.observation.one_hot_map import OneHotMap


class NetworkEnvironment(gym.Env):
    """
    This class encapsulates the environment in which agents will be trained.
    It simulates the behaviour of a power grid, using external solver and
    fetching the initial network from external repository.
    """

    def __init__(
        self,
        network: Network,
        initial_observation: NetworkObservation,
        loadflow_solver: LoadFlowSolver,
        loadflow_type: LoadFlowType,
        action_space: ActionSpace,
        observation_space: Space,
        one_hot_map: OneHotMap,
        reward_handler: BaseReward,
    ) -> None:
        self.network = network
        self.initial_observation = initial_observation
        self.loadflow_solver = loadflow_solver
        self.loadflow_type = loadflow_type
        self.action_space = action_space
        self.observation_space = observation_space
        self.one_hot_map = one_hot_map
        self.reward_handler = reward_handler

    @property
    def current_observation(self):
        """Getter for the current step."""
        return self._current_observation

    @current_observation.setter
    def current_observation(self, value):
        """Setter for the current step with validation."""
        self._current_observation = value

    @property
    def last_taken_action(self):
        """Getter for the last action taken."""
        return self._last_taken_action

    @last_taken_action.setter
    def last_taken_action(self, value: BaseAction):
        """Setter for the current step with validation."""
        self._last_taken_action = value

    @property
    def episode_reward(self):
        """Getter for the episode reward."""
        return self._episode_reward

    @episode_reward.setter
    def episode_reward(self, value):
        """Setter for the current step with validation."""
        self._episode_reward = value

    @property
    def is_terminated(self):
        """Getter for the termination flag."""
        return self._is_terminated

    @is_terminated.setter
    def is_terminated(self, value):
        """Setter for the termination flag."""
        self._is_terminated = value

    @classmethod
    def from_network_id(
        cls,
        network_id: str,
        network_repository: NetworkRepository,  # This can be an API from core
        loadflow_solver: LoadFlowSolver,  # This can be an API from core
        loadflow_type: LoadFlowType,  # This can be duplicated
        reward_handler: BaseReward,  # This is internal
        action_types: list[str],
    ) -> Self:
        network = network_repository.get(network_id=network_id)
        initial_timestamp_str = network.list_timestamps()[0]
        initial_timestamp = parse_datetime(
            d=initial_timestamp_str, format=DATETIME_FORMAT, tz=DEFAULT_TIMEZONE
        )
        # We assume that the action_space at 1st timestamp is the same going forward
        initial_network = Network.from_elements(
            id=f"{network.id}_{initial_timestamp_str}",
            elements=network.list_elements(timestamp=initial_timestamp),
        )
        initial_network_solved = loadflow_solver.solve(
            network=initial_network, loadflow_type=loadflow_type
        )

        initial_observation = NetworkObservation.from_network(
            network=initial_network_solved,
            timestamp=initial_timestamp,
        )

        # Based on initial Network, init all (regardless of valid) actions.
        all_actions = []
        if DiscreteActionTypes.DO_NOTHING in action_types:
            all_actions.append(DoNothingAction())
        for element in initial_network.list_elements(timestamp=initial_timestamp):
            for i in action_types:
                if i == DiscreteActionTypes.DO_NOTHING:
                    continue
                try:
                    # Check for each type of action if it could affect each element given the network.
                    # Assumption, all actions affect an element and are either valid or not.
                    # This logic could be moved to each state timestep and used for caching in case.
                    res = getattr(action, i).from_network(element.id, initial_network)
                    all_actions.append(res)
                except ValueError:  # TODO: Be more precise here.
                    continue

        action_space = ActionSpace.from_actions(  # Doubling the logic here.
            actions=all_actions, network=initial_network
        )

        # Based on initial observation, compute the OneHotMap that will be used all the way.
        one_hot_map = OneHotMap.from_network_observation(
            network_observation=initial_observation
        )

        return cls(
            network=network,
            initial_observation=initial_observation,
            loadflow_solver=loadflow_solver,
            loadflow_type=loadflow_type,
            action_space=action_space,
            observation_space=initial_observation.to_observation_space(
                one_hot_map=one_hot_map
            ),
            one_hot_map=one_hot_map,
            reward_handler=reward_handler,
        )

    def reset(self) -> tuple[NetworkObservation, dict]:
        """Reset the env to its initial state."""

        self.current_observation = self.initial_observation
        self.is_terminated = False
        self.episode_reward = 0.0

        return self.initial_observation, {}

    def step(self, action: BaseAction) -> tuple[NetworkObservation, float, bool, dict]:
        """Applies an action to the network. Pass an initialised action as action."""

        # 1) Get the network for next timestamp.
        all_timestamps = self.network.list_timestamps()
        current_str_timestamp = parse_datetime_to_str(
            d=self.current_observation.timestamp,
            format=DATETIME_FORMAT,
            tz=DEFAULT_TIMEZONE,
        )
        current_str_timestamp_index = all_timestamps.index(current_str_timestamp)

        next_datetime_timestamp = parse_datetime(
            all_timestamps[current_str_timestamp_index + 1],
            format=DATETIME_FORMAT,
            tz=DEFAULT_TIMEZONE,
        )

        next_network = Network.from_elements(
            id="tmp_id",
            elements=self.network.list_elements(timestamp=next_datetime_timestamp),
        )

        # 2) Apply both previous action and new action to the next network retireved.
        # if hasattr(self, "last_taken_action") and self.last_taken_action is not None:
        #    next_network_updated = action.execute(
        #        network=self.last_taken_action.execute(next_network)
        #    )
        # else:
        next_network_updated = action.execute(next_network)

        next_observation = NetworkObservation.from_network(
            network=self.loadflow_solver.solve(
                network=next_network_updated, loadflow_type=self.loadflow_type
            ),
            timestamp=parse_datetime(
                next_network_updated.elements[0].timestamp,
                format=DATETIME_FORMAT,
                tz=DEFAULT_TIMEZONE,
            ),
        )

        # 3) Compute reward on this new state
        reward = self.reward_handler.compute_reward(
            network_observation=next_observation
        )

        next_observation_no_action = NetworkObservation.from_network(
            network=self.loadflow_solver.solve(
                network=next_network, loadflow_type=self.loadflow_type
            ),
            timestamp=parse_datetime(
                next_network.elements[0].timestamp,
                format=DATETIME_FORMAT,
                tz=DEFAULT_TIMEZONE,
            ),
        )

        self.current_observation = next_observation
        self.last_taken_action = action

        # 4) Check if terminated
        if current_str_timestamp == list(reversed(self.network.list_timestamps()))[0]:
            self.is_terminated = True

        return (
            next_observation_no_action,
            reward,
            self.is_terminated,
            {},
        )
