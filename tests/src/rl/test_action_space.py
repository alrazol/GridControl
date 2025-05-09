import pytest
from datetime import datetime
from gym.spaces import Discrete
from src.core.constants import DEFAULT_TIMEZONE
from src.core.domain.models.network import Network
from src.core.domain.models.element import NetworkElement
from src.rl.action import DoNothingAction
from src.rl.action.enums import DiscreteActionTypes
from src.rl.action_space import ActionSpace
from src.core.constants import SupportedNetworkElementTypes
from src.core.domain.enums import State
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
from src.core.constants import ElementStatus


@pytest.fixture
def mock_network_elements() -> list[NetworkElement]:
    """Fixture to create mock NetworkElement objects for a network."""
    return [
        NetworkElement(
            uid="line_uid",
            id="line_1",
            timestamp=datetime(2024, 1, 1, tzinfo=DEFAULT_TIMEZONE),
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
            timestamp=datetime(2024, 1, 1, tzinfo=DEFAULT_TIMEZONE),
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
            timestamp=datetime(2024, 1, 1, tzinfo=DEFAULT_TIMEZONE),
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
def mock_network(mock_network_elements: list[NetworkElement]) -> Network:
    return Network(uid="network_uid", id="network_name", elements=mock_network_elements)


@pytest.fixture
def mock_action_types() -> list[DiscreteActionTypes]:
    return [DiscreteActionTypes.DO_NOTHING, DiscreteActionTypes.SWITCH]


class TestActionSpace:
    def test_to_gym_discrete(self, mock_network):
        """Test gym conversion when only discrete actions are present."""
        action_space = ActionSpace(
            valid_actions=[DoNothingAction()], invalid_actions=[]
        )
        gym_space = action_space.to_gym()

        assert isinstance(gym_space, Discrete)
        assert gym_space.n == 1
