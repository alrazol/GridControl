import pytest
import os
import json
import requests_mock
from datetime import datetime
from gym.spaces import Space, Box
from src.rl.one_hot_map import OneHotMap
from src.rl.reward.base import BaseReward
from src.rl.action.enums import DiscreteActionTypes
from src.rl.repositories import LoadFlowSolverRepository
from src.core.domain.models.network import Network
from src.core.domain.models.element import NetworkElement
from src.core.infrastructure.settings import Settings
from src.rl.observation.network_snapshot_observation_builder import (
    NetworkSnapshotObservationBuilder,
)
from src.core.domain.ports.network_builder import NetworkBuilder
from src.rl.action.base import BaseAction
from src.core.constants import (
    LoadFlowType,
    State,
    DEFAULT_TIMEZONE,
    SupportedNetworkElementTypes,
)
from src.rl.environment import NetworkEnvironment
from src.rl.action_space import ActionSpace
from src.rl.action.do_nothing import DoNothingAction
from src.rl.observation.network import NetworkSnapshotObservation, NetworkObservation
from src.core.domain.models.elements_metadata.load import (
    LoadMetadata,
    LoadStaticAttributes,
    LoadDynamicAttributes,
    LoadSolvedAttributes,
)
from src.core.utils import generate_hash


def load_json_response(filename):
    """Helper function to load JSON responses from the file system."""
    filepath = os.path.join(os.path.dirname(__file__), "responses", filename)
    with open(filepath, "r") as file:
        return json.load(file)


@pytest.fixture
def tmp_env(monkeypatch) -> Settings:
    """Fixture to temporarily override or set environment variables."""
    env_overrides = {
        "NETWORK_API_BASEURL": "http://test.com",
        "SHOULD_CREATE_TABLES": False,
    }
    for key, value in env_overrides.items():
        monkeypatch.setenv(key, value)

    yield Settings(dict(os.environ))


@pytest.fixture
def mock_requests(tmp_env: Settings, mock_network_id: str):
    """Fixture to mock API requests within a valid environment context."""

    with requests_mock.Mocker() as m:

        def param_matcher(request):
            expected_params = {"network_id": [mock_network_id]}
            return request.qs == expected_params

        base_url = tmp_env.NETWORK_API_BASEURL

        m.get(
            f"{base_url}/get-network",
            json=load_json_response("test_network.json"),
            status_code=200,
            additional_matcher=param_matcher,
        )

        yield m


@pytest.fixture
def mock_network_id() -> str:
    return "some_id"


