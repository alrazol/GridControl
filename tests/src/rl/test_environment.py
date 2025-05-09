import pytest
import os
import json
import requests_mock
from datetime import datetime
from gym.spaces import Space, Box
from src.rl.one_hot_map import OneHotMap
from src.rl.reward.reward_handler import RewardHandler
from src.rl.reward.base import BaseReward
from src.rl.action.enums import DiscreteActionTypes
from src.rl.repositories import LoadFlowSolverRepository
from src.rl.repositories.network_transition_handler import NetworkTransitionHandler
from src.rl.observation.network_observation_handler import NetworkObservationHandler
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
from src.rl.observation.load import LoadObservation
from src.core.constants import ElementStatus


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
            timestamp=datetime(2024, 1, 1, 1, 0, tzinfo=DEFAULT_TIMEZONE),
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
    network = Network(
        uid=mock_network_id, id=mock_network_id, elements=mock_network_elements
    )
    network.timestamps = network.list_timestamps()
    return network


@pytest.fixture
def mock_initial_network(
    mock_network_elements: list[NetworkElement],
    mock_network_id: str,
) -> Network:
    _ = mock_network_elements
    return Network(
        uid=generate_hash(f"{mock_network_id}_2024-01-01T00:00:00+0000"),
        id=f"{mock_network_id}_2024-01-01T00:00:00+0000",
        elements=[
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
            )
        ],
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
        valid_actions=[DoNothingAction()],
        invalid_actions=[],
    )


@pytest.fixture
def mock_observation_space() -> Space:
    return Box(low=1, high=2)


@pytest.fixture
def mock_one_hot_map() -> OneHotMap:
    OneHotMap(
        types={},
        buses={},
        voltage_levels={},
        statuses={},
        constraint_sides={},
        constraint_types={},
        affected_elements={},
    )


@pytest.fixture
def mock_initial_observation(mock_observation_memory_length: int) -> NetworkObservation:
    return NetworkObservation(
        history_length=mock_observation_memory_length,
        network_snapshot_observations=(
            NetworkSnapshotObservation(
                observations=[], timestamp=datetime(2024, 1, 1, tzinfo=DEFAULT_TIMEZONE)
            ),
        ),
    )


@pytest.fixture
def mock_action_for_step() -> BaseAction:
    return DoNothingAction()


class MockReward(BaseReward):
    def compute_reward(
        self, network_snapshot_observation: NetworkSnapshotObservation
    ) -> float:
        _ = network_snapshot_observation
        return 0.0


class MockRewardHandler(RewardHandler):
    def build_reward(
        self,
    ) -> float:
        return MockReward()


class MockLoadFlowSolver(LoadFlowSolverRepository):
    def solve(self, network: Network, loadflow_type: LoadFlowType) -> Network:
        _ = loadflow_type
        for element in network.elements:
            if State.SOLVED in element.element_metadata.supported_states:
                element.element_metadata.state = State.SOLVED
        return network


