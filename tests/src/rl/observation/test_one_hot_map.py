import pytest
import numpy as np
from src.core.constants import ElementStatus
from src.core.constants import SupportedNetworkElementTypes
from datetime import datetime
from src.rl.observation.generator import GeneratorObservation
from src.rl.observation.load import LoadObservation
from src.rl.observation.line import LineObservation
from src.rl.observation.network import NetworkObservation
from src.rl.observation.one_hot_map import OneHotMap


@pytest.fixture
def generator_observation() -> GeneratorObservation:
    return GeneratorObservation(
        id="gen1",
        timestamp=datetime(2024, 1, 1),
        type=SupportedNetworkElementTypes.GENERATOR,
        status=ElementStatus.ON,
        bus_id="bus1",
        voltage_level_id="vl1",
        Ptarget=10.0,
        active_power=9.0,
        reactive_power=5.0,
    )


@pytest.fixture
def load_observation() -> LoadObservation:
    return LoadObservation(
        id="load1",
        timestamp=datetime(2024, 1, 1),
        type=SupportedNetworkElementTypes.LOAD,
        status=ElementStatus.ON,
        bus_id="bus2",
        voltage_level_id="vl1",
        Pd=10.0,
        active_power=9.0,
        reactive_power=5.0,
    )


@pytest.fixture
def line_observation() -> LineObservation:
    return LineObservation(
        id="line1",
        timestamp=datetime(2024, 1, 1),
        type=SupportedNetworkElementTypes.LINE,
        status=ElementStatus.ON,
        bus1_id="bus1",
        bus2_id="bus2",
        voltage_level1_id="vl1",
        voltage_level2_id="vl1",
        b1=0.1,
        b2=0.1,
        g1=0.1,
        g2=0.1,
        r=0.1,
        x=0.1,
        p1=10.0,
        p2=10.0,
        operational_constraints=[
            {
                "affected_element": "line1",
                "side": "TWO",
                "type": "ACTIVE_POWER",
                "value": 10,
            }
        ],
    )


@pytest.fixture
def network_observation(
    generator_observation, load_observation, line_observation
) -> NetworkObservation:
    return NetworkObservation(
        observations=[generator_observation, load_observation, line_observation],
        timestamp=datetime(2024, 1, 1),
    )


class TestOneHotMap:
    def test_from_network_observation(self, network_observation):
        """Test the construction of the map from a NetworkObservation."""
        one_hot_map = OneHotMap.from_network_observation(
            network_observation=network_observation
        )

        assert np.array_equal(one_hot_map.buses["bus1"], np.array([1, 0]))
        assert np.array_equal(one_hot_map.buses["bus2"], np.array([0, 1]))
        assert np.array_equal(one_hot_map.voltage_levels["vl1"], np.array([1]))
        assert np.array_equal(one_hot_map.statuses[ElementStatus.ON], np.array([0, 1]))
        assert np.array_equal(one_hot_map.statuses[ElementStatus.OFF], np.array([1, 0]))
