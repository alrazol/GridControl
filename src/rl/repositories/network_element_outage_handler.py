from src.rl.enums import Granularity
from src.rl.enums import OutageType
from src.core.constants import ElementStatus
from src.core.domain.models.element import NetworkElement
from src.core.constants import SupportedNetworkElementTypes
from src.rl.outage.network_element_outage_handler import NetworkElementOutageHandler

MAINTENANCE_DURATION = 5


class DefaultNetworkElementOutageHandler(NetworkElementOutageHandler):
    """Handles the outage probability and events for a single network element."""

    def __init__(
        self,
        element: NetworkElement,
        initial_outage_prob: float,
        initial_remaining_duration: int,
        initial_usage_time: int,
        lambda_factor: float,
        seed: int,
        granularity: Granularity = Granularity.HOUR,
        maintenance_duration: int = MAINTENANCE_DURATION,
    ):
        """
        :param element: NetworkElement instance.
        :param initial_outage_prob: Initial probability of an outage.
        :param initial_remaining_duration: Initial duration of an outage.
        :param initial_usage_time: Initial accumulated usage time.
        :param lambda_factor: Scaling factor for outage probability growth.
        :param seed: Random seed for reproducibility.
        :param granularity: Time unit granularity (HOUR, DAY, WEEK).
        :param maintenance_duration_range: Lower and upper bound of maintenance duration.
        """
        if element.type not in [
            #SupportedNetworkElementTypes.GENERATOR,
            SupportedNetworkElementTypes.LINE,
        ]:
            raise ValueError(
                "OutageHandler can only be used with GENERATOR or LINE elements."
            )

        self.maintenance_duration = maintenance_duration

        # Store initial values for reset
        self._initial_outage_prob = initial_outage_prob
        self._initial_remaining_duration = initial_remaining_duration
        self._initial_usage_time = initial_usage_time
        self._initial_status = element.element_metadata.static.status

        super().__init__(
            element,
            initial_outage_prob,
            initial_remaining_duration,
            initial_usage_time,
            lambda_factor,
            seed,
            granularity,
        )

        self.reset()

    def reset(self):
        """Resets the outage handler to its initial state."""
        self.outage_prob = self._initial_outage_prob
        self.status = self._initial_status
        self.remaining_duration = (
            self._initial_remaining_duration
            if self._initial_status == ElementStatus.OUTAGE
            else 0
        )
        self.usage_time = self._initial_usage_time
        self._outage_type = None

    def _update_usage_time(self) -> None:
        """Updates usage time and outage probability based on element status."""
        if self.status in [ElementStatus.OUTAGE, ElementStatus.MAINTENANCE]:
            return

        if self.status == ElementStatus.ON:
            self.usage_time += 1
            self.outage_prob = self.lambda_factor * self.usage_time

    def _sample_outage(self) -> None:
        """Samples an unplanned outage and assigns a type with duration."""
        if self.status in [ElementStatus.OUTAGE, ElementStatus.MAINTENANCE]:
            return

        if self.rng.random() < self.outage_prob:
            self.status = ElementStatus.OUTAGE
            self._outage_type = self.rng.choice(
                [OutageType.SHORT_TERM, OutageType.MID_TERM, OutageType.LONG_TERM],
                p=[0.50, 0.35, 0.15],
            )

            self.remaining_duration = self.rng.integers(
                self._outage_type.lower_duration, self._outage_type.upper_duration
            )

    def step(self) -> None:
        """Advances the outage state (decreasing remaining durations)."""
        # Update usage time
        self._update_usage_time()

        # Sample outage with correct time step check
        time_step = {"HOUR": 24, "DAY": 7, "WEEK": 1}[self.granularity.name]
        if self.status == ElementStatus.ON and self.usage_time % time_step == 0:
            self._sample_outage()

        # Decrease remaining duration if in outage or maintenance
        if self.status in [ElementStatus.OUTAGE, ElementStatus.MAINTENANCE]:
            self.remaining_duration -= 1
            if self.remaining_duration <= 0:
                self.status = ElementStatus.ON
                self.usage_time = 0
                self.outage_prob = 0.0
                self._outage_type = None

    def send_to_maintenance(self):
        """Initiates planned maintenance, resetting outage probability."""
        if self.status in [ElementStatus.OUTAGE, ElementStatus.MAINTENANCE]:
            return

        self.status = ElementStatus.MAINTENANCE
        self.remaining_duration = self.maintenance_duration
