from src.core.infrastructure.settings import Settings
from src.rl.repositories.network_repository import NetworkRepository
from src.rl.repositories.http_network_repository import HttpNetworkRepository
from src.rl.repositories.loadflow_solver import LoadFlowSolverRepository
from src.rl.repositories.experiment_repository import ExperimentRepository
from src.rl.repositories.sqlite_experiment_repository import SQLiteExperimentRepository
from src.core.infrastructure.adapters.pypowsybl_loadflow_solver import (
    PyPowSyblLoadFlowSolver,
)
from src.core.infrastructure.services.converters.pypowsybl_methods.service import (
    PyPowsyblCompatService,
)


# TODO: RL specific settings should be used here, separate modules.
class Repositories:
    def __init__(self, s: Settings) -> None:
        self.settings = s

    def get_network_repository(self) -> NetworkRepository:
        return HttpNetworkRepository(baseurl=self.settings.NETWORK_API_BASEURL)

    def get_experiment_repository(self) -> ExperimentRepository:
        return SQLiteExperimentRepository(
            db_url=self.settings.DB_URL,
            should_create_tables=self.settings.SHOULD_CREATE_TABLES,
        )

    def get_solver(self) -> LoadFlowSolverRepository:
        return PyPowSyblLoadFlowSolver(
            to_pypowsybl_converter_service=PyPowsyblCompatService()
        )
