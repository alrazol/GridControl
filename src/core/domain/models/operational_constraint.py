from typing import Self
from pydantic import BaseModel
from src.core.domain.enums import OperationalConstraintType, BranchSide
from src.core.utils import generate_hash, parse_datetime_to_str
from src.core.constants import (
    DATETIME_FORMAT,
    DEFAULT_TIMEZONE,
    SupportedNetworkElementTypes,
)
from datetime import datetime


class OperationalConstraint(BaseModel):
    uid: str
    element_uid: str
    element_id: str
    side: BranchSide
    name: str
    type: OperationalConstraintType
    value: float
    acceptable_duration: int

    @classmethod
    def from_element(
        cls,
        element_id: str,
        timestamp: datetime | None,
        element_type: SupportedNetworkElementTypes,
        side: BranchSide,
        name: str,
        type: OperationalConstraintType,
        value: float,
        acceptable_duration: int,
    ) -> Self:
        if element_type != SupportedNetworkElementTypes.LINE:
            m = "Only 'LINE' can have operational constraint."
            raise ValueError(m)

        timestamp_parsed = (
            parse_datetime_to_str(
                timestamp, format=DATETIME_FORMAT, tz=DEFAULT_TIMEZONE
            )
            if timestamp is not None
            else timestamp
        )

        # TODO: Very sensitive to changes in element.from_metadata
        element_uid = generate_hash(s=f"{element_id}_{timestamp_parsed}")

        return cls(
            uid=generate_hash(f"{element_uid}_{side.value}_{type.value}"),
            element_uid=element_uid,
            element_id=element_id,
            side=side,
            name=name,
            type=type,
            value=value,
            acceptable_duration=acceptable_duration,
        )
