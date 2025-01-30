from typing import Self
from pydantic import model_validator, Field
from src.core.domain.enums import State
from src.core.domain.models.base_model import BaseConfigModel
from src.core.domain.models.elements_metadata.base import BaseMetadata
from src.core.constants import ElementStatus


class LineStaticAttributes(BaseConfigModel):
    """This represents the static attributes of a 'LINE' metadata."""

    status: ElementStatus  # TODO: Should be a dynamic attribute.
    voltage_level1_id: str
    voltage_level2_id: str
    bus1_id: str
    bus2_id: str
    b1: float  # Line shunt susceptance (S) on side 1
    b2: float  # Line shunt susceptance (S) on side 2
    g1: float  # Line shunt conductance (S) on side 1
    g2: float  # Line shunt conductance (S) on side 2
    r: float  # Resistance (Ohm) NOTE: per unit?
    x: float  # Reactance (Ohm) NOTE: per unit?
    connectable_bus1_id: str | None = None
    connectable_bus2_id: str | None = None
    name: str | None = None


class LineSolvedAttributes(BaseConfigModel):
    """Solved attributes for a 'LINE' element."""

    p1: float
    q1: float
    i1: float
    p2: float
    q2: float
    i2: float


class LineMetadata(BaseMetadata):
    """Through composition - this defines the metadata that is expected for a 'LOAD'."""

    state: State
    static: LineStaticAttributes
    dynamic: None = Field(default=None, exclude=True)  # Line has not dynamic attributes
    solved: LineSolvedAttributes | None = None

    @model_validator(mode="after")
    def check_state_consistency(self) -> Self:
        """Check the state passed is consistent with data passed."""

        if self.state == State.DYNAMIC:
            m = f"State can't be {State.DYNAMIC}."
            raise ValueError(m)

        if self.state == State.STATIC:
            m = "State is not consistent with data provided."
            if self.solved is not None:
                raise ValueError(m)

        return self

    @property
    def supported_states(self) -> list[State]:
        """Returns the list of states supported by this element."""
        return [State.STATIC, State.SOLVED]  # NOTE: Warning hardcoded
