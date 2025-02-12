import pytest
import numpy as np
import pandas as pd
import pandas.testing as pdt
from datetime import datetime
from src.rl.one_hot_map import OneHotMap
from src.core.constants import SupportedNetworkElementTypes, ElementStatus
from src.core.domain.models.element import NetworkElement
from src.core.domain.models.elements_metadata.line import (
    LineMetadata,
    LineStaticAttributes,
    LineSolvedAttributes,
)
from src.rl.observation.line import LineObservation
from src.rl.observation.network import NetworkSnapshotObservation
from src.core.domain.enums import State, BranchSide, OperationalConstraintType
from src.core.constants import DEFAULT_TIMEZONE


@pytest.fixture
def mock_line_element():
    """Fixture to create a mock NetworkElement for a line."""
    return NetworkElement(
        uid="line_uid",
        id="line_1",
        timestamp=datetime(
            2024,
            1,
            1,
            0,
            0,
            tzinfo=DEFAULT_TIMEZONE,
        ),
        type=SupportedNetworkElementTypes.LINE,
        element_metadata=LineMetadata(
            state=State.SOLVED,
            static=LineStaticAttributes(
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
    )


@pytest.fixture
def mock_line_observation():
    """Fixture to create a mock LineObservation."""
    return LineObservation(
        id="line_1",
        timestamp=datetime(
            2024,
            1,
            1,
            0,
            0,
            tzinfo=DEFAULT_TIMEZONE,
        ),
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
        p1=50.0,
        p2=45.0,
        operational_constraints=[],
    )


@pytest.fixture
def mock_line_observation_with_constraint():
    """Fixture to create a mock LineObservation."""
    return LineObservation(
        id="line_1",
        timestamp=datetime(
            2024,
            1,
            1,
            0,
            0,
            tzinfo=DEFAULT_TIMEZONE,
        ),
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
        p1=50.0,
        p2=45.0,
        operational_constraints=[
            {
                "side": BranchSide.TWO,
                "type": OperationalConstraintType.ACTIVE_POWER,
                "affected_element": "line_1",
                "value": 10.0,
            }
        ],
    )


@pytest.fixture
def mock_network_observation(mock_line_observation):
    return NetworkSnapshotObservation(
        timestamp=datetime(
            2024,
            1,
            1,
            0,
            0,
            tzinfo=DEFAULT_TIMEZONE,
        ),
        observations=[mock_line_observation],
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
        constraint_sides={
            BranchSide.TWO: np.array([1, 0, 0]),
            BranchSide.ONE: np.array([0, 1, 0]),
            BranchSide.THREE: np.array([0, 0, 1]),
        },
        constraint_types={
            OperationalConstraintType.ACTIVE_POWER: np.array([1, 0, 0]),
            OperationalConstraintType.APPARENT_POWER: np.array([0, 1, 0]),
            OperationalConstraintType.CURRENT: np.array([0, 0, 1]),
        },
        affected_elements={"line_1": np.array([1])},
    )


class TestLineObservation:
    """Test suite for LineState."""

    def test_from_element(self, mock_line_element: NetworkElement):
        """Test creation of LineState from a NetworkElement."""
        obs = LineObservation.from_element(mock_line_element)
        assert obs.type == SupportedNetworkElementTypes.LINE
        assert obs.status == ElementStatus.ON
        assert obs.bus1_id == "BUS1"
        assert obs.bus2_id == "BUS2"
        assert obs.voltage_level1_id == "VL1"
        assert obs.voltage_level2_id == "VL2"
        assert obs.b1 == 0.01
        assert obs.b2 == 0.02
        assert obs.g1 == 0.03
        assert obs.g2 == 0.04
        assert obs.r == 0.05
        assert obs.x == 0.06
        assert obs.p1 == 50.0
        assert obs.p2 == 45.0
        assert obs.id == "line_1"

    def test_bus_ids(self, mock_line_element: NetworkElement):
        """Test the bus_ids property."""
        obs = LineObservation.from_element(mock_line_element)
        assert obs.bus_ids == ["BUS1", "BUS2"]

    def test_voltage_level_ids(self, mock_line_element: NetworkElement):
        """Test the voltage_level_ids property."""
        obs = LineObservation.from_element(mock_line_element)
        assert obs.voltage_level_ids == ["VL1", "VL2"]

    def test_to_array(
        self, mock_line_observation: LineObservation, mock_one_hot_map: OneHotMap
    ):
        """Test conversion of state to a flat array."""
        expected_array = np.concatenate(
            [
                mock_one_hot_map.types[SupportedNetworkElementTypes.LINE],
                mock_one_hot_map.statuses[ElementStatus.ON],
                mock_one_hot_map.buses["BUS1"],
                mock_one_hot_map.buses["BUS2"],
                mock_one_hot_map.voltage_levels["VL1"],
                mock_one_hot_map.voltage_levels["VL2"],
                [50.0, 45.0],
            ]
        )
        result_array = mock_line_observation.to_array(one_hot_map=mock_one_hot_map)
        np.testing.assert_array_equal(result_array, expected_array)

    def test_to_dataframe(
        self,
        mock_line_observation: LineObservation,
    ):
        """Test conversion of obs to a pd.DataFrame."""
        expected_data = {
            "id": ["line_1"],
            "timestamp": [
                datetime(
                    2024,
                    1,
                    1,
                    0,
                    0,
                    tzinfo=DEFAULT_TIMEZONE,
                ),
            ],
            "type": [SupportedNetworkElementTypes.LINE],
            "status": [ElementStatus.ON],
            "bus1_id": ["BUS1"],
            "bus2_id": ["BUS2"],
            "voltage_level1_id": ["VL1"],
            "voltage_level2_id": ["VL2"],
            "p1": [50.0],
            "p2": [45.0],
        }
        expected_df = pd.DataFrame(data=expected_data)
        df = mock_line_observation.to_dataframe()
        pdt.assert_frame_equal(df, expected_df)

    def test_to_array_with_constraint(
        self,
        mock_line_observation_with_constraint: LineObservation,
        mock_one_hot_map: OneHotMap,
    ):
        """Test conversion of state to a flat array."""
        expected_array = np.concatenate(
            [
                mock_one_hot_map.types[SupportedNetworkElementTypes.LINE],
                mock_one_hot_map.statuses[ElementStatus.ON],
                mock_one_hot_map.buses["BUS1"],
                mock_one_hot_map.buses["BUS2"],
                mock_one_hot_map.voltage_levels["VL1"],
                mock_one_hot_map.voltage_levels["VL2"],
                [50.0, 45.0],
                mock_one_hot_map.constraint_sides[BranchSide.TWO],
                mock_one_hot_map.constraint_types[
                    OperationalConstraintType.ACTIVE_POWER
                ],
                mock_one_hot_map.affected_elements["line_1"],
                [10.0],
            ]
        )
        result_array = mock_line_observation_with_constraint.to_array(
            one_hot_map=mock_one_hot_map
        )
        np.testing.assert_array_equal(result_array, expected_array)

    def test_to_dataframe_with_constraints(
        self,
        mock_line_observation_with_constraint: LineObservation,
    ):
        """Test conversion of obs to a pd.DataFrame."""
        expected_data = {
            "id": ["line_1"],
            "timestamp": [
                datetime(
                    2024,
                    1,
                    1,
                    0,
                    0,
                    tzinfo=DEFAULT_TIMEZONE,
                ),
            ],
            "type": [SupportedNetworkElementTypes.LINE],
            "status": [ElementStatus.ON],
            "bus1_id": ["BUS1"],
            "bus2_id": ["BUS2"],
            "voltage_level1_id": ["VL1"],
            "voltage_level2_id": ["VL2"],
            "p1": [50.0],
            "p2": [45.0],
            "constraint_0_type": [OperationalConstraintType.ACTIVE_POWER],
            "constraint_0_value": [10.0],
        }
        expected_df = pd.DataFrame(data=expected_data)
        df = mock_line_observation_with_constraint.to_dataframe()
        pdt.assert_frame_equal(df, expected_df)