@pytest.fixture
def mock_network_elements() -> list[NetworkElement]:
    return [
        NetworkElement(
            uid="some_uid",
            id="load_1",
            timestamp=datetime(2024, 1, 1, 0, 0, tzinfo=DEFAULT_TIMEZONE),
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
            id="load_1",
            timestamp=datetime(2024, 1, 2, 0, 0, tzinfo=DEFAULT_TIMEZONE),
            type=SupportedNetworkElementTypes.LOAD,
            element_metadata=LoadMetadata(
                state=State.SOLVED,
                static=LoadStaticAttributes(
                    voltage_level_id="VL1",
                    bus_id="BUS1",
                ),
                dynamic=LoadDynamicAttributes(
                    Pd=30.0,
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
    ]


@pytest.fixture
def mock_network(
    mock_network_elements: list[NetworkElement],
    mock_network_id: str,
) -> Network:
    return Network(
        uid=mock_network_id, id=mock_network_id, elements=mock_network_elements
    )


@pytest.fixture
def mock_initial_network(
    mock_network_elements: list[NetworkElement],
    mock_network_id: str,
) -> Network:
    return Network(
        uid=generate_hash(f"{mock_network_id}_2024-01-01T00:00:00+0000"),
        id=f"{mock_network_id}_2024-01-01T00:00:00+0000",
        elements=[mock_network_elements[0]],
    )


@pytest.fixture
def mock_action_types() -> list[DiscreteActionTypes]:
    return [DiscreteActionTypes.DO_NOTHING]


@pytest.fixture
def mock_loadflow_type() -> LoadFlowType:
    return LoadFlowType.DC


@pytest.fixture
def mock_observation_memory_length() -> int:
    return 1


# @pytest.fixture
# def mock_network(
#    mock_requests: requests_mock.Mocker, mock_network_id: str, tmp_env: Settings
# ) -> Network:
#    _ = mock_requests
#    return (
#        Repositories(s=tmp_env).get_network_repository().get(network_id=mock_network_id)
#    )


@pytest.fixture
def mock_action_space(mock_network: Network) -> ActionSpace:
    return ActionSpace(
        network=mock_network,
        valid_actions=[DoNothingAction()],
        invalid_actions=[],
    )


@pytest.fixture
def mock_observation_space() -> Space:
    return Box(low=1, high=2)


@pytest.fixture
def mock_one_hot_map() -> OneHotMap:
    OneHotMap(
        network_observation=NetworkSnapshotObservation(
            observations=[], timestamp=datetime(2024, 1, 1, tzinfo=DEFAULT_TIMEZONE)
        ),
        types={},
        buses={},
        voltage_levels={},
        statuses={},
        constraint_sides={},
        constraint_types={},
        affected_elements={},
    )


@pytest.fixture
def mock_initial_observation() -> NetworkObservation:
    return NetworkObservation(
        history_length=1,
        network_snapshot_observations=(
            NetworkSnapshotObservation(
                observations=[], timestamp=datetime(2024, 1, 1, tzinfo=DEFAULT_TIMEZONE)
            ),
        ),
    )


@pytest.fixture
def mock_action_for_step() -> BaseAction:
    return DoNothingAction()


class MockRewardHandler(BaseReward):
    def compute_reward(self, network: Network) -> float:
        _ = network
        return 0.0


class MockLoadFlowSolver(LoadFlowSolverRepository):
    def solve(self, network: Network, loadflow_type: LoadFlowType) -> Network:
        _ = loadflow_type
        for element in network.elements:
            if State.SOLVED in element.element_metadata.supported_states:
                element.element_metadata.state = State.SOLVED
        return network


class MockNetworkBuilder(NetworkBuilder):
    def from_elements(self, id: str, elements: list[NetworkElement]) -> Network:
        return Network(
            uid=id,
            id=id,
            elements=[],
        )


class MockNetworkSnapshotObservationBuilder(NetworkSnapshotObservationBuilder):
    def from_network(
        self, network: Network, timestamp: datetime
    ) -> NetworkSnapshotObservation:
        _ = network
        return NetworkSnapshotObservation(observations=[], timestamp=timestamp)


@pytest.fixture
def mock_network_environment(
    mock_network: Network,
    mock_initial_observation: NetworkSnapshotObservation,
    mock_initial_network: Network,
    mock_loadflow_type: LoadFlowType,
    mock_action_space: ActionSpace,
    mock_observation_space: Space,
    mock_one_hot_map: OneHotMap,
) -> NetworkEnvironment:
    return NetworkEnvironment(
        network=mock_network,
        initial_observation=mock_initial_observation,
        initial_network=mock_initial_network,
        loadflow_solver=MockLoadFlowSolver(),
        loadflow_type=mock_loadflow_type,
        action_space=mock_action_space,
        observation_space=mock_observation_space,
        reward_handler=MockRewardHandler(),
        one_hot_map=mock_one_hot_map,
        network_builder=MockNetworkBuilder(),
        network_snapshot_observation_builder=MockNetworkSnapshotObservationBuilder(),
    )


class TestNetworkEnvironment:
    def test_initialisation(
        self,
        mock_network: Network,
        mock_initial_observation: NetworkSnapshotObservation,
        mock_initial_network: Network,
        mock_loadflow_type: LoadFlowType,
        mock_action_space: ActionSpace,
        mock_observation_space: Space,
        mock_one_hot_map: OneHotMap,
    ):
        env = NetworkEnvironment(
            network=mock_network,
            initial_observation=mock_initial_observation,
            initial_network=mock_initial_network,
            loadflow_solver=MockLoadFlowSolver(),
            loadflow_type=mock_loadflow_type,
            action_space=mock_action_space,
            observation_space=mock_observation_space,
            reward_handler=MockRewardHandler(),
            one_hot_map=mock_one_hot_map,
            network_builder=MockNetworkBuilder(),
            network_snapshot_observation_builder=MockNetworkSnapshotObservationBuilder(),
        )
        assert isinstance(env, NetworkEnvironment)
        assert env.network == mock_network
        assert env.initial_observation == mock_initial_observation
        assert env.initial_network == mock_initial_network
        assert env.loadflow_type == mock_loadflow_type
        assert env.action_space == mock_action_space
        assert env.observation_space == mock_observation_space
        assert env.one_hot_map == mock_one_hot_map
        assert isinstance(env.loadflow_solver, MockLoadFlowSolver)
        assert isinstance(env.reward_handler, MockRewardHandler)
        assert isinstance(env.network_builder, MockNetworkBuilder)
        assert isinstance(
            env.network_snapshot_observation_builder,
            MockNetworkSnapshotObservationBuilder,
        )

    def test_reset(
        self,
        mock_network_environment: NetworkEnvironment,
        mock_initial_observation: NetworkObservation,
    ):
        initial_observation, _ = mock_network_environment.reset()
        assert initial_observation == mock_initial_observation
        assert mock_network_environment.current_observation == initial_observation
        assert mock_network_environment.current_network == Network(
            uid=generate_hash(f"{mock_network_environment.initial_network.id}"),
            id=mock_network_environment.initial_network.id,
            elements=mock_network_environment.initial_network.elements,
        )
        assert (
            mock_network_environment.current_timestamp
            == initial_observation.list_network_snapshot_observations()[0].timestamp
        )
        assert mock_network_environment.episode_reward == 0.0
        assert mock_network_environment.is_terminated is False

    # def test_step(
    #     self,
    #     mock_network_environment: NetworkEnvironment,
    #     mock_action_for_step: BaseAction,
    # ):
    #     mock_network_environment.reset()
    #     next_observation, reward, is_terminated, _ = mock_network_environment.step(
    #         action=mock_action_for_step,
    #     )
    #     assert isinstance(next_observation, NetworkObservation)
