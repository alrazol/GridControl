import pytest
import os
import json
import requests_mock
from src.rl.one_hot_map import OneHotMap
from src.rl.reward.base import BaseReward
from src.rl.action.enums import DiscreteActionTypes
from src.rl.repositories import LoadFlowSolverRepository
from src.core.domain.models.network import Network
from src.core.infrastructure.settings import Settings
from src.rl.repositories import Repositories
from src.core.constants import LoadFlowType, State
from src.rl.environment import NetworkEnvironment
from src.rl.action_space import ActionSpace
from src.rl.action.do_nothing import DoNothingAction


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
def mock_action_types() -> list[DiscreteActionTypes]:
    return [DiscreteActionTypes.DO_NOTHING, DiscreteActionTypes.SWITCH]


@pytest.fixture
def mock_loadflow_type() -> LoadFlowType:
    return LoadFlowType.DC


@pytest.fixture
def mock_observation_memory_length() -> int:
    return 1


@pytest.fixture
def mock_network(
    mock_requests: requests_mock.Mocker, mock_network_id: str, tmp_env: Settings
) -> Network:
    _ = mock_requests
    return (
        Repositories(s=tmp_env).get_network_repository().get(network_id=mock_network_id)
    )


@pytest.fixture
def mock_action_space(mock_network: Network) -> ActionSpace:
    return ActionSpace(
        network=mock_network,
        valid_actions=[DoNothingAction()],
        invalid_actions=[],
    )


@pytest.fixture
def mock_one_hot_map(mock_network: Network) -> OneHotMap:
    pass


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


class TestNetworkEnvironment:
    def test_initialisation(
        self,
        mock_network: Network,
        mock_loadflow_type: LoadFlowType,
        mock_action_types: list[DiscreteActionTypes],
        mock_observation_memory_length: int,
    ):
        env = NetworkEnvironment(
            network=mock_network,
            loadflow_solver=MockLoadFlowSolver(),
            loadflow_type=mock_loadflow_type,
            reward_handler=MockRewardHandler(),
            action_types=mock_action_types,
            observation_memory_length=mock_observation_memory_length,
        )
        assert isinstance(env, NetworkEnvironment)

    def test_reset(
        self,
        tmp_env: Settings,
        mock_requests: requests_mock.Mocker,
        mock_network_id: str,
        mock_loadflow_type: LoadFlowType,
        mock_action_types: list[DiscreteActionTypes],
        mock_observation_memory_length: int,
    ):
        """Test the creation of a NetworkEnvironment from a network_id."""

        _ = mock_requests

        env = NetworkEnvironment.from_network_id(
            network_id=mock_network_id,
            network_repository=Repositories(s=tmp_env).get_network_repository(),
            loadflow_solver=MockLoadFlowSolver(),
            loadflow_type=mock_loadflow_type,
            reward_handler=MockRewardHandler(),
            action_types=mock_action_types,
            observation_memory_length=mock_observation_memory_length,
        )
        assert isinstance(env, NetworkEnvironment)
