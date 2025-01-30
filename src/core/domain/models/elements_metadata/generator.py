from typing import Self
from src.core.domain.models.base_model import BaseConfigModel
from src.core.domain.models.elements_metadata.base import BaseMetadata
from src.core.domain.enums import State
from pydantic import model_validator
from src.core.constants import ElementStatus


class GeneratorStaticAttributes(BaseConfigModel):
    """Defines the static attributes of a 'GENERATOR' element."""

    status: ElementStatus
    voltage_level_id: str
    bus_id: str
    Pmax: float  # MW
    Pmin: float  # MW
    is_voltage_regulator: bool


class GeneratorDynamicAttributes(BaseConfigModel):
    """Defines the dynamic attributes of a 'GENERATOR' element."""

    Ptarget: float  # MW
    Vtarget: float  # kV
    Qtarget: float | None = None  # MVAr
    Srated: float | None = None  # MVA


class GeneratorSolvedAttributes(BaseConfigModel):
    """Defines the solved attributes of a 'GENERATOR' element."""

    p: float  # MW
    q: float  # MVAr
    i: float | None = None  # A
    connected: bool


class GeneratorMetadata(BaseMetadata):
    """Through composition, defines the metadata for a 'GENERATOR' element."""

    state: State
    static: GeneratorStaticAttributes
    dynamic: GeneratorDynamicAttributes | None = None
    solved: GeneratorSolvedAttributes | None = None

    @model_validator(mode="after")
    def validate_state_consistency(self) -> Self:
        """Validates that the metadata state is consistent with the data provided."""

        m = "State is not consistent with the data provided."

        if self.state == State.STATIC:
            if self.dynamic is not None or self.solved is not None:
                raise ValueError(m)

        if self.state == State.DYNAMIC:
            if self.dynamic is None or self.solved is not None:
                raise ValueError(m)

        if self.state == State.SOLVED:
            if self.dynamic is None or self.solved is None:
                raise ValueError(m)

        return self

    @property
    def supported_states(self) -> list[State]:
        """Returns the list of states supported by this element."""
        return [State.STATIC, State.DYNAMIC, State.SOLVED]  # NOTE: Warning hardcoded
