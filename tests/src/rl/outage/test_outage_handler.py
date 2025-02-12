import pytest
import numpy as np
from src.rl.enums import Granularity
from src.rl.outage.outage_handler import OutageHandler


@pytest.fixture
def default_outage_handler():
    """Fixture to create a default OutageHandler instance for tests."""
    return OutageHandler(
        element_id="E1",
        initial_outage_prob=0.1,
        initial_is_out=False,
        initial_is_in_maintenance=False,
        initial_remaining_duration=0,
        initial_usage_time=0,
        lambda_factor=0.02,
        lower_duration=2,
        upper_duration=5,
        granularity=Granularity.HOUR,
    )


class TestOutageHandler:
    """Test suite for OutageHandler class."""

    # --- Initialization ---
    def test_initial_conditions(self, default_outage_handler):
        """Test if OutageHandler initializes with correct default values."""
        handler = default_outage_handler
        assert handler.element_id == "E1"
        assert handler.outage_prob == 0.1
        assert handler.is_out is False
        assert handler.is_in_maintenance is False
        assert handler.remaining_duration == 0
        assert handler.usage_time == 0

    # --- Property Tests ---
    def test_outage_prob_limits(self, default_outage_handler):
        """Test if outage probability stays within [0, 1]."""
        handler = default_outage_handler
        handler.outage_prob = 1.5  # Should be capped at 1.0
        assert handler.outage_prob == 1.0

        handler.outage_prob = -0.5  # Should be floored at 0.0
        assert handler.outage_prob == 0.0

    def test_usage_time_limits(self, default_outage_handler):
        """Test that usage time does not go negative."""
        handler = default_outage_handler
        handler.usage_time = -10  # Should be reset to 0
        assert handler.usage_time == 0

    # --- Usage Time Updates ---
    def test_usage_time_increment(self, default_outage_handler):
        """Test that usage time increases correctly when the element is ON."""
        handler = default_outage_handler
        handler.update_usage_time(is_on=True)
        assert handler.usage_time == 1  # Granularity is 1 (hour)
        assert handler.outage_prob == 0.02  # lambda_factor * usage_time

        handler.update_usage_time(is_on=True)
        assert handler.usage_time == 2
        assert handler.outage_prob == 0.04  # 0.02 * 2

    def test_no_usage_increase_when_off(self, default_outage_handler):
        """Test that usage time does not increase when the element is OFF."""
        handler = default_outage_handler
        handler.update_usage_time(is_on=False)
        assert handler.usage_time == 0
        assert handler.outage_prob == 0.1  # No change

    # --- Outage Sampling ---
    def test_sample_outage_triggers(self, default_outage_handler, mocker):
        """Test that an outage occurs when probability is high."""
        handler = default_outage_handler
        handler.outage_prob = 1.0  # Ensure an outage will trigger

        mocker.patch("numpy.random.rand", return_value=0.5)  # Mock random value
        handler.sample_outage()

        assert handler.is_out is True
        assert handler.remaining_duration >= 2  # Must be at least lower_duration
        assert handler.remaining_duration <= 5  # Must be at most upper_duration

    def test_sample_outage_does_not_trigger(self, default_outage_handler, mocker):
        """Test that an outage does not occur when probability is 0."""
        handler = default_outage_handler
        handler.outage_prob = 0.0  # No chance of outage

        mocker.patch("numpy.random.rand", return_value=0.5)  # Mock random value
        handler.sample_outage()

        assert handler.is_out is False

    # --- Step Function Tests ---
    def test_step_reduces_remaining_duration(self, default_outage_handler):
        """Test that step() reduces remaining_duration for outages and maintenance."""
        handler = default_outage_handler
        handler.is_out = True
        handler.remaining_duration = 3

        handler.step()
        assert handler.remaining_duration == 2  # Should decrease

        handler.step()
        assert handler.remaining_duration == 1

        handler.step()
        assert handler.remaining_duration == 0
        assert handler.is_out is False  # Should return to normal

    def test_step_no_change_when_no_outage_or_maintenance(self, default_outage_handler):
        """Test that step() does nothing when element is in normal state."""
        handler = default_outage_handler
        handler.step()  # No outage or maintenance
        assert handler.remaining_duration == 0  # Should remain 0
        assert handler.is_out is False
        assert handler.is_in_maintenance is False

    # --- Maintenance Tests ---
    def test_send_to_maintenance(self, default_outage_handler, mocker):
        """Test that sending an element to maintenance resets probability and usage time."""
        handler = default_outage_handler
        handler.usage_time = 10
        handler.outage_prob = 0.5

        mocker.patch("numpy.random.randint", return_value=4)  # Mock maintenance duration
        handler.send_to_maintenance()

        assert handler.is_in_maintenance is True
        assert handler.remaining_duration == 4  # Mocked duration
        assert handler.usage_time == 0  # Reset
        assert handler.outage_prob == 0.0  # Reset

    def test_no_maintenance_if_already_in_outage(self, default_outage_handler):
        """Test that an element in an outage cannot be sent to maintenance."""
        handler = default_outage_handler
        handler.is_out = True
        handler.remaining_duration = 3

        handler.send_to_maintenance()
        assert handler.is_in_maintenance is False  # Should not enter maintenance
        assert handler.is_out is True  # Should remain in outage

    def test_no_maintenance_if_already_in_maintenance(self, default_outage_handler):
        """Test that an element already in maintenance cannot be re-sent."""
        handler = default_outage_handler
        handler.is_in_maintenance = True
        handler.remaining_duration = 3

        handler.send_to_maintenance()
        assert handler.remaining_duration == 3  # Should not change
