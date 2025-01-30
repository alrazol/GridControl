from typing import Self
from datetime import datetime
from pydantic import BaseModel
from src.core.utils import parse_datetime_to_str
from src.core.utils import generate_hash
from src.core.constants import (
    SupportedNetworkElementTypes,
    DATETIME_FORMAT,
    DEFAULT_TIMEZONE,
)
from src.core.domain.models.elements_metadata import (
    BaseMetadata,
)
from src.core.domain.models.operational_constraint import OperationalConstraint


class NetworkElement(BaseModel):
    """
    Model for a network element.

    uid: unique identifier based on timestamp and id
    id: identifier aka name.
    state: Maps to the expected format of metadata.
    timestamp: description.
    type: Element type, 'LINE', 'GENERATOR' etc...
    element_metadata: Info on the physical characteristics of the element.
    network_id: id of the network the element belongs to.

    """

    uid: str
    id: str
    timestamp: str | None
    type: SupportedNetworkElementTypes
    element_metadata: BaseMetadata
    network_id: str
    operational_constraints: list[OperationalConstraint]

    @classmethod
    def from_metadata(
        cls,
        id: str,
        timestamp: datetime | None,
        type: SupportedNetworkElementTypes,
        element_metadata: BaseMetadata,
        operational_constraints: list[OperationalConstraint],
        network_id: str,
    ) -> Self:
        """Build a NetworkElement and implementing pydantic validation on the provided metadata, according to the element type"""

        if (
            len(operational_constraints) > 0
            and type != SupportedNetworkElementTypes.LINE
        ):
            m = "Operational constraints can only apply to lines."
            raise ValueError(m)

        timestamp_parsed = (
            parse_datetime_to_str(
                timestamp, format=DATETIME_FORMAT, tz=DEFAULT_TIMEZONE
            )
            if timestamp is not None
            else timestamp
        )

        element = cls(
            uid=generate_hash(s=f"{id}_{timestamp_parsed}"),
            id=id,
            state=element_metadata.state,
            timestamp=timestamp_parsed,
            type=type,
            element_metadata=element_metadata,
            network_id=network_id,
            operational_constraints=operational_constraints,
        )
        return element
