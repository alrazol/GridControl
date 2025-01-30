from abc import ABC, abstractmethod
from src.core.domain.ports.loadflow_solver import LoadFlowSolver
from src.core.domain.models.network import Network
from src.core.constants import LoadFlowType


class LoadFlowSolverRepository(ABC):
    """Will only need a get in the RL package."""

    @abstractmethod
    def solve(self, network: Network, loadflow_type: LoadFlowType) -> LoadFlowSolver:
        pass
