import pytest
import numpy as np
import pandas as pd
import pandas.testing as pdt
from datetime import datetime
from src.rl.observation.network import NetworkObservation
from src.core.domain.models.network import Network
from src.core.domain.models.element import NetworkElement
from src.core.constants import SupportedNetworkElementTypes, ElementStatus
from src.core.domain.models.elements_metadata.line import (
    LineMetadata,
    LineStaticAttributes,
    LineSolvedAttributes,
)
from src.core.domain.models.elements_metadata.load import (
    LoadMetadata,
    LoadStaticAttributes,
    LoadDynamicAttributes,
    LoadSolvedAttributes,
)
from src.core.domain.models.elements_metadata.generator import (
    GeneratorMetadata,
    GeneratorStaticAttributes,
    GeneratorDynamicAttributes,
    GeneratorSolvedAttributes,
)
from src.core.domain.enums import State
from src.rl.observation.one_hot_map import OneHotMap
from src.rl.observation.generator import GeneratorObservation
from src.rl.observation.load import LoadObservation
from src.rl.observation.line import LineObservation


@pytest.fixture
def mock_network_elements():
    """Fixture to create mock NetworkElement objects for a network."""
    return [
        NetworkElement(
            uid="line_uid",
            id="line_1",
            timestamp="2024-01-01T00:00:00+0000",
            type=SupportedNetworkElementTypes.LINE,
            element_metadata=LineMetadata(
                state=State.SOLVED,
                static=LineStaticAttributes(
                    status=ElementStatus.ON,
                    bus1_id="BUS1",
                    bus2_id="BUS2",
                    voltage_level1_id="VL1",
                    voltage_level2_id="VL1",
                    b1=0.01,
                    b2=0.02,
                    g1=0.03,
                    g2=0.04,
                    r=0.05,
                    x=0.06,
                ),
                solved=LineSolvedAttributes(
                    p1=50.0,
                    p2=45.0,
                    i1=10.0,
                    i2=10.0,
                    q1=10.0,
                    q2=10.0,
                ),
            ),
            network_id="network_1",
            operational_constraints=[],
        ),
        NetworkElement(
            uid="some_uid",
            id="load_1",
            timestamp="2024-01-01T00:00:00+0000",
            type=SupportedNetworkElementTypes.LOAD,
            element_metadata=LoadMetadata(
                state=State.SOLVED,
                static=LoadStaticAttributes(
                    voltage_level_id="VL1",
                    bus_id="BUS1",
                ),
                dynamic=LoadDynamicAttributes(
                    Pd=20.0,
                    Qd=10.0,
                ),
                solved=LoadSolvedAttributes(
                    p=20.0,
                    q=10.0,
                ),
            ),
            network_id="network_1",
            operational_constraints=[],
        ),
        NetworkElement(
            uid="some_uid",
            id="gen_1",
            timestamp="2024-01-01T00:00:00+0000",
            type=SupportedNetworkElementTypes.GENERATOR,
            element_metadata=GeneratorMetadata(
                state=State.SOLVED,
                static=GeneratorStaticAttributes(
                    status=ElementStatus.ON,
                    voltage_level_id="VL1",
                    bus_id="BUS2",
                    Pmax=15.0,
                    Pmin=0.0,
                    is_voltage_regulator=True,
                ),
                dynamic=GeneratorDynamicAttributes(
                    Ptarget=10.0,
                    Vtarget=5.0,
                ),
                solved=GeneratorSolvedAttributes(
                    p=10.0,
                    q=5.0,
                    connected=True,
                ),
            ),
            network_id="network_1",
            operational_constraints=[],
        ),
    ]


@pytest.fixture
def mock_observations():
    """Fixture to create mock NetworkObservation objects for a observations."""
    # Order matters
    return [
        GeneratorObservation(
            id="gen_1",
            timestamp=datetime(2024, 1, 1),
            type=SupportedNetworkElementTypes.GENERATOR,
            status=ElementStatus.ON,
            bus_id="BUS1",
            voltage_level_id="VL1",
            Ptarget=10.0,
            active_power=10.0,
            reactive_power=5.0,
        ),
        LineObservation(
            id="line_1",
            timestamp=datetime(2024, 1, 1),
            type=SupportedNetworkElementTypes.LINE,
            status=ElementStatus.ON,
            bus1_id="BUS1",
            bus2_id="BUS2",
            voltage_level1_id="VL1",
            voltage_level2_id="VL2",
            b1=0.01,
            b2=0.02,
            g1=0.03,
            g2=0.04,
            r=0.05,
            x=0.06,
            p1=10.0,
            p2=10.0,
            operational_constraints=[],
        ),
        LoadObservation(
            id="load_1",
            timestamp=datetime(2024, 1, 1),
            type=SupportedNetworkElementTypes.LOAD,
            status=ElementStatus.ON,
            bus_id="BUS1",
            voltage_level_id="VL1",
            Pd=10.0,
            active_power=10.0,
            reactive_power=5.0,
        ),
    ]


