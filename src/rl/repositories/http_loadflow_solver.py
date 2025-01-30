import requests
from src.rl.repositories.loadflow_solver import LoadFlowSolver
from src.core.domain.models.network import Network
from src.core.constants import LoadFlowType


class HttpLoadFlowSolver(LoadFlowSolver):
    def __init__(self, baseurl: str):
        self.baseurl = baseurl

    def get(self, network: Network, loadflow_type: LoadFlowType) -> Network:
        endpoint = "get-loadflow-solver"
        headers = {
            "Accept": "application/json",
        }
        params = {"network": network, "loadflow_type": loadflow_type}
        response_data = requests.get(
            url=f"{self.baseurl}/{endpoint}",
            params=params,
            headers=headers,
        )
        response_data.raise_for_status()
        return response_data.json()
