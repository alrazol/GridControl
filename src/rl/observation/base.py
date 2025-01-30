import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Self
from src.core.domain.models.element import NetworkElement
from src.core.constants import SupportedNetworkElementTypes, ElementStatus


class BaseElementObservation(ABC):
    """
    This is a base class for an element observation, that is what an agent can see.
    A NetworkObservation will derive from this, as a natural list of BaseElementObservation
    as well as optional network level observations.
    """

    def __init__(
        self,
        id: str,
        timestamp: datetime,
        type: SupportedNetworkElementTypes,
        status: ElementStatus,
    ) -> None:
        self.id = id
        self.timestamp = timestamp
        self.type = type
        self.status = status

    @classmethod
    @abstractmethod
    def from_element(cls, element: NetworkElement) -> Self:
        """
        All specific implementations of element observations must be able
        to be built from NetworkElement.
        """
        pass

    @property
    @abstractmethod
    def is_switchable(self) -> bool:
        """Can the element be moved from status 'ON' to 'OFF' and vice versa."""
        pass

    @property
    def bus_ids(self) -> list[str]:
        """Which bus id(s) the element is connected to."""
        pass

    @property
    def voltage_level_ids(self) -> list[str]:
        """To which voltage level id(s) the element belongs."""
        pass

    @abstractmethod
    def to_array(self, one_hot_map: dict[str, dict[str, np.ndarray]]) -> np.ndarray:
        """
        Convert the element observation to a flat array, one-hot encoding
        categorical attributes using the provided one-hot mappings.
        """
        pass

    @abstractmethod
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert the element observation to pd.DataFrame.
        """
        pass
