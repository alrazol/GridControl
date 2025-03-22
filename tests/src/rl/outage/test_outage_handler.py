import pytest
import numpy as np
from datetime import datetime
from src.core.constants import DEFAULT_TIMEZONE
from src.rl.enums import Granularity, OutageType
from src.core.constants import ElementStatus, State
from src.core.constants import SupportedNetworkElementTypes
from src.rl.outage.network_element_outage_handler import NetworkElementOutageHandler
from src.rl.repositories.network_element_outage_handler import (
    DefaultNetworkElementOutageHandler,
    MAINTENANCE_DURATION,
)
from src.core.domain.models.element import NetworkElement

# from src.core.domain.models.elements_metadata.generator import (
#     GeneratorMetadata,
#     GeneratorStaticAttributes,
# )
from src.core.domain.models.elements_metadata.line import (
    LineMetadata,
    LineStaticAttributes,
)


@pytest.fixture
def mock_seed() -> int:
    return 0


# @pytest.fixture
# def mock_network_element() -> NetworkElement:
#     return NetworkElement(
#         uid="some_uid",
#         id="some_id",
#         timestamp=datetime(2024, 1, 1, tzinfo=DEFAULT_TIMEZONE),
#         type=SupportedNetworkElementTypes.GENERATOR,
#         element_metadata=GeneratorMetadata(
#             state=State.STATIC,
#             static=GeneratorStaticAttributes(
#                 status=ElementStatus.ON,
#                 bus_id="BUS1",
#                 voltage_level_id="VL1",
#                 Pmax=100.0,
#                 Pmin=50.0,
#                 is_voltage_regulator=True,
#             ),
#         ),
#         network_id="some_id",
#         operational_constraints=[],
#     )


@pytest.fixture
def mock_network_element() -> NetworkElement:
    return NetworkElement(
        uid="some_uid",
        id="some_id",
        timestamp=datetime(2024, 1, 1, tzinfo=DEFAULT_TIMEZONE),
        type=SupportedNetworkElementTypes.LINE,
        element_metadata=LineMetadata(
            state=State.STATIC,
            static=LineStaticAttributes(
                status=ElementStatus.ON,
                voltage_level1_id="VL1",
                voltage_level2_id="VL2",
                bus1_id="bus1",
                bus2_id="bus2",
                b1=0.1,
                b2=0.1,
                g1=0.1,
                g2=0.1,
                r=0.1,
                x=0.1,
            ),
        ),
        network_id="some_id",
        operational_constraints=[],
    )


@pytest.fixture
def mock_network_element_outage_handler(
    mock_network_element: NetworkElement,
    mock_seed: int,
) -> NetworkElementOutageHandler:
    return DefaultNetworkElementOutageHandler(
        element=mock_network_element,
        initial_outage_prob=0.0,
        initial_remaining_duration=0,
        initial_usage_time=0,
        lambda_factor=0.1,
        granularity=Granularity.HOUR,
        seed=mock_seed,
    )


class TestOutageHandler:
    def test_initialization(self, mock_network_element: NetworkElement, mock_seed: int):
        outage_handler = DefaultNetworkElementOutageHandler(
            element=mock_network_element,
            initial_outage_prob=0.0,
            initial_remaining_duration=0,
            initial_usage_time=0,
            lambda_factor=0.1,
            granularity=Granularity.HOUR,
            seed=mock_seed,
        )
        assert outage_handler.element_id == "some_id"
        assert outage_handler.outage_prob == 0.0
        assert outage_handler.status == ElementStatus.ON
        assert outage_handler.remaining_duration == 0
        assert outage_handler.usage_time == 0
        assert outage_handler.outage_type is None
        assert outage_handler.lambda_factor == 0.1

    def test_usage_time_increment(
        self,
        mock_network_element_outage_handler: NetworkElementOutageHandler,
    ):
        mock_network_element_outage_handler._update_usage_time()
        assert mock_network_element_outage_handler.usage_time == 1
        assert mock_network_element_outage_handler.outage_prob == 0.1

    def test_no_increment_when_off(
        self,
        mock_network_element_outage_handler: NetworkElementOutageHandler,
    ):
        mock_network_element_outage_handler.status = ElementStatus.OFF
        mock_network_element_outage_handler._update_usage_time()
        assert mock_network_element_outage_handler.usage_time == 0
        assert mock_network_element_outage_handler.outage_prob == 0.0

    def test_outage_triggering(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mock_network_element_outage_handler: NetworkElementOutageHandler,
    ):
        monkeypatch.setattr(np.random, "rand", lambda: 0.0)
        mock_network_element_outage_handler.outage_prob = 1.0
        mock_network_element_outage_handler._sample_outage()
        assert mock_network_element_outage_handler.status == ElementStatus.OUTAGE
        assert isinstance(mock_network_element_outage_handler.outage_type, OutageType)
        assert mock_network_element_outage_handler.remaining_duration > 0

    def test_step_decrements_remaining_duration(
        self,
        mock_network_element_outage_handler: NetworkElementOutageHandler,
    ):
        mock_network_element_outage_handler.status = ElementStatus.OUTAGE
        mock_network_element_outage_handler.remaining_duration = 5
        mock_network_element_outage_handler.step()
        assert mock_network_element_outage_handler.remaining_duration == 4

    def test_step_recovery_from_outage(
        self,
        mock_network_element_outage_handler: NetworkElementOutageHandler,
    ):
        mock_network_element_outage_handler.status = ElementStatus.OUTAGE
        mock_network_element_outage_handler.remaining_duration = 1
        mock_network_element_outage_handler.step()
        assert mock_network_element_outage_handler.status == ElementStatus.ON
        assert mock_network_element_outage_handler.usage_time == 0
        assert mock_network_element_outage_handler.outage_prob == 0.0
        assert mock_network_element_outage_handler.outage_type is None

    def test_send_to_maintenance(
        self,
        mock_network_element_outage_handler: NetworkElementOutageHandler,
    ):
        mock_network_element_outage_handler.send_to_maintenance()
        assert mock_network_element_outage_handler.status == ElementStatus.MAINTENANCE
        assert (
            mock_network_element_outage_handler.remaining_duration
            == MAINTENANCE_DURATION
        )
        assert mock_network_element_outage_handler.usage_time == 0
        assert mock_network_element_outage_handler.outage_prob == 0.0

    # def test_reset(
    #     self,
    #     mock_network_element_outage_handler: NetworkElementOutageHandler,
    # ):
    #     pass
