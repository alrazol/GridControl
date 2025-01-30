from typing import Self
from src.core.domain.models.base_model import BaseConfigModel
from src.core.domain.models.elements_metadata.base import BaseMetadata
from src.core.domain.enums import State
from pydantic import model_validator, Field


class BusStaticAttributes(BaseConfigModel):
    """This class defines the static attributes of a 'BUS' element metadata."""

    voltage_level_id: str  # Voltage level to which the bus belongs to


class BusMetadata(BaseMetadata):
    """Gives the attributes for a 'BUS' element."""

    state: State
    static: BusStaticAttributes
    dynamic: None = Field(default=None, exclude=True)  # Bus can only be static
    solved: None = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def check_state_consistency(self) -> Self:
        if self.state != State.STATIC:
            m = f"State has to be {State.STATIC} for a 'BUS' metadata."
            raise ValueError(m)
        return self

    @property
    def supported_states(self) -> list[State]:
        """Returns the list of states supported by this element."""
        return [State.STATIC]  # NOTE: Warning hardcoded
