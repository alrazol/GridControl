from src.core.domain.models.element import NetworkElement
from src.core.domain.models.network import Network
from src.core.domain.ports.network_builder import NetworkBuilder
from src.core.utils import generate_hash


class DefaultNetworkBuilder(NetworkBuilder):
    @staticmethod
    def from_elements(id: str, elements: list[NetworkElement]) -> Network:
        return Network(
            uid=generate_hash(s=id),
            id=id,
            elements=[element for element in elements],
        )
