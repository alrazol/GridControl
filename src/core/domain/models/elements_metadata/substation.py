from typing import Self
from pydantic import model_validator, Field
from src.core.domain.models.base_model import BaseConfigModel
from src.core.domain.models.elements_metadata.base import BaseMetadata
from src.core.domain.enums import State


class SubstationStaticAttributes(BaseConfigModel):
    """Metadata for a substation element."""

    # id: str
    name: str | None = None
    country: str | None = None
    tso: str | None = None


class SubstationMetadata(BaseMetadata):
    state: State
    static: SubstationStaticAttributes
    dynamic: None = Field(default=None, exclude=True)  # Substation is only static
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
