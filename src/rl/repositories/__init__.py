from src.core.infrastructure.settings import Settings
from src.rl.repositories.network_repository import NetworkRepository
from src.rl.repositories.http_network_repository import HttpNetworkRepository
from src.rl.repositories.loadflow_solver import LoadFlowSolverRepository
from src.rl.repositories.network_builder import NetworkBuilder
from src.rl.repositories.loss_tracker import LossTrackerRepository
from src.rl.repositories.reward_tracker import RewardTrackerRepository
from src.rl.repositories.network_snapshot_observation_builder import (
    DefaultNetworkSnapshotObservationBuilder,
)
from src.core.infrastructure.adapters.pypowsybl_loadflow_solver import (
    PyPowSyblLoadFlowSolver,
)
from src.core.infrastructure.adapters.network_builder import DefaultNetworkBuilder
from src.core.infrastructure.services.converters.pypowsybl_methods.service import (
    PyPowsyblCompatService,
)
from src.rl.artifacts.loss import LossTracker
from src.rl.artifacts.reward import RewardTracker
from src.rl.observation.network_snapshot_observation_builder import (
    NetworkSnapshotObservationBuilder,
)


class Repositories:
    def __init__(self, s: Settings) -> None:
        self.settings = s

    def get_network_repository(self) -> NetworkRepository:
        return HttpNetworkRepository(baseurl=self.settings.NETWORK_API_BASEURL)

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
