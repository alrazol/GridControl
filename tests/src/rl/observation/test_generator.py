import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from src.core.constants import SupportedNetworkElementTypes
from src.core.domain.models.element import NetworkElement
from src.core.domain.models.elements_metadata.generator import (
    GeneratorMetadata,
    GeneratorStaticAttributes,
    GeneratorDynamicAttributes,
    GeneratorSolvedAttributes,
)
from src.rl.observation.generator import GeneratorObservation
from src.rl.observation.network import NetworkObservation
from src.core.domain.enums import State
from src.core.constants import ElementStatus
from src.rl.observation.one_hot_map import OneHotMap
import pandas.testing as pdt


@pytest.fixture
def mock_generator_element():
    """Fixture to create a mock NetworkElement for a generator."""
    return NetworkElement(
        uid="some_uid",
        id="gen_1",
        timestamp="2024-01-01T00:00:00+0000",
        type=SupportedNetworkElementTypes.GENERATOR,
        element_metadata=GeneratorMetadata(
            state=State.SOLVED,
            static=GeneratorStaticAttributes(
                status=ElementStatus.ON,
                voltage_level_id="VL1",
                bus_id="BUS1",
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
    )


@pytest.fixture
def mock_generator_observation():
    return GeneratorObservation(
        id="gen_1",
        timestamp=datetime(2024, 1, 1),
        type=SupportedNetworkElementTypes.GENERATOR,
        status=ElementStatus.ON,
        bus_id="BUS1",
        voltage_level_id="VL1",
        Ptarget=10.0,
        active_power=10.0,
        reactive_power=5.0,
    )


@pytest.fixture
def mock_network_observation(mock_generator_observation):
    return NetworkObservation(
        observations=[mock_generator_observation], timestamp=datetime(2024, 1, 1)
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
            ElementStatus.ON: np.array([0, 1]),
            ElementStatus.OFF: np.array([1, 0]),
        },
        constraint_sides={},
        constraint_types={},
        affected_elements={},
    )


class TestGeneratorObservation:
    def test_from_element(self, mock_generator_element: NetworkElement):
        """Test creation of GeneratorState from a NetworkElement."""
        obs = GeneratorObservation.from_element(mock_generator_element)
        assert obs.type == SupportedNetworkElementTypes.GENERATOR
        assert obs.bus_id == "BUS1"
        assert obs.voltage_level_id == "VL1"
        assert obs.active_power == 10.0
        assert obs.reactive_power == 5.0
        assert obs.id == "gen_1"
        assert isinstance(obs, GeneratorObservation)

    @pytest.mark.parametrize(
        "bus_id, expected",
        [
            ("BUS1", ["BUS1"]),
            ("BUS2", ["BUS2"]),
        ],
    )
    def test_get_bus_ids(
        self, mock_generator_element: NetworkElement, bus_id, expected
    ):
        """Test getting bus IDs."""
        mock_generator_element.element_metadata.static.bus_id = bus_id
        obs = GeneratorObservation.from_element(mock_generator_element)
        assert obs.bus_ids == expected

    @pytest.mark.parametrize(
        "voltage_level_id, expected",
        [
            ("VL1", ["VL1"]),
            ("VL2", ["VL2"]),
        ],
    )
    def test_get_voltage_level_ids(
        self, mock_generator_element: NetworkElement, voltage_level_id, expected
    ):
        """Test getting voltage level IDs."""
        mock_generator_element.element_metadata.static.voltage_level_id = (
            voltage_level_id
        )
        obs = GeneratorObservation.from_element(mock_generator_element)
        assert obs.voltage_level_ids == expected

    def test_to_array(
        self,
        mock_generator_observation: GeneratorObservation,
        mock_one_hot_map: OneHotMap,
    ):
        """Test conversion of obs to a flat array."""
        expected_array = np.concatenate(
            [
                mock_one_hot_map.types[SupportedNetworkElementTypes.GENERATOR],
                mock_one_hot_map.buses["BUS1"],
                mock_one_hot_map.voltage_levels["VL1"],
                mock_one_hot_map.statuses[ElementStatus.ON],
                [10.0, 5.0, 10.0],
            ]
        )
        result_array = mock_generator_observation.to_array(one_hot_map=mock_one_hot_map)
        np.testing.assert_array_equal(result_array, expected_array)

    def test_to_dataframe(
        self,
        mock_generator_observation: GeneratorObservation,
        mock_one_hot_map: OneHotMap,
    ):
        """Test conversion of obs to a pd.DataFrame."""
        expected_data = {
            "id": ["gen_1"],
            "timestamp": [datetime(2024, 1, 1)],
            "type": [SupportedNetworkElementTypes.GENERATOR],
            "status": [ElementStatus.ON],
            "bus_id": ["BUS1"],
            "voltage_level_id": ["VL1"],
            "Ptarget": [10.0],
            "active_power": [10.0],
            "reactive_power": [5.0],
        }
        expected_df = pd.DataFrame(data=expected_data)
        df = mock_generator_observation.to_dataframe()
        pdt.assert_frame_equal(df, expected_df)

# TODO: Add a test with math nan as active power etc...
