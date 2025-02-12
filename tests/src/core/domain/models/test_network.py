from pydantic import ValidationError
import pytest
from datetime import datetime, timezone
import pandas as pd
from src.core.domain.models.element import NetworkElement
from src.core.domain.models.network import Network
from src.core.constants import SupportedNetworkElementTypes
from src.core.domain.models.elements_metadata.generator import (
    GeneratorMetadata,
    GeneratorStaticAttributes,
    GeneratorDynamicAttributes,
)
from src.core.domain.models.elements_metadata.line import (
    LineMetadata,
    LineStaticAttributes,
)
from src.core.utils import generate_hash
from src.core.domain.enums import State
from src.core.constants import ElementStatus, DEFAULT_TIMEZONE


@pytest.fixture
def valid_network_id():
    return "network_1"


@pytest.fixture
def valid_elements():
    return [
        NetworkElement(
            uid=generate_hash("element_1_2025-01-01T12:00:00+0000"),
            id="element_1",
            state=State.DYNAMIC,
            timestamp=datetime(
                2025,
                1,
                1,
                12,
                0,
                0,
                tzinfo=DEFAULT_TIMEZONE,
            ),
            type=SupportedNetworkElementTypes.GENERATOR,
            element_metadata=GeneratorMetadata(
                state=State.DYNAMIC,
                static=GeneratorStaticAttributes(
                    status=ElementStatus.ON,
                    voltage_level_id="VL1",
                    bus_id="bus_1",
                    Pmax=100.0,
                    Pmin=0.0,
                    is_voltage_regulator=True,
                ),
                dynamic=GeneratorDynamicAttributes(
                    Ptarget=80.0,
                    Vtarget=11.0,
                ),
            ),
            network_id="network_1",
            operational_constraints=[],
        ),
        NetworkElement(
            uid=generate_hash("element_1_2025-01-01T13:00:00+0000"),
            id="element_1",
            state=State.DYNAMIC,
            timestamp=datetime(
                2025,
                1,
                1,
                13,
                0,
                0,
                tzinfo=DEFAULT_TIMEZONE,
            ),
            type=SupportedNetworkElementTypes.GENERATOR,
            element_metadata=GeneratorMetadata(
                state=State.DYNAMIC,
                static=GeneratorStaticAttributes(
                    status=ElementStatus.ON,
                    voltage_level_id="VL1",
                    bus_id="bus_1",
                    Pmax=100.0,
                    Pmin=0.0,
                    is_voltage_regulator=True,
                ),
                dynamic=GeneratorDynamicAttributes(
                    Ptarget=80.0,
                    Vtarget=11.0,
                ),
            ),
            network_id="network_1",
            operational_constraints=[],
        ),
        NetworkElement(
            uid=generate_hash("element_2_2025-01-01T12:00:00+0000"),
            id="element_2",
            state=State.STATIC,
            timestamp=datetime(
                2025,
                1,
                1,
                12,
                0,
                0,
                tzinfo=DEFAULT_TIMEZONE,
            ),
            type=SupportedNetworkElementTypes.LINE,
            element_metadata=LineMetadata(
                state=State.STATIC,
                static=LineStaticAttributes(
                    status=ElementStatus.ON,
                    voltage_level1_id="VL1",
                    voltage_level2_id="VL2",
                    bus1_id="BUS1",
                    bus2_id="BUS2",
                    r=0.01,
                    x=0.1,
                    b1=0.1,
                    b2=0.1,
                    g1=0.2,
                    g2=0.1,
                ),
            ),
            network_id="network_1",
            operational_constraints=[],
        ),
    ]


