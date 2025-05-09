import gym
import copy
from gym.spaces import Space
from datetime import datetime
from src.rl.config_loaders.environment.config_loader import EnvironmentConfig
from src.core.domain.ports import LoadFlowSolver
from src.core.constants import SupportedNetworkElementTypes
from src.rl.repositories.network_repository import NetworkRepository
from src.core.constants import LoadFlowType
from src.core.domain.models.network import Network
from src.rl.observation.network import NetworkObservation
from src.rl.action.base import BaseAction
from src.rl.action_space import ActionSpace
from src.rl.one_hot_map import OneHotMap
from src.rl.repositories import (
    NetworkSnapshotObservationBuilder,
    NetworkTransitionHandler,
)
from src.rl.action_space_builder import ActionSpaceBuilder
from src.core.domain.ports.network_builder import NetworkBuilder
from src.core.utils import parse_datetime_to_str
from src.rl.observation.network_observation_handler import NetworkObservationHandler
from src.rl.one_hot_map_builder import OneHotMapBuilder
from src.rl.reward.reward_handler import RewardHandler
from src.rl.outage.outage_handler_builder import OutageHandlerBuilder
from src.rl.outage.network_element_outage_handler_builder import (
    NetworkElementOutageHandlerBuilder,
)
from src.rl.outage.outage_handler import OutageHandler
from src.rl.enums import Granularity


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
        reward_handler: RewardHandler,
        network_snapshot_observation_builder: NetworkSnapshotObservationBuilder,
        network_builder: NetworkBuilder,
        network_transition_handler: NetworkTransitionHandler,
        network_observation_handler: NetworkObservationHandler,
        outage_handler: OutageHandler,
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
        self.network_snapshot_observation_builder = network_snapshot_observation_builder
        self.network_builder = network_builder
        self.network_transition_handler = network_transition_handler
        self.network_observation_handler = network_observation_handler
        self.outage_handler = outage_handler

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
        self.current_observation = copy.deepcopy(self.initial_observation)
        self.current_network = copy.deepcopy(self.initial_network)
        self.is_terminated = False
        self.episode_reward = 0.0
        self.outage_handler.reset()

        return self.initial_observation, {}

    def step(self, action: BaseAction) -> tuple[NetworkObservation, float, bool, dict]:
        """
        Rollout one step of the environment.
        """

        # 1) Fetch next timesamp's Network.
        all_timestamps = self.network.timestamps
        next_timestamp = all_timestamps[
            all_timestamps.index(self.current_timestamp) + 1
        ]
        if not hasattr(self, "current_timestamp"):
            raise ValueError("You need to reset the environment before taking actions.")

        next_network = (
            self.network_builder.from_elements(  # NOTE: Make a copy of elements or not?
                id=f"{self.network.id}_{parse_datetime_to_str(next_timestamp)}",
                elements=self.network.list_elements(
                    timestamp=all_timestamps[
                        all_timestamps.index(self.current_timestamp) + 1
                    ]
                ),
            )
        )

        # 2) Update current network with the action & inplace dynamic attrs with next timestamp's values.
        # Inplace maybe the self.current_network?
        self.current_network = self.network_transition_handler.build_next_network(
            outage_handler=self.outage_handler,
            current_network=self.current_network,
            next_network_no_action=next_network,
            action=action,
        )

        # 3) Observation comes from solving the next_network_with_action.
        next_snapshot_observation = (
            self.network_snapshot_observation_builder.from_network(
                network=self.loadflow_solver.solve(
                    network=self.current_network,
                    loadflow_type=self.loadflow_type,
                ),
                timestamp=self.current_network.list_timestamps()[0],
                outage_handler=self.outage_handler,
            )
        )

        # 4) Compute reward on next NetworkObservationSnapshot.
        reward = self.reward_handler.build_reward().compute_reward(
            network_snapshot_observation=next_snapshot_observation,
        )

        # 5) Update attrs.
        self.current_observation = (
            self.network_observation_handler.add_network_snapshot_observation(
                network_observation=self.current_observation,
                network_snapshot_observation=next_snapshot_observation,
            )
        )
        self.current_timestamp = next_timestamp

        if next_timestamp == list(reversed(all_timestamps))[0]:
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
    environment_config: EnvironmentConfig,
    loadflow_solver: LoadFlowSolver,
    network_builder: NetworkBuilder,
    network_snapshot_observation_builder: NetworkSnapshotObservationBuilder,
    action_space_builder: ActionSpaceBuilder,
    one_hot_map_builder: OneHotMapBuilder,
    network_observation_handler: NetworkObservationHandler,
    network_transition_handler: NetworkTransitionHandler,
    loadflow_type: LoadFlowType,
    reward_handler: RewardHandler,
    action_types: list[str],
    observation_memory_length: int,
    outage_handler_builder: OutageHandlerBuilder,
    network_element_outage_handler_builder: NetworkElementOutageHandlerBuilder,
) -> NetworkEnvironment:
    # 1) Fetch the network
    network = network_repository.get(network_id=network_id)
    network.timestamps = network.list_timestamps()
    initial_network = network_builder.from_elements(
        id="tmp",
        elements=copy.deepcopy(network.list_elements(timestamp=network.timestamps[0])),
    )

    # 2) Initialise the outage handler.
    outage_handler = outage_handler_builder.from_network_element_outage_handlers(
        network_element_outage_handlers=[
            network_element_outage_handler_builder.from_element(
                element=copy.deepcopy(element),
                config=environment_config.outage_handler_config.get(element.id),
                granularity=Granularity.HOUR,
            )
            for element in initial_network.list_elements(
                timestamp=initial_network.list_timestamps()[0],
                element_types=[
                    SupportedNetworkElementTypes.LINE,
                ],
            )
        ],
    )

    # 3) Build the initial network snapshot observation.
    initial_network_snapshot_observation = (  # NOTE: Creates a new object
        network_snapshot_observation_builder.from_network(
            network=loadflow_solver.solve(
                network=initial_network, loadflow_type=loadflow_type
            ),
            timestamp=network.timestamps[0],
            outage_handler=outage_handler,
        )
    )

    # 4) Build the action space.
    action_space = action_space_builder.from_action_types(
        action_types=action_types,
        network=initial_network,
        outage_handler=outage_handler,
    )

    # 5) Build the observation space, assumed unique across timestamps.
    one_hot_map = one_hot_map_builder.from_network_snapshot_observation(
        network_snapshot_observation=initial_network_snapshot_observation
    )
    initial_observation_empty = network_observation_handler.init_network_observation(
        history_length=observation_memory_length,
    )
    initial_observation = network_observation_handler.add_network_snapshot_observation(
        network_observation=initial_observation_empty,
        network_snapshot_observation=initial_network_snapshot_observation,
    )

    observation_space = initial_observation.to_observation_space(
        one_hot_map=one_hot_map
    )

    return NetworkEnvironment(
        network=network,
        initial_observation=initial_observation,
        initial_network=initial_network,
        loadflow_solver=loadflow_solver,
        loadflow_type=loadflow_type,
        action_space=action_space,
        observation_space=observation_space,
        one_hot_map=one_hot_map,
        reward_handler=reward_handler,
        network_snapshot_observation_builder=network_snapshot_observation_builder,
        network_builder=network_builder,
        network_transition_handler=network_transition_handler,
        network_observation_handler=network_observation_handler,
        outage_handler=outage_handler,
    )
