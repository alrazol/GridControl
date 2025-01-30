from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from src.core.domain.models.base_model import BaseConfigModel
from src.core.domain.enums import State

Static = TypeVar("Static", bound=BaseConfigModel)
Dynamic = TypeVar("Dynamic", bound=BaseConfigModel)
Solved = TypeVar("Solved", bound=BaseConfigModel)


class BaseMetadata(BaseConfigModel, Generic[Static], ABC):
    """Base class for elements' metadata classes."""

    state: State  # TODO: Should be infered now and exposed
    static: Static
    dynamic: Dynamic | None
    solved: Solved | None

    @property
    @abstractmethod
    def supported_states(self) -> list[State]:
        pass
