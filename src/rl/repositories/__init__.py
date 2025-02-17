from src.core.infrastructure.settings import Settings
from src.rl.repositories.network_repository import NetworkRepository
from src.rl.repositories.http_network_repository import HttpNetworkRepository
from src.rl.repositories.loadflow_solver import LoadFlowSolverRepository
from src.rl.repositories.network_builder import NetworkBuilder
from src.rl.environment_helpers import NetworkTransitionHandler
from src.rl.artifacts.loss import LossTrackerRepository
from src.rl.artifacts.reward import RewardTrackerRepository
from src.rl.one_hot_map_builder import OneHotMapBuilder
from src.rl.repositories.network_snapshot_observation_builder import (
    DefaultNetworkSnapshotObservationBuilder,
)
from src.rl.reward.reward_handler import RewardHandler
from src.rl.repositories.one_hot_map_builder import DefaultOneHotMapBuilder
from src.rl.repositories.network_observation_handler import (
    DefaultNetworkObservationHandler,
)
from src.core.infrastructure.adapters.pypowsybl_loadflow_solver import (
    PyPowSyblLoadFlowSolver,
)
from src.core.infrastructure.adapters.network_builder import DefaultNetworkBuilder
from src.core.infrastructure.services.converters.pypowsybl_methods.service import (
    PyPowsyblCompatService,
)
from src.rl.repositories.loss_tracker import LossTracker
from src.rl.repositories.reward_tracker import RewardTracker
from src.rl.observation.network_snapshot_observation_builder import (
    NetworkSnapshotObservationBuilder,
)
from src.rl.observation.network_observation_handler import NetworkObservationHandler
from src.rl.repositories.network_transition_handler import (
    DefaultNetworkTransitionHandler,
)
from src.rl.action_space_builder import ActionSpaceBuilder
from src.rl.repositories.action_space_builder import DefaultActionSpaceBuilder
from src.rl.repositories.reward_handler import DefaultRewardHandler


class Repositories:
    def __init__(self, s: Settings) -> None:
        self.settings = s

    def get_network_repository(self) -> NetworkRepository:
        return HttpNetworkRepository(
            baseurl=self.settings.NETWORK_API_BASEURL,
            network_builder=DefaultNetworkBuilder(),
        )

    def get_solver(self) -> LoadFlowSolverRepository:
        return PyPowSyblLoadFlowSolver(
            to_pypowsybl_converter_service=PyPowsyblCompatService(),
            network_builder=DefaultNetworkBuilder(),
        )

    def get_loss_tracker(self) -> LossTrackerRepository:
        return LossTracker()

    def get_reward_tracker(self) -> RewardTrackerRepository:
        return RewardTracker()

    def get_observation_builder(self) -> NetworkSnapshotObservationBuilder:
        return DefaultNetworkSnapshotObservationBuilder()

    def get_network_builder(self) -> NetworkBuilder:
        return DefaultNetworkBuilder()

    def get_network_transition_handler(self) -> NetworkTransitionHandler:
        return DefaultNetworkTransitionHandler()

    def get_network_observation_handler(self) -> NetworkObservationHandler:
        return DefaultNetworkObservationHandler()

    def get_network_snapshot_observation_builder(
        self,
    ) -> NetworkSnapshotObservationBuilder:
        return DefaultNetworkSnapshotObservationBuilder()

    def get_action_space_builder(self) -> ActionSpaceBuilder:
        return DefaultActionSpaceBuilder()

    def get_one_hot_map_builder(self) -> OneHotMapBuilder:
        return DefaultOneHotMapBuilder()

    def get_reward_handler(
        self, aggregator_name: str, rewards: list[str]
    ) -> RewardHandler:
        return DefaultRewardHandler(aggregator_name=aggregator_name, rewards=rewards)
