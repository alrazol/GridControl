from src.core.infrastructure.settings import Settings

import src.rl.repositories.one_hot_map_builder as ohmb
from src.rl.one_hot_map_builder import OneHotMapBuilder
from src.rl.repositories.one_hot_map_builder import (
    __all__ as AVAILABLE_ONE_HOT_MAP_BUILDERS,
)

import src.rl.repositories.network_transition_handler as nth
from src.rl.repositories.network_transition_handler import (
    __all__ as AVAILABLE_NETWORK_TRANSITION_HANDLERS,
)
from src.rl.environment_helpers import NetworkTransitionHandler

import src.rl.repositories.network_snapshot_observation_builder as nsob
from src.rl.repositories.network_snapshot_observation_builder import (
    __all__ as AVAILABLE_NETWORK_SNAPSHOT_OBSERVATION_BUILDERS,
)
from src.rl.observation.network_snapshot_observation_builder import (
    NetworkSnapshotObservationBuilder,
)


from src.rl.repositories.network_repository import NetworkRepository
from src.rl.repositories.sqlite_network_repository import SQLiteNetworkRepository
from src.rl.repositories.loadflow_solver import LoadFlowSolverRepository
from src.rl.repositories.network_builder import NetworkBuilder
from src.rl.artifacts.loss import LossTrackerRepository
from src.rl.artifacts.reward import RewardTrackerRepository
from src.rl.reward.reward_handler import RewardHandler
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
from src.rl.observation.network_observation_handler import NetworkObservationHandler
from src.rl.action_space_builder import ActionSpaceBuilder
from src.rl.repositories.action_space_builder import DefaultActionSpaceBuilder
from src.rl.repositories.reward_handler import DefaultRewardHandler
from src.rl.repositories.outage_handler_builder import DefaultOutageHandlerBuilder
from src.rl.outage.outage_handler_builder import OutageHandlerBuilder
from src.rl.outage.network_element_outage_handler_builder import (
    NetworkElementOutageHandlerBuilder,
)
from src.rl.repositories.network_element_outage_handler_builder import (
    DefaultNetworkElementOutageHandlerBuilder,
)


class Repositories:
    def __init__(self, s: Settings) -> None:
        self.settings = s

    def get_network_repository(self) -> NetworkRepository:
        return SQLiteNetworkRepository(
            db_url=self.settings.DB_URL,
            should_create_tables=False,
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

    def get_network_builder(self) -> NetworkBuilder:
        return DefaultNetworkBuilder()

    def get_network_transition_handler(
        self, class_name: str
    ) -> NetworkTransitionHandler:
        if class_name not in AVAILABLE_NETWORK_TRANSITION_HANDLERS:
            raise ValueError(
                f"Invalid NetworkTransitionHandler class name: {class_name}"
            )
        return getattr(nth, class_name)()

    def get_network_observation_handler(self) -> NetworkObservationHandler:
        return DefaultNetworkObservationHandler()

    def get_network_snapshot_observation_builder(
        self, class_name: str
    ) -> NetworkSnapshotObservationBuilder:
        if class_name not in AVAILABLE_NETWORK_SNAPSHOT_OBSERVATION_BUILDERS:
            raise ValueError(
                f"Invalid NetworkSnapshotObservationBuilder class name: {class_name}"
            )
        return getattr(nsob, class_name)()

    def get_action_space_builder(self) -> ActionSpaceBuilder:
        return DefaultActionSpaceBuilder()

    def get_one_hot_map_builder(self, class_name: str) -> OneHotMapBuilder:
        if class_name not in AVAILABLE_ONE_HOT_MAP_BUILDERS:
            raise ValueError(f"Invalid OneHotMapBuilder class name: {class_name}")
        return getattr(ohmb, class_name)()

    def get_reward_handler(
        self, aggregator_name: str, rewards: list[str]
    ) -> RewardHandler:
        return DefaultRewardHandler(aggregator_name=aggregator_name, rewards=rewards)

    def get_outage_handler_builder(self) -> OutageHandlerBuilder:
        return DefaultOutageHandlerBuilder()

    def get_network_element_outage_handler_builder(
        self,
    ) -> NetworkElementOutageHandlerBuilder:
        # TODO: A getatrr for the specific network element outage handler
        return DefaultNetworkElementOutageHandlerBuilder()