@pytest.fixture
def mock_network(mock_network_elements):
    """Fixture to create a mock Network."""
    return Network(uid="network_uid", id="network_name", elements=mock_network_elements)


@pytest.fixture
def mock_network_observation(mock_observations):
    """Fixture to create a mock Network."""
    return NetworkObservation(
        observations=mock_observations, timestamp=datetime(2024, 1, 1)
    )


@pytest.fixture
def mock_one_hot_map(mock_network_observation):
    """Fixture to create mock one-hot encoding maps."""
    return OneHotMap(
        network_observation=mock_network_observation,
        types={
            SupportedNetworkElementTypes.GENERATOR: np.array([1, 0, 0]),
            SupportedNetworkElementTypes.LOAD: np.array([0, 1, 0]),
            SupportedNetworkElementTypes.LINE: np.array([0, 0, 1]),
        },
        buses={
            "BUS1": np.array([1, 0]),
            "BUS2": np.array([0, 1]),
        },
        voltage_levels={
            "VL1": np.array([1, 0]),
            "VL2": np.array([0, 1]),
        },
        statuses={
            ElementStatus.OFF: np.array([1, 0]),
            ElementStatus.ON: np.array([0, 1]),
        },
        constraint_sides={},
        constraint_types={},
        affected_elements={},
    )


class TestNetworkObservation:
    """Test suite for NetworkState."""

    def test_from_network(self, mock_network):
        """Test creation of NetworkState from a Network object."""
        obs = NetworkObservation.from_network(mock_network, timestamp=datetime(2024, 1, 1))
        assert len(obs.observations) == 3
        # Sorting by id...
        assert isinstance(obs.observations[0], GeneratorObservation)
        assert isinstance(obs.observations[1], LineObservation)
        assert isinstance(obs.observations[2], LoadObservation)

    def test_to_array(self, mock_network_observation, mock_one_hot_map):
        """Test conversion of NetworkState to a flat array."""

        array = mock_network_observation.to_array(mock_one_hot_map)
        assert array.ndim == 1  # Flat array
        assert array.size > 0  # Should not be empty
        # TODO: Further testing of values in it

    def test_to_dataframe(self, mock_network_observation: NetworkObservation):
        """Test conversion of NetworkState to a flat array."""
        expected_outcome = {
            "GENERATOR": pd.DataFrame(
                data={
                    "id": [mock_network_observation.observations[0].id],
                    "timestamp": [mock_network_observation.observations[0].timestamp],
                    "type": [mock_network_observation.observations[0].type],
                    "status": [mock_network_observation.observations[0].status],
                    "bus_id": [mock_network_observation.observations[0].bus_id],
                    "voltage_level_id": [
                        mock_network_observation.observations[0].voltage_level_id
                    ],
                    "Ptarget": [mock_network_observation.observations[0].Ptarget],
                    "active_power": [
                        mock_network_observation.observations[0].active_power
                    ],
                    "reactive_power": [
                        mock_network_observation.observations[0].reactive_power
                    ],
                }
            ),
            "LINE": pd.DataFrame(
                data={
                    "id": [mock_network_observation.observations[1].id],
                    "timestamp": [mock_network_observation.observations[1].timestamp],
                    "type": [mock_network_observation.observations[1].type],
                    "status": [mock_network_observation.observations[1].status],
                    "bus1_id": [mock_network_observation.observations[1].bus1_id],
                    "bus2_id": [mock_network_observation.observations[1].bus2_id],
                    "voltage_level1_id": [
                        mock_network_observation.observations[1].voltage_level1_id
                    ],
                    "voltage_level2_id": [
                        mock_network_observation.observations[1].voltage_level2_id
                    ],
                    "p1": [mock_network_observation.observations[1].p1],
                    "p2": [mock_network_observation.observations[1].p2],
                }
            ),
            "LOAD": pd.DataFrame(
                data={
                    "id": [mock_network_observation.observations[2].id],
                    "timestamp": [mock_network_observation.observations[2].timestamp],
                    "type": [mock_network_observation.observations[2].type],
                    "status": [mock_network_observation.observations[2].status],
                    "bus_id": [mock_network_observation.observations[2].bus_id],
                    "voltage_level_id": [
                        mock_network_observation.observations[2].voltage_level_id
                    ],
                    "Pd": [mock_network_observation.observations[2].Pd],
                    "active_power": [
                        mock_network_observation.observations[2].active_power
                    ],
                    "reactive_power": [
                        mock_network_observation.observations[2].reactive_power
                    ],
                }
            ),
        }
        dfs = mock_network_observation.to_dataframe()
        for k, _ in dfs.items():
            pdt.assert_frame_equal(expected_outcome[k], dfs[k])
