from pydantic import BaseModel
from src.core.domain.models.network import Network
from src.core.constants import LoadFlowType


class NetworkRequest(BaseModel):
    """This model for request a Network based on id."""

    network_id: str


class LoadFlowRequest(BaseModel):
    """Request for a loadflow solution."""

    network: Network
    loadflow_type: LoadFlowType
