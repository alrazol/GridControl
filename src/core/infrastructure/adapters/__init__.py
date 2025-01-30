from src.core.domain.ports.network_repository import DatabaseNetworkRepository
from src.core.domain.ports.loadflow_solver import LoadFlowSolver
from src.core.domain.ports.visualiser import Visualiser
from src.core.infrastructure.adapters.sqlite_network_repository import (
    SQLiteNetworkRepository,
)
from src.core.infrastructure.adapters.pypowsybl_loadflow_solver import (
    PyPowSyblLoadFlowSolver,
)
from src.core.infrastructure.adapters.pypowsybl_visualiser_repository import (
    PyPowSyblVisualiserRepository,
)
from src.core.domain.ports import Ports
from src.core.infrastructure.settings import Settings
from src.core.infrastructure.services import PyPowsyblCompatService


class Adapters(Ports):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.to_pypowsybl_converter_service = PyPowsyblCompatService()

    def network_repository(self) -> DatabaseNetworkRepository:
        return SQLiteNetworkRepository(
            db_url=self.settings.DB_URL,
            should_create_tables=self.settings.SHOULD_CREATE_TABLES,
        )

    def loadflow_solver_repository(self) -> LoadFlowSolver:
        return PyPowSyblLoadFlowSolver(
            to_pypowsybl_converter_service=self.to_pypowsybl_converter_service
        )

    def visualiser_repository(self) -> Visualiser:
        return PyPowSyblVisualiserRepository(
            to_pypowsybl_converter_service=self.to_pypowsybl_converter_service
        )
