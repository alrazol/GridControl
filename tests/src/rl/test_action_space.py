import pytest
from datetime import datetime
from gym.spaces import Discrete
from src.core.constants import DEFAULT_TIMEZONE
from src.core.domain.models.network import Network
from src.core.domain.models.element import NetworkElement
from src.rl.action import BaseAction
from src.rl.action.enums import DiscreteActionTypes
from src.rl.action_space import ActionSpace
from src.rl.action import DoNothingAction, SwitchAction
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
    def test_instantiation(
        self,
        mock_network: Network,
        mock_action_types: list[DiscreteActionTypes],
    ):
        """Test that ActionSpace correctly instantiates from action types."""
        action_space = ActionSpace.from_action_types(
            action_types=mock_action_types, network=mock_network
        )

        assert isinstance(action_space, ActionSpace)
        assert len(action_space.valid_actions) > 0
        assert all(isinstance(a, BaseAction) for a in action_space.valid_actions)

    def test_no_duplicate_actions(
        self,
        mock_network: Network,
        mock_action_types: list[DiscreteActionTypes],
    ):
        """Ensure that duplicate actions raise an error."""
        duplicate_actions = mock_action_types + [DiscreteActionTypes.SWITCH]
        with pytest.raises(
            ValueError, match="Some actions in the list are duplicated."
        ):
            ActionSpace.from_action_types(duplicate_actions, mock_network)

    def test_unique_timestamp_violation(
        self, mock_network_elements: list[NetworkElement]
    ):
        """Test that an ActionSpace cannot be built from a multi-timestamp network."""
        network = Network(
            uid="some_uid",
            id="some_id",
            elements=mock_network_elements
            + [
                NetworkElement(
                    uid="some_uid",
                    id="gen_2",
                    timestamp=datetime(2024, 1, 1, 2, 0, tzinfo=DEFAULT_TIMEZONE),
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
                )
            ],
        )
        with pytest.raises(ValueError, match="Can't have more than one timestamp"):
            ActionSpace.from_action_types([DiscreteActionTypes.SWITCH], network)

    def test_action_validation(
        self, mock_network: Network, mock_actions: list[BaseAction]
    ):
        """Test that valid actions are correctly separated from invalid ones."""
        valid_actions, invalid_actions = mock_actions

        action_space = ActionSpace(
            network=mock_network,
            valid_actions=valid_actions,
            invalid_actions=invalid_actions,
        )

        assert len(action_space.valid_actions) == len(valid_actions)
        assert len(action_space.invalid_actions) == len(invalid_actions)

    def test_from_action_types(
        self,
        mock_action_types: list[DiscreteActionTypes],
        mock_network: Network,
    ):
        """Test the ActionSpace from_action_types() pipeline e2e."""
        expected_valid_actions = [DoNothingAction(), SwitchAction(element_id="line_1")]
        expected_invalid_actions = [
            SwitchAction(element_id="load_1"),
            SwitchAction(element_id="gen_1"),
        ]
        expected_action_space = ActionSpace(
            network=mock_network,
            valid_actions=expected_valid_actions,
            invalid_actions=expected_invalid_actions,
        )
        action_space = ActionSpace.from_action_types(
            action_types=mock_action_types, network=mock_network
        )
        assert expected_action_space.valid_actions == action_space.valid_actions
        assert expected_action_space.invalid_actions == action_space.invalid_actions
        assert expected_action_space.network == action_space.network

    def test_to_gym_discrete(self, mock_network):
        """Test gym conversion when only discrete actions are present."""
        action_space = ActionSpace(
            network=mock_network, valid_actions=[DoNothingAction()], invalid_actions=[]
        )
        gym_space = action_space.to_gym()

        assert isinstance(gym_space, Discrete)
        assert gym_space.n == 1