class TestNetwork:
    """Tests for the `Network` class."""

    @pytest.mark.parametrize(
        "elements, expected_error",
        [
            # Valid case
            (
                [
                    NetworkElement(
                        uid=generate_hash("element_1_2025-01-01T12:00:00+0000"),
                        id="element_1",
                        timestamp=datetime(
                            2025,
                            1,
                            1,
                            12,
                            0,
                            0,
                            tzinfo=DEFAULT_TIMEZONE,
                        ),
                        type=SupportedNetworkElementTypes.GENERATOR,
                        element_metadata=GeneratorMetadata(
                            state=State.STATIC,
                            static=GeneratorStaticAttributes(
                                status=ElementStatus.ON,
                                voltage_level_id="VL1",
                                bus_id="bus_1",
                                Pmax=100.0,
                                Pmin=0.0,
                                is_voltage_regulator=True,
                            ),
                        ),
                        network_id="network_1",
                        operational_constraints=[],
                    )
                ],
                None,
            ),
            # Duplicate (id, timestamp) pair
            (
                [
                    NetworkElement(
                        uid=generate_hash("element_1_2025-01-01T12:00:00+0000"),
                        id="element_1",
                        timestamp=datetime(
                            2025,
                            1,
                            1,
                            12,
                            0,
                            0,
                            tzinfo=DEFAULT_TIMEZONE,
                        ),
                        type=SupportedNetworkElementTypes.GENERATOR,
                        element_metadata=GeneratorMetadata(
                            state=State.STATIC,
                            static=GeneratorStaticAttributes(
                                status=ElementStatus.ON,
                                voltage_level_id="VL1",
                                bus_id="bus_1",
                                Pmax=100.0,
                                Pmin=0.0,
                                is_voltage_regulator=True,
                            ),
                        ),
                        network_id="network_1",
                        operational_constraints=[],
                    ),
                    NetworkElement(
                        uid=generate_hash("element_1_2025-01-01T12:00:00+0000"),
                        id="element_1",
                        timestamp=datetime(
                            2025,
                            1,
                            1,
                            12,
                            0,
                            0,
                            tzinfo=DEFAULT_TIMEZONE,
                        ),
                        type=SupportedNetworkElementTypes.GENERATOR,
                        element_metadata=GeneratorMetadata(
                            state=State.STATIC,
                            static=GeneratorStaticAttributes(
                                status=ElementStatus.ON,
                                voltage_level_id="VL1",
                                bus_id="bus_1",
                                Pmax=100.0,
                                Pmin=0.0,
                                is_voltage_regulator=True,
                            ),
                        ),
                        network_id="network_1",
                        operational_constraints=[],
                    ),
                ],
                "Duplicate id/timestamp pair found: id=element_1, timestamp=2025-01-01T12:00:00+0000.",
            ),
        ],
    )
    def test_validate_timestamps(self, valid_network_id, elements, expected_error):
        """Test validation of timestamps and unique IDs."""
        if expected_error:
            with pytest.raises(ValidationError) as exc_info:
                Network.from_elements(id=valid_network_id, elements=elements)

            # Extract the error details from the ValidationError
            error_messages = [err["msg"] for err in exc_info.value.errors()]
            assert any(expected_error in msg for msg in error_messages)
        else:
            network = Network.from_elements(id=valid_network_id, elements=elements)
            assert len(network.elements) == len(elements)

    @pytest.mark.parametrize(
        "elements, expected_timestamps",
        [
            # Case with multiple unique timestamps
            (
                [
                    NetworkElement(
                        uid=generate_hash("element_1_2025-01-01T12:00:00+0000"),
                        id="element_1",
                        timestamp=datetime(
                            2025,
                            1,
                            1,
                            12,
                            0,
                            0,
                            tzinfo=DEFAULT_TIMEZONE,
                        ),
                        type=SupportedNetworkElementTypes.GENERATOR,
                        element_metadata=GeneratorMetadata(
                            state=State.STATIC,
                            static=GeneratorStaticAttributes(
                                status=ElementStatus.ON,
                                voltage_level_id="VL1",
                                bus_id="bus_1",
                                Pmax=100.0,
                                Pmin=0.0,
                                is_voltage_regulator=True,
                            ),
                        ),
                        network_id="network_1",
                        operational_constraints=[],
                    ),
                    NetworkElement(
                        uid=generate_hash("element_1_2025-01-01T13:00:00+0000"),
                        id="element_1",
                        timestamp=datetime(
                            2025,
                            1,
                            1,
                            13,
                            0,
                            0,
                            tzinfo=DEFAULT_TIMEZONE,
                        ),
                        type=SupportedNetworkElementTypes.GENERATOR,
                        element_metadata=GeneratorMetadata(
                            state=State.STATIC,
                            static=GeneratorStaticAttributes(
                                status=ElementStatus.ON,
                                voltage_level_id="VL1",
                                bus_id="bus_1",
                                Pmax=100.0,
                                Pmin=0.0,
                                is_voltage_regulator=True,
                            ),
                        ),
                        network_id="network_1",
                        operational_constraints=[],
                    ),
                ],
                [
                    datetime(
                        2025,
                        1,
                        1,
                        12,
                        0,
                        0,
                        tzinfo=DEFAULT_TIMEZONE,
                    ),
                    datetime(
                        2025,
                        1,
                        1,
                        13,
                        0,
                        0,
                        tzinfo=DEFAULT_TIMEZONE,
                    ),
                ],
            ),
        ],
    )
    def test_list_timestamps(self, valid_network_id, elements, expected_timestamps):
        """Test listing unique timestamps in the network."""
        network = Network.from_elements(id=valid_network_id, elements=elements)
        timestamps = network.list_timestamps()
        assert timestamps == expected_timestamps

    @pytest.mark.parametrize(
        "timestamp, element_type, expected_count",
        [
            # Case with specific timestamp and type
            (
                datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                SupportedNetworkElementTypes.LINE,
                1,
            ),
            (
                datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                SupportedNetworkElementTypes.GENERATOR,
                1,
            ),
        ],
    )
    def test_list_elements(
        self, valid_network_id, valid_elements, timestamp, element_type, expected_count
    ):
        """Test listing elements by timestamp and type."""
        network = Network.from_elements(id=valid_network_id, elements=valid_elements)
        elements = network.list_elements(timestamp, element_type)
        assert len(elements) == expected_count

    def test_to_dataframe(self, valid_network_id, valid_elements):
        """Test converting an element's data to a DataFrame."""
        network = Network.from_elements(id=valid_network_id, elements=valid_elements)
        element_id = "element_1"
        df = network.to_dataframe(element_id)

        assert isinstance(df, pd.DataFrame)
        assert "timestamp" in df.columns
        assert "static.voltage_level_id" in df.columns
        assert "dynamic.Vtarget" in df.columns
        assert len(df) == 2  # Two timestamps for `element_1`
