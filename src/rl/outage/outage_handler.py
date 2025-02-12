import numpy as np
from src.rl.enums import Granularity
from src.rl.enums import OutageType
from src.core.constants import ElementStatus
from src.core.domain.models.element import NetworkElement
from src.core.constants import SupportedNetworkElementTypes

MAINTENANCE_DURATION = 24 * 5


class OutageHandler:
    """Handles the outage probability and events for a single network element."""

    def __init__(
        self,
        element: NetworkElement,
        initial_outage_prob: float,
        initial_remaining_duration: int,
        initial_usage_time: int,
        lambda_factor: float,
        granularity: Granularity = Granularity.HOUR,
    ):
        """
        :param element_id: ID of the network element.
        :param lambda_factor: Scaling factor for outage probability growth.
        :param granularity: Time unit granularity (HOUR, DAY, WEEK).
        """

        if element.type not in [
            SupportedNetworkElementTypes.GENERATOR,
            SupportedNetworkElementTypes.LINE,
        ]:
            raise ValueError(
                "OutageHandler can only be used with GENERATOR or LINE elements."
            )

        self.lambda_factor = lambda_factor
        self.granularity = granularity

        # Initialize attributes
        self._outage_prob = initial_outage_prob
        self._status = element.element_metadata.static.status
        self._remaining_duration = (
            initial_remaining_duration if self._status == ElementStatus.OUTAGE else 0
        )
        self._usage_time = initial_usage_time
        self._outage_type = None

    @property
    def outage_prob(self):
        return self._outage_prob

    @outage_prob.setter
    def outage_prob(self, value):
        self._outage_prob = max(0.0, min(1.0, value))

    @property
    def status(self):
        """Gets the current status of the element."""
        return self._status

    @status.setter
    def status(self, value: ElementStatus):
        """Sets the element's status, handling resets where needed."""
        self._status = value
        if value == ElementStatus.MAINTENANCE:
            self.usage_time = 0
            self.outage_prob = 0.0

    @property
    def remaining_duration(self):
        return self._remaining_duration

    @remaining_duration.setter
    def remaining_duration(self, value: int):
        self._remaining_duration = max(0, value)

    @property
    def usage_time(self):
        return self._usage_time

    @usage_time.setter
    def usage_time(self, value: int):
        self._usage_time = max(0, value)

    @property
    def outage_type(self):
        """Gets the outage type if the element is in an outage."""
        return self._outage_type if self.status == ElementStatus.OUTAGE else None

    def _update_usage_time(self) -> None:
        """Updates usage time and outage probability based on element status."""
        if self._status in [ElementStatus.OUTAGE, ElementStatus.MAINTENANCE]:
            return

        if self._status == ElementStatus.ON:
            self.usage_time += 1
        else:
            return

        self.outage_prob = self.lambda_factor * self.usage_time

    def _sample_outage(self) -> None:
        """Samples an unplanned outage and assigns a type with duration."""

        if self._status in [ElementStatus.OUTAGE, ElementStatus.MAINTENANCE]:
            return

        if np.random.rand() < self.outage_prob:
            self.status = ElementStatus.OUTAGE
            self._outage_type = np.random.choice( # TODO: Make the probas elsewhere
                [OutageType.SHORT_TERM, OutageType.MID_TERM, OutageType.LONG_TERM],
                p=[0.50, 0.35, 0.15],
            )

            self.remaining_duration = np.random.randint(
                self._outage_type.lower_duration, self._outage_type.upper_duration
            )

    def step(self):
        """Advances the outage state (decreasing remaining durations)."""
        # Update usage time
        self._update_usage_time()

        # Sample outage if no outage or maintenance
        if self._status == ElementStatus.ON and self._usage_time % 24 == 0:
            self._sample_outage()

        # Decrease remaining duration if in outage or maintenance
        if self._status in [ElementStatus.OUTAGE, ElementStatus.MAINTENANCE]:
            self.remaining_duration -= 1
            if self.remaining_duration <= 0:
                self.status = ElementStatus.ON
                self.usage_time = 0
                self.outage_prob = 0.0
                self._outage_type = None

    def send_to_maintenance(self):
        """Initiates planned maintenance, resetting outage probability."""
        if self._status in [ElementStatus.OUTAGE, ElementStatus.MAINTENANCE]:
            return

        self.status = ElementStatus.MAINTENANCE
        self.remaining_duration = MAINTENANCE_DURATION
