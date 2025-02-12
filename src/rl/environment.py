import gym
import copy
from gym.spaces import Space
from datetime import datetime
from typing import Self
from src.core.domain.ports import LoadFlowSolver
from src.rl.repositories.network_repository import NetworkRepository
from src.core.constants import LoadFlowType
from src.core.domain.models.network import Network
from src.rl.observation.network import NetworkObservation, NetworkSnapshotObservation
from src.core.utils import parse_datetime, parse_datetime_to_str
from src.core.constants import DATETIME_FORMAT, DEFAULT_TIMEZONE
from src.rl.action.base import BaseAction
from src.rl.reward.base import BaseReward
from src.rl.action_space import ActionSpace
from src.rl.one_hot_map import OneHotMap
from src.core.constants import SupportedNetworkElementTypes


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
        initial_dynamic_network: Network,
        loadflow_solver: LoadFlowSolver,
        loadflow_type: LoadFlowType,
        action_space: ActionSpace,
        observation_space: Space,
        one_hot_map: OneHotMap,
        reward_handler: BaseReward,
    ) -> None:
        self.network = network
        self.initial_observation = initial_observation
        self.initial_dynamic_network = initial_dynamic_network
        self.loadflow_solver = loadflow_solver
        self.loadflow_type = loadflow_type
        self.action_space = action_space
        self.observation_space = observation_space
        self.one_hot_map = one_hot_map
        self.reward_handler = reward_handler

    @property
    def current_timestamp(self):
        return self._current_timestamp

    @current_timestamp.setter
    def current_timestamp(self, value: datetime):
        self._current_timestamp = value

    @property
    def current_observation(self):
        return self._current_observation

    @current_observation.setter
    def current_observation(self, value: NetworkObservation):
        self._current_observation = value

    @property
    def current_dynamic_network(self):
        return self._current_dynamic_network

    @current_dynamic_network.setter
    def current_dynamic_network(self, value: Network):
        self._current_dynamic_network = value

    @property
    def last_taken_action(self):
        return self._last_taken_action

    @last_taken_action.setter
    def last_taken_action(self, value: BaseAction):
        self._last_taken_action = value

    @property
    def episode_reward(self):
        return self._episode_reward

    @episode_reward.setter
    def episode_reward(self, value):
        self._episode_reward = value

    @property
    def is_terminated(self):
        return self._is_terminated

    @is_terminated.setter
    def is_terminated(self, value):
        self._is_terminated = value

    def reset(self) -> tuple[NetworkObservation, dict]:
        """
        Reset the env to its initial state.
        """

        self.current_timestamp = (
            self.initial_observation.list_network_snapshot_observations()[0].timestamp
        )
        self.current_observation = self.initial_observation
        self.current_dynamic_network = self.initial_dynamic_network
        self.is_terminated = False
        self.episode_reward = 0.0

        return self.initial_observation, {}

    def step(self, action: BaseAction) -> tuple[NetworkObservation, float, bool, dict]:
        """
        Rollout one step of the environment.
        """

        # 1) Get the network for next timestamp.
        all_timestamps = self.network.list_timestamps()

        # TODO: Compute those and access them as properties here.
        # TODO: Have those as current timestamp and next timestamp properties.
        current_str_timestamp = parse_datetime_to_str(
            d=self.current_observation.list_network_snapshot_observations()[
                -1
            ].timestamp,
        )
        current_str_timestamp_index = all_timestamps.index(current_str_timestamp)

        next_datetime_timestamp = parse_datetime(
            all_timestamps[current_str_timestamp_index + 1]
        )

        next_timestamp_elements_copy = copy.deepcopy(
            self.network.list_elements(timestamp=next_datetime_timestamp)
        )
        current_network_copy = copy.deepcopy(self.current_dynamic_network)

        next_network = Network.from_elements(
            id="tmp_id",
            elements=next_timestamp_elements_copy,
        )

        # Take action on past network + update dynamic attributes
        # TODO: Isolate in methods to be able to test.
        next_network_updated = action.execute(current_network_copy)
        for element in next_network_updated.elements:
            element.timestamp = parse_datetime_to_str(d=next_datetime_timestamp)
            if element.type in [
                SupportedNetworkElementTypes.GENERATOR,
                SupportedNetworkElementTypes.LOAD,
            ]:
                element.element_metadata.dynamic = next_network.get_element(
                    id=element.id, timestamp=next_datetime_timestamp
                ).element_metadata.dynamic

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

        self.current_dynamic_network = next_network_updated
        next_observation_history = self.current_observation.update(next_observation)
        self.current_observation = next_observation_history
        self.last_taken_action = action

        # 4) Check if terminated
        if (
            all_timestamps[current_str_timestamp_index + 1]
            == list(reversed(self.network.list_timestamps()))[0]
        ):
            self.is_terminated = True

        return (
            next_observation_history,
            reward,
            self.is_terminated,
            {},
        )


def make_env(
    network_id: str,
    network_repository: NetworkRepository,
    loadflow_solver: LoadFlowSolver,
    loadflow_type: LoadFlowType,
    reward_handler: BaseReward,
    action_types: list[str],
    observation_memory_length: int,
) -> Self:
    # 1) Fetch the network and build initial observation
    network = network_repository.get(network_id=network_id)
    initial_network = network.get_timestamp_network(
        timestamp=network.list_timestamps()[0],
    )
    initial_network_snapshot_observation = NetworkSnapshotObservation.from_network(
        network=loadflow_solver.solve(
            network=initial_network, loadflow_type=loadflow_type
        ),
        timestamp=network.list_timestamps()[0],
    )

    # 2) Build the action space.
    action_space = ActionSpace.from_action_types(
        action_types=action_types,
        network=initial_network,
    )

    # 3) Build the observation space, assumed unique across timestamps.
    one_hot_map = OneHotMap.from_network_observation(
        network_observation=initial_network_snapshot_observation
    )
    initial_observation = NetworkObservation(
        history_length=observation_memory_length,
    ).add_network_snapshot_observation(initial_network_snapshot_observation)
    observation_space = initial_observation.to_observation_space(
        one_hot_map=one_hot_map
    )

    return NetworkEnvironment(
        network=network,
        initial_observation=initial_observation,
        initial_dynamic_network=initial_network,
        loadflow_solver=loadflow_solver,
        loadflow_type=loadflow_type,
        action_space=action_space,
        observation_space=observation_space,
        one_hot_map=one_hot_map,
        reward_handler=reward_handler,
    )
