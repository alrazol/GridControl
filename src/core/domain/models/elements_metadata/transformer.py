from typing import Self
from pydantic import model_validator, Field
from src.core.domain.models.base_model import BaseConfigModel
from src.core.domain.models.elements_metadata.base import BaseMetadata
from src.core.domain.enums import State


class TwoWindingsTransformersStaticAttributes(BaseConfigModel):
    """This describes the static attributes of a 'TwoWindingsTransformers'."""

    # id: str
    voltage_level1_id: str  # Voltage level coming in side 1 of the line
    voltage_level2_id: str  # Voltage level coming in side 2 of the line
    bus1_id: str  # The bus to which the line is connected on side 1
    bus2_id: str  # The bus to which the line is connected on side 2
    rated_u1: float  # Nominal voltage of the side 1 of the transformer
    rated_u2: float  # Nominal voltage of the side 2 of the transformer
    rated_s: float | None = None  # Nominal power of the transformer
    b: float  # The shunt susceptance, in S
    g: float  # The shunt conductance, in S
    r: float  # The resistance, in Ohm
    x: float  # The reactance, in Ohm
    name: str | None = None


class TwoWindingsTransformersMetadata(BaseMetadata):
    """
    Metadata for a 2-windings transformer element.
    """

    state: State
    static: TwoWindingsTransformersStaticAttributes
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
