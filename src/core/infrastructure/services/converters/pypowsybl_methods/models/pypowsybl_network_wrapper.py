from datetime import datetime
from pydantic import BaseModel, field_validator, ConfigDict
from pypowsybl.network import Network as PyPowSyblNetwork
from src.core.domain.models.element import NetworkElement
from src.core.constants import ElementStatus
from src.core.utils import parse_datetime_to_str
from src.core.constants import DATETIME_FORMAT, DEFAULT_TIMEZONE


class PyPowSyblNetworkWrapper(BaseModel):
    data: dict[datetime, (PyPowSyblNetwork, NetworkElement)]

    # Can't generate pydantic model for the pp object
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("data", mode="after")
    def check_only_off_elements_in_elements(
        v: dict[datetime, (PyPowSyblNetwork, NetworkElement)],
    ) -> dict[datetime, (PyPowSyblNetwork, NetworkElement)]:
        for _, network in v.items():
            for element in network[1]:
                if element.element_metadata.static.status != ElementStatus.OFF:
                    m = "All elements in off elements have to have status 'OFF'."
                    raise ValueError(m)
        return v

    @field_validator("data", mode="after")
    def check_datetimes_format(
        v: dict[datetime, (PyPowSyblNetwork, NetworkElement)],
    ) -> dict[datetime, (PyPowSyblNetwork, NetworkElement)]:
        for timestamp in v.keys():
            _ = parse_datetime_to_str(
                d=timestamp, format=DATETIME_FORMAT, tz=DEFAULT_TIMEZONE
            )
        return v

    def get_active_network(self) -> dict[str, PyPowSyblNetwork]:
        return {
            parse_datetime_to_str(
                d=t, format=DATETIME_FORMAT, tz=DEFAULT_TIMEZONE
            ): net[0]
            for t, net in self.data.items()
        }
