from fastapi import APIRouter, Depends, HTTPException, Query
from src.core.domain.models.network import Network
from src.core.application.api.dependencies import Dependencies
from src.core.infrastructure.settings import Settings
from src.core.domain.ports.network_repository import DatabaseNetworkRepository
from src.core.domain.ports.loadflow_solver import LoadFlowSolver
from src.core.constants import LoadFlowType

router = APIRouter()

dependencies = Dependencies(s=Settings())


@router.get("/get-network")
async def get_network(
    network_id: str = Query(..., description="ID of the network to retrieve"),
    network_repository: DatabaseNetworkRepository = Depends(
        dependencies.get_repository
    ),
):
    """
    Endpoint to retrieve a network by its ID.
    """
    try:
        network = network_repository.get(network_id=network_id)
        return network
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


#@router.get("/get-loadflow-solver")
#async def get_loadflow_solver(
#    network: dict,
#    loadflow_type: str,
#    solver_repository: LoadFlowSolver = Depends(dependencies.get_loadflow_solver),
#):
#    """
#    Endpoint to get a loadflow solution for a network.
#    """
#    try:
#        network = solver_repository.solve(network=network, loadflow_type=loadflow_type)
#        return network
#    except ValueError as e:
#        raise HTTPException(status_code=404, detail=str(e))
