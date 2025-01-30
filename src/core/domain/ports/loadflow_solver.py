from abc import ABC, abstractmethod
from src.core.domain.models.network import Network
from src.core.domain.enums import LoadFlowType


class LoadFlowSolver(ABC):
    @abstractmethod
    def solve(
        self, network: Network, loadflow_type: LoadFlowType
    ) -> Network:  # NOTE: Should it take a DynamicNetwork and return a SolvedNetwork? Being more precise here in typing
        pass
