import pytest
from datetime import datetime

from src.rl.repositories.network_observation_handler import (
    DefaultNetworkObservationHandler,
)
from src.rl.observation.network import NetworkObservation, NetworkSnapshotObservation
from src.core.constants import DEFAULT_TIMEZONE


@pytest.fixture
def mock_history_length():
    return 2


@pytest.fixture
def mock_network_snapshot_observations() -> NetworkSnapshotObservation:
    return [
        NetworkSnapshotObservation(
            observations=[],
            timestamp=datetime(2024, 1, 1, 0, 0, tzinfo=DEFAULT_TIMEZONE),
        ),
        NetworkSnapshotObservation(
            observations=[],
            timestamp=datetime(2024, 1, 2, 0, 0, tzinfo=DEFAULT_TIMEZONE),
        ),
        NetworkSnapshotObservation(
            observations=[],
            timestamp=datetime(2024, 1, 3, 0, 0, tzinfo=DEFAULT_TIMEZONE),
        ),
        NetworkSnapshotObservation(
            observations=[],
            timestamp=datetime(2024, 1, 4, 0, 0, tzinfo=DEFAULT_TIMEZONE),
        ),
    ]


@pytest.fixture
def mock_network_observation(
    mock_history_length: int,
) -> NetworkObservation:
    return NetworkObservation(history_length=mock_history_length)


class TestNetworkObservationHandler:
    def test_init_network_observation(self):
        """Test initializing a new NetworkObservation instance."""
        history_length = 2
        new_network_observation = (
            DefaultNetworkObservationHandler().init_network_observation(
                history_length=history_length
            )
        )
        assert isinstance(new_network_observation, NetworkObservation)
        assert new_network_observation.history_length == history_length
        assert len(new_network_observation.network_snapshot_observations) == 0

    def test_add_network_snapshot(
        self,
        mock_network_observation: NetworkObservation,
        mock_network_snapshot_observations: list[NetworkSnapshotObservation],
    ):
        """Test adding snapshots maintains history_length and orders correctly."""
        new_network_observation = mock_network_observation
        for i, snapshot in enumerate(mock_network_snapshot_observations):
            new_network_observation = (
                DefaultNetworkObservationHandler().add_network_snapshot_observation(
                    network_observation=new_network_observation,
                    network_snapshot_observation=snapshot,
                )
            )
            # 1 snapshot is added at each iteration, but can't be > 2
            assert len(new_network_observation.network_snapshot_observations) == min(
                i + 1, 2
            )

        assert (
            new_network_observation.network_snapshot_observations[0]
            == mock_network_snapshot_observations[2]
        )
        assert (
            new_network_observation.network_snapshot_observations[1]
            == mock_network_snapshot_observations[3]
        )  # Most recent
