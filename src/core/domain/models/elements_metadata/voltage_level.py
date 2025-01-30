from typing import Literal
from src.core.domain.models.base_model import BaseConfigModel
from src.core.domain.models.elements_metadata.base import BaseMetadata
from src.core.domain.enums import State
from pydantic import model_validator, Field
from typing import Self


class VoltageLevelsStaticAttributes(BaseConfigModel):
    topology_kind: Literal["BUS_BREAKER", "NODE_BREAKER"]
    Vnominal: float  # Nominal voltage
    substation_id: str | None = None
    Vlimitlow: float | None = None  # Low voltage limit
    Vlimithigh: float | None = None  # High voltage limit
    name: str | None = None


class VoltageLevelsMetadata(BaseMetadata):
    """
    Metadata for a substation element.
    """

    state: State
    static: VoltageLevelsStaticAttributes
    dynamic: None = Field(default=None, exclude=True)
    solved: None = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def check_state_consistency(self) -> Self:
        if self.state != State.STATIC:
            m = f"State has to be {State.STATIC}"
            raise ValueError(m)

        return self

    @property
    def supported_states(self) -> list[State]:
        """Returns the list of states supported by this element."""
        return [State.STATIC]  # NOTE: Warning hardcoded
