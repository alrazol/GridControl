import pytest
import numpy as np
import pandas as pd
import pandas.testing as pdt
from datetime import datetime
from src.core.constants import ElementStatus, SupportedNetworkElementTypes
from src.core.domain.models.element import NetworkElement
from src.core.domain.models.elements_metadata.load import (
    LoadMetadata,
    LoadStaticAttributes,
    LoadSolvedAttributes,
    LoadDynamicAttributes,
)
from src.rl.observation.load import LoadObservation
from src.core.domain.enums import State
from src.rl.observation.one_hot_map import OneHotMap
from src.rl.observation.network import NetworkObservation


@pytest.fixture
def mock_load_element():
    """Fixture to create a mock NetworkElement for a load."""
    return NetworkElement(
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
    )


@pytest.fixture
def mock_load_observation():
    """Fixture to create a mock LoadObservation."""
    return LoadObservation(
        id="load_1",
        timestamp=datetime(2024, 1, 1),
        type=SupportedNetworkElementTypes.LOAD,
        status=ElementStatus.ON,
        bus_id="BUS1",
        voltage_level_id="VL1",
        Pd=10.0,
        active_power=10.0,
        reactive_power=5.0,
    )


@pytest.fixture
def mock_network_observation(mock_load_observation):
    return NetworkObservation(
        observations=[mock_load_observation], timestamp=datetime(2024, 1, 1)
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


class TestLoadObservation:
    """Test suite for LoadState."""

    def test_from_element(self, mock_load_element: NetworkElement):
        """Test creation of LoadState from a NetworkElement."""
        obs = LoadObservation.from_element(mock_load_element)
        assert obs.type == SupportedNetworkElementTypes.LOAD
        assert obs.status == ElementStatus.ON
        assert obs.bus_id == "BUS1"
        assert obs.voltage_level_id == "VL1"
        assert obs.active_power == 20.0
        assert obs.reactive_power == 10.0
        assert obs.id == "load_1"

    @pytest.mark.parametrize(
        "bus_id, expected",
        [
            ("BUS1", ["BUS1"]),
            ("BUS2", ["BUS2"]),
        ],
    )
    def test_bus_ids(self, mock_load_element: NetworkElement, bus_id, expected):
        """Test getting bus IDs."""
        mock_load_element.element_metadata.static.bus_id = bus_id
        obs = LoadObservation.from_element(mock_load_element)
        assert obs.bus_ids == expected

    @pytest.mark.parametrize(
        "voltage_level_id, expected",
        [
            ("VL1", ["VL1"]),
            ("VL2", ["VL2"]),
        ],
    )
    def test_voltage_level_ids(
        self, mock_load_element: NetworkElement, voltage_level_id, expected
    ):
        """Test getting voltage level IDs."""
        mock_load_element.element_metadata.static.voltage_level_id = voltage_level_id
        obs = LoadObservation.from_element(mock_load_element)
        assert obs.voltage_level_ids == expected

    def test_to_array(
        self, mock_load_observation: LoadObservation, mock_one_hot_map: OneHotMap
    ):
        """Test conversion of state to a flat array."""
        expected_array = np.concatenate(
            [
                mock_one_hot_map.types[SupportedNetworkElementTypes.LOAD],
                mock_one_hot_map.buses["BUS1"],
                mock_one_hot_map.voltage_levels["VL1"],
                mock_one_hot_map.statuses[ElementStatus.ON],
                [10.0, 10.0, 5.0],
            ]
        )
        result_array = mock_load_observation.to_array(one_hot_map=mock_one_hot_map)
        np.testing.assert_array_equal(result_array, expected_array)

    def test_to_dataframe(
        self,
        mock_load_observation: LoadObservation,
    ):
        """Test conversion of obs to a pd.DataFrame."""
        expected_data = {
            "id": ["load_1"],
            "timestamp": [datetime(2024, 1, 1)],
            "type": [SupportedNetworkElementTypes.LOAD],
            "status": [ElementStatus.ON],
            "bus_id": ["BUS1"],
            "voltage_level_id": ["VL1"],
            "Pd": [10.0],
            "active_power": [10.0],
            "reactive_power": [5.0],
        }
        expected_df = pd.DataFrame(data=expected_data)
        df = mock_load_observation.to_dataframe()
        pdt.assert_frame_equal(df, expected_df)
