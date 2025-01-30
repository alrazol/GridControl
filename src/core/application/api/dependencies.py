from src.core.domain.ports import DatabaseNetworkRepository
from src.core.infrastructure.adapters.sqlite_network_repository import (
    SQLiteNetworkRepository,
)
from src.core.infrastructure.adapters.pypowsybl_loadflow_solver import (
    PyPowSyblLoadFlowSolver,
)
from src.core.domain.ports import LoadFlowSolver
from src.core.infrastructure.settings import Settings
from src.core.infrastructure.services.converters.pypowsybl_methods.service import (
    PyPowsyblCompatService,
)


class Dependencies:
    def __init__(self, s: Settings) -> None:
        self.settings = s
        self.converter_service = PyPowsyblCompatService()

    def get_repository(self) -> DatabaseNetworkRepository:
        return SQLiteNetworkRepository(
            db_url=self.settings.DB_URL, should_create_tables=False
        )

    def get_loadflow_solver(self) -> LoadFlowSolver:
        return PyPowSyblLoadFlowSolver(
            to_pypowsybl_converter_service=self.converter_service
        )
