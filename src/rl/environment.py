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
        initial_network: Network,
        loadflow_solver: LoadFlowSolver,
        loadflow_type: LoadFlowType,
        action_space: ActionSpace,
        observation_space: Space,
        one_hot_map: OneHotMap,
        reward_handler: BaseReward,
    ) -> None:
        self.network = network
        self.initial_observation = initial_observation
        self.initial_network = initial_network
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
    def current_network(self):
        return self._current_network

    @current_network.setter
    def current_network(self, value: Network):
        self._current_network = value

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
        self.current_network = self.initial_network
        self.is_terminated = False
        self.episode_reward = 0.0

        return self.initial_observation, {}

    def step(self, action: BaseAction) -> tuple[NetworkObservation, float, bool, dict]:
        """
        Rollout one step of the environment.
        """

        def _build_next_network(
            current_network: Network,
            next_network_no_action: Network,
            action: BaseAction,
        ) -> Network:
            """
            Build next Network by inplacing dynamic attributes of elements, and applying action.
            """
            out = action.execute(current_network)
            next_timestamp = next_network_no_action.elements[0].timestamp
            for element in out.elements:
                element.timestamp = next_timestamp
                if element.type in [
                    SupportedNetworkElementTypes.GENERATOR,
                    SupportedNetworkElementTypes.LOAD,
                ]:
                    element.element_metadata.dynamic = (
                        next_network_no_action.get_element(
                            id=element.id, timestamp=next_timestamp
                        ).element_metadata.dynamic
                    )
            return out

        # 1) Fetch next timesamp's Network.
        all_timestamps = self.network.list_timestamps()
        if not hasattr(self, "current_timestamp"):
            raise ValueError("You need to reset the environment before taking actions.")

        next_network = Network.from_elements(
            id="tmp",
            elements=self.network.list_elements(
                timestamp=all_timestamps[
                    all_timestamps.index(self.current_timestamp) + 1
                ]
            ),
        )

        # 2) Update current network with the action & inplace dynamic attrs with next timestamp's values.
        next_network_with_action = _build_next_network(
            current_network=self.current_network,
            next_network_no_action=next_network,
            action=action,
        )

        # 3) Observation comes from solving the next_network_with_action.
        next_observation_snapshot = NetworkSnapshotObservation.from_network(
            network=self.loadflow_solver.solve(
                network=next_network_with_action,
                loadflow_type=self.loadflow_type,
            ),
            timestamp=next_network_with_action.list_timestamps()[0],
        )

        # 4) Compute reward on next NetworkObservationSnapshot.
        reward = self.reward_handler.compute_reward(
            network_observation=next_observation_snapshot,
        )

        # 5) Update attrs.
        self.current_network = next_network_with_action
        self.current_observation = (
            self.current_observation.add_network_snapshot_observation(
                next_observation_snapshot
            )
        )

        if (
            all_timestamps[all_timestamps.index(self.current_timestamp) + 1]
            == list(reversed(self.network.list_timestamps()))[0]
        ):
            self.is_terminated = True

        return (
            self.current_observation,
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
