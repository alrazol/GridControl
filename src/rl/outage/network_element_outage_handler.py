import numpy as np
from abc import ABC, abstractmethod
from src.core.domain.models.element import NetworkElement
from src.rl.enums import Granularity
from src.core.constants import ElementStatus
from src.rl.enums import OutageType


class NetworkElementOutageHandler(ABC):
    """Abstract base class for handling outages of network elements."""

    def __init__(
        self,
        element: NetworkElement,
        initial_outage_prob: float,
        initial_remaining_duration: int,
        initial_usage_time: int,
        lambda_factor: float,
        seed: int,
        granularity: Granularity,
    ):
        """
        Initializes the outage handler.

        :param element: The network element.
        :param initial_outage_prob: Initial probability of an outage.
        :param initial_remaining_duration: Initial duration of the outage (if applicable).
        :param initial_usage_time: Initial accumulated usage time.
        :param lambda_factor: Scaling factor for outage probability growth.
        :param seed: Random seed for reproducibility.
        :param granularity: Time unit granularity (HOUR, DAY, WEEK).
        """
        self.element_id = element.id
        self.lambda_factor = lambda_factor
        self.granularity = granularity
        self.rng = np.random.default_rng(seed)

        # Store initial values for reset
        self._initial_outage_prob = initial_outage_prob
        self._initial_remaining_duration = initial_remaining_duration
        self._initial_usage_time = initial_usage_time
        self._initial_status = element.element_metadata.static.status

    @property
    def outage_prob(self) -> float:
        """Returns the current outage probability."""
        return self._outage_prob

    @outage_prob.setter
    def outage_prob(self, value: float):
        """Sets outage probability within valid bounds [0,1]."""
        self._outage_prob = max(0.0, min(1.0, value))

    @property
    def status(self) -> ElementStatus:
        """Gets the current status of the element."""
        return self._status

    @status.setter
    def status(self, value: ElementStatus):
        """Sets the element's status, handling necessary resets."""
        self._status = value
        if value == ElementStatus.MAINTENANCE:
            self.usage_time = 0
            self.outage_prob = 0.0

    @property
    def remaining_duration(self) -> int:
        """Returns the remaining outage or maintenance duration."""
        return self._remaining_duration

    @remaining_duration.setter
    def remaining_duration(self, value: int):
        """Sets the remaining duration, ensuring it is non-negative."""
        self._remaining_duration = max(0, value)

    @property
    def usage_time(self) -> int:
        """Returns the accumulated usage time."""
        return self._usage_time

    @usage_time.setter
    def usage_time(self, value: int):
        """Sets usage time, ensuring it is non-negative."""
        self._usage_time = max(0, value)

    @property
    def outage_type(self) -> OutageType | None:
        """Returns the current outage type if in an outage, otherwise None."""
        return self._outage_type if self.status == ElementStatus.OUTAGE else None

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def _update_usage_time(self) -> None:
        """Updates usage time and outage probability. To be implemented by subclasses."""
        pass

    @abstractmethod
    def _sample_outage(self) -> None:
        """Samples an unplanned outage and assigns type/duration. To be implemented by subclasses."""
        pass

    @abstractmethod
    def step(self) -> None:
        """Advances the state of the outage system."""
        pass

    @abstractmethod
    def send_to_maintenance(self) -> None:
        """Initiates planned maintenance, resetting outage probability."""
        pass
