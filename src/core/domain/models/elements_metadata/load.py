from typing import Literal
from src.core.domain.models.base_model import BaseConfigModel
from src.core.domain.models.elements_metadata.base import BaseMetadata
from src.core.domain.enums import State
from pydantic import model_validator
from typing import Self


class LoadStaticAttributes(BaseConfigModel):
    """This class defines the static attributes of a 'LOAD' element metadata."""

    # id: str
    voltage_level_id: str
    bus_id: str
    name: str | None = None
    connectable_bus_id: str | None = None
    node: int | None = None
    type: Literal["UNDEFINED", "AUXILIARY", "FICTITIOUS"] | None = None


class LoadDynamicAttributes(BaseConfigModel):
    """This class defines the dynamic attributes of a 'LOAD' element metadata."""

    Pd: float  # MW
    Qd: float  # MVAr


class LoadSolvedAttributes(BaseConfigModel):
    """This class defines the solved attributes of a 'LOAD' element metadata."""

    p: float  # MW
    q: float  # MVAr
    i: float | None = None  # A (AC solver specific)


class LoadMetadata(BaseMetadata):
    """Through composition - this defines the metadata that is expected for a 'LOAD'."""

    state: State  # We specify the state externally and validate it against the data
    static: LoadStaticAttributes
    dynamic: LoadDynamicAttributes | None = None
    solved: LoadSolvedAttributes | None = None

    @model_validator(mode="after")
    def check_state_consistency(self) -> Self:
        """Check the state passed is consistent with data passed."""

        m = "State is not consistent with data provided."

        if self.state == State.STATIC:
            if self.dynamic is not None or self.solved is not None:
                raise ValueError(m)

        if self.state == State.DYNAMIC:
            if self.dynamic is None or self.solved is not None:
                raise ValueError(m)

        if self.state == State.SOLVED:
            if self.solved is None or self.dynamic is None:
                raise ValueError(m)

        return self

    @property
    def supported_states(self) -> list[State]:
        """Returns the list of states supported by this element."""
        return [State.STATIC, State.DYNAMIC, State.SOLVED]  # NOTE: Warning hardcoded
