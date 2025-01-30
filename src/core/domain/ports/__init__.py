from abc import ABC, abstractmethod
from src.core.domain.ports.network_repository import DatabaseNetworkRepository
from src.core.domain.ports.loadflow_solver import LoadFlowSolver
from src.core.domain.ports.visualiser import Visualiser


class Ports(ABC):
    """This class defines the interfaces for the different repositories."""

    @abstractmethod
    def network_repository(self) -> DatabaseNetworkRepository:
        pass

    @abstractmethod
    def loadflow_solver_repository(self) -> LoadFlowSolver:
        pass

    @abstractmethod
    def visualiser_repository(self) -> Visualiser:
        pass