class MockNetworkBuilder(NetworkBuilder):
    def from_elements(
        self, id: str | None = None, elements: list[NetworkElement] | None = None
    ) -> Network:
        _ = elements
        return Network(
            uid=generate_hash(f"{id}"),
            id=id,
            elements=[
                NetworkElement(
                    uid="some_uid",
                    id="load_1",
                    timestamp=datetime(2024, 1, 1, 1, 0, tzinfo=DEFAULT_TIMEZONE),
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
            ],
        )


class MockNetworkSnapshotObservationBuilder(NetworkSnapshotObservationBuilder):
    @staticmethod
    def from_network(
        network: Network | None = None,
        timestamp: datetime | None = None,
    ) -> NetworkSnapshotObservation:
        _ = network
        _ = timestamp
        return NetworkSnapshotObservation(
            observations=[
                LoadObservation(
                    id="load_1",
                    timestamp=datetime(
                        2024,
                        1,
                        1,
                        0,
                        0,
                        tzinfo=DEFAULT_TIMEZONE,
                    ),
                    type=SupportedNetworkElementTypes.LOAD,
                    status=ElementStatus.ON,
                    bus_id="BUS1",
                    voltage_level_id="VL1",
                    Pd=30.0,
                    active_power=10.0,
                    reactive_power=5.0,
                )
            ],
            timestamp=datetime(
                2024,
                1,
                1,
                0,
                0,
                tzinfo=DEFAULT_TIMEZONE,
            ),
        )


class MockNetworkObservationHandler(NetworkObservationHandler):
    @staticmethod
    def init_network_observation(
        history_length: int,
        network_snapshot_observations: tuple[NetworkSnapshotObservation, ...] = (),
    ) -> NetworkObservation:
        pass

    @staticmethod
    def add_network_snapshot_observation(
        network_observation: NetworkObservation | None = None,
        network_snapshot_observation: NetworkSnapshotObservation | None = None,
    ) -> NetworkObservation:
        _ = network_observation
        _ = network_snapshot_observation
        return NetworkObservation(
            history_length=1,
            network_snapshot_observations=[
                NetworkSnapshotObservation(
                    observations=[
                        LoadObservation(
                            id="load_1",
                            timestamp=datetime(
                                2024,
                                1,
                                1,
                                1,
                                0,
                                tzinfo=DEFAULT_TIMEZONE,
                            ),
                            type=SupportedNetworkElementTypes.LOAD,
                            status=ElementStatus.ON,
                            bus_id="BUS1",
                            voltage_level_id="VL1",
                            Pd=30.0,
                            active_power=10.0,
                            reactive_power=5.0,
                        )
                    ],
                    timestamp=datetime(
                        2024,
                        1,
                        1,
                        1,
                        0,
                        tzinfo=DEFAULT_TIMEZONE,
                    ),
                )
            ],
        )


class MockNetworkTransitionHandler(NetworkTransitionHandler):
    def build_next_network(
        self,
        current_network: Network | None = None,
        next_network_no_action: Network | None = None,
        action: BaseAction | None = None,
    ) -> Network:
        _ = action
        return Network(
            uid=generate_hash("some_id_2024-01-01T00:00:00+0000"),
            id="some_id_2024-01-01T00:00:00+0000",
            elements=[
                NetworkElement(
                    uid="some_uid",
                    id="load_1",
                    timestamp=datetime(2024, 1, 1, 1, 0, tzinfo=DEFAULT_TIMEZONE),
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
            ],
        )


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
        reward_handler=MockRewardHandler(aggregator_name="placeholder", rewards=[]),
        one_hot_map=mock_one_hot_map,
        network_builder=MockNetworkBuilder(),
        network_snapshot_observation_builder=MockNetworkSnapshotObservationBuilder(),
        network_transition_handler=MockNetworkTransitionHandler(),
        network_observation_handler=MockNetworkObservationHandler(),
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
            reward_handler=MockRewardHandler(aggregator_name="placeholder", rewards=[]),
            one_hot_map=mock_one_hot_map,
            network_builder=MockNetworkBuilder(),
            network_snapshot_observation_builder=MockNetworkSnapshotObservationBuilder(),
            network_transition_handler=MockNetworkTransitionHandler(),
            network_observation_handler=MockNetworkObservationHandler(),
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
        assert isinstance(
            env.reward_handler,
            MockRewardHandler,
        )
        assert isinstance(env.network_builder, MockNetworkBuilder)
        assert isinstance(
            env.network_snapshot_observation_builder,
            MockNetworkSnapshotObservationBuilder,
        )
        assert isinstance(
            env.network_observation_handler,
            MockNetworkObservationHandler,
        )

    def test_reset(
        self,
        mock_network_environment: NetworkEnvironment,
        mock_initial_observation: NetworkObservation,
        mock_initial_network: Network,
    ):
        initial_observation, _ = mock_network_environment.reset()

        # Assert initial obs
        assert initial_observation == mock_initial_observation

        # Assert current obs
        assert (
            mock_network_environment.current_observation.history_length
            == initial_observation.history_length
        )
        assert (
            mock_network_environment.current_observation.network_snapshot_observations[
                0
            ].__dict__
            == initial_observation.network_snapshot_observations[0].__dict__
        )
        assert len(
            mock_network_environment.current_observation.network_snapshot_observations
        ) == len(initial_observation.network_snapshot_observations)

        # Assert current network
        assert mock_network_environment.current_network.id == mock_initial_network.id
        assert mock_network_environment.current_network.uid == mock_initial_network.uid
        assert (
            mock_network_environment.current_network.elements[0]
            == mock_initial_network.elements[0]
        )

        # Assert current timestamp
        assert (
            mock_network_environment.current_timestamp
            == initial_observation.list_network_snapshot_observations()[0].timestamp
        )
        assert mock_network_environment.episode_reward == 0.0
        assert mock_network_environment.is_terminated is False

    def test_step(
        self,
        mock_network_environment: NetworkEnvironment,
        mock_action_for_step: BaseAction,
    ):
        mock_network_environment.reset()
        next_observation, reward, is_terminated, _ = mock_network_environment.step(
            action=mock_action_for_step,
        )
        # Assert the next obs is the mocked one.
        assert [
            i.__dict__
            for j in next_observation.network_snapshot_observations
            for i in j.observations
        ] == [
            i.__dict__
            for j in MockNetworkObservationHandler.add_network_snapshot_observation().network_snapshot_observations
            for i in j.observations
        ]
        assert [
            i.timestamp for i in next_observation.network_snapshot_observations
        ] == [
            i.timestamp
            for i in MockNetworkObservationHandler.add_network_snapshot_observation().network_snapshot_observations
        ]

        # Assert the next current obs is well assigned to the next obs.
        assert [
            i.__dict__
            for j in mock_network_environment.current_observation.network_snapshot_observations
            for i in j.observations
        ] == [
            i.__dict__
            for j in next_observation.network_snapshot_observations
            for i in j.observations
        ]
        assert mock_network_environment.current_timestamp == datetime(
            2024, 1, 1, 1, 0, tzinfo=DEFAULT_TIMEZONE
        )

        # Assert current network has been set
        assert (
            mock_network_environment.current_network
            == MockNetworkTransitionHandler().build_next_network()
        )

        assert reward == 0.0
        assert is_terminated is True


#    def test_make_env():
#        pass
