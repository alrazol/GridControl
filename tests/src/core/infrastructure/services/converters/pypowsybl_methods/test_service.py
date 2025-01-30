import pytest
from datetime import datetime, timezone
from src.core.utils import parse_datetime_to_str
from src.core.constants import State, SupportedNetworkElementTypes
from src.core.domain.models.element import NetworkElement
from src.core.domain.models.network import Network
from src.core.domain.models.elements_metadata.bus import (
    BusMetadata,
    BusStaticAttributes,
)
from src.core.domain.models.elements_metadata.generator import (
    GeneratorMetadata,
    GeneratorStaticAttributes,
    GeneratorDynamicAttributes,
    GeneratorSolvedAttributes,
)
from src.core.domain.models.elements_metadata.voltage_level import (
    VoltageLevelsMetadata,
    VoltageLevelsStaticAttributes,
)
from src.core.domain.models.elements_metadata.line import (
    LineMetadata,
    LineStaticAttributes,
)
from src.core.infrastructure.services.converters.pypowsybl_methods.service import (
    PyPowsyblCompatService,
)
from src.core.constants import ElementStatus
from src.core.infrastructure.services.converters.pypowsybl_methods.models.pypowsybl_network_wrapper import (
    PyPowSyblNetworkWrapper,
)
from src.core.constants import DATETIME_FORMAT, DEFAULT_TIMEZONE


class TestElementToPypowsybl:
    """Tests for `element_to_pypowsybl` function."""

    @pytest.mark.parametrize(
        "network_element, expected_output",
        [
            # Test case for BUS
            (
                NetworkElement(
                    uid="uid",
                    id="bus_1",
                    timestamp="2024-01-01T00:00:00+0000",
                    type=SupportedNetworkElementTypes.BUS,
                    element_metadata=BusMetadata(
                        state=State.STATIC,
                        static=BusStaticAttributes(
                            voltage_level_id="VL1",
                        ),
                    ),
                    network_id="network1",
                    operational_constraints=[],
                ),
                {
                    "id": "bus_1",
                    "voltage_level_id": "VL1",
                },
            ),
            # Test case for GENERATOR
            (
                NetworkElement(
                    uid="uid",
                    id="gen_1",
                    timestamp="2024-01-01T00:00:00+0000",
                    type=SupportedNetworkElementTypes.GENERATOR,
                    element_metadata=GeneratorMetadata(
                        state=State.DYNAMIC,
                        static=GeneratorStaticAttributes(
                            status=ElementStatus.ON,
                            voltage_level_id="VL2",
                            bus_id="bus2",
                            Pmax=100.0,
                            Pmin=50.0,
                            is_voltage_regulator=True,
                        ),
                        dynamic=GeneratorDynamicAttributes(
                            Ptarget=75.0,
                            Vtarget=1.02,
                            Qtarget=None,
                            Srated=200.0,
                        ),
                    ),
                    network_id="network_1",
                    operational_constraints=[],
                ),
                {
                    "id": "gen_1",
                    "voltage_level_id": "VL2",
                    "bus_id": "bus2",
                    "max_p": 100.0,
                    "min_p": 50.0,
                    "target_p": 75.0,
                    "target_v": 1.02,
                    "voltage_regulator_on": True,
                    "rated_s": 200.0,
                },
            ),
            # Test case for an OFF line
            (
                NetworkElement(
                    uid="uid",
                    id="line_1",
                    timestamp="2024-01-01T00:00:00+0000",
                    type=SupportedNetworkElementTypes.LINE,
                    element_metadata=LineMetadata(
                        state=State.STATIC,
                        static=LineStaticAttributes(
                            status=ElementStatus.OFF,
                            voltage_level1_id="VL1",
                            voltage_level2_id="VL1",
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
                    network_id="network_1",
                    operational_constraints=[],
                ),
                {
                    "id": "line_1",
                    "voltage_level1_id": "VL1",
                    "voltage_level2_id": "VL1",
                    "bus1_id": "bus1",
                    "bus2_id": "bus2",
                    "b1": 0.1,
                    "b2": 0.1,
                    "g1": 0.1,
                    "g2": 0.1,
                    "r": 0.1,
                    "x": 0.1,
                },
            ),
        ],
    )
    def test_element_to_pypowsybl(
        self,
        network_element,
        expected_output,
    ):
        """Parameterized test for converting elements to Pypowsybl format."""

        result = PyPowsyblCompatService.element_to_pypowsybl(network_element)
        assert result == expected_output


class TestElementFromPypowsybl:
    """Tests for `element_from_pypowsybl` function."""

    @pytest.mark.parametrize(
        "element_id, element_type, timestamp, network_id, element_metadata, constraints, expected_static, expected_dynamic, expected_solved, expected_metadata_state",
        [
            # Test case for GENERATOR
            (
                "gen_1",
                SupportedNetworkElementTypes.GENERATOR,
                datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                "network_1",
                {
                    "voltage_level_id": "VL2",
                    "bus_id": "bus2",
                    "max_p": 100.0,
                    "min_p": 50.0,
                    "voltage_regulator_on": True,
                    "target_p": 75.0,
                    "target_v": 1.02,
                    "rated_s": 200.0,
                    "p": 1.0,
                    "q": 1.0,
                    "i": 1.0,
                    "connected": True,
                },
                [],
                GeneratorStaticAttributes(
                    status=ElementStatus.ON,
                    voltage_level_id="VL2",
                    bus_id="bus2",
                    Pmax=100.0,
                    Pmin=50.0,
                    is_voltage_regulator=True,
                ),
                GeneratorDynamicAttributes(
                    Ptarget=75.0,
                    Vtarget=1.02,
                    Srated=200.0,
                ),
                GeneratorSolvedAttributes(
                    p=1.0,
                    q=1.0,
                    i=1.0,
                    connected=True,
                ),
                State.SOLVED,
            ),
        ],
    )
    def test_element_from_pypowsybl(
        self,
        element_id,
        element_type,
        network_id,
        timestamp,
        element_metadata,
        constraints,
        expected_static,
        expected_dynamic,
        expected_solved,
        expected_metadata_state,
    ):
        """Parameterized test for creating elements from Pypowsybl metadata."""
        result = PyPowsyblCompatService.element_from_pypowsybl(
            element_id=element_id,
            element_type=element_type,
            timestamp=timestamp,
            network_id=network_id,
            element_metadata_pypowsybl=element_metadata,
            operational_constraints=constraints,
        )
        assert result.id == element_id
        assert result.type == element_type
        assert result.element_metadata.static == expected_static
        assert result.element_metadata.dynamic == expected_dynamic
        assert result.element_metadata.solved == expected_solved
        assert result.element_metadata.state == expected_metadata_state

    @pytest.mark.parametrize(
        "element_id, element_type, element_metadata",
        [
            # Unsupported element types
            (
                "unsupported_1",
                SupportedNetworkElementTypes.SUBSTATION,
                {},
            ),
            (
                "unsupported_2",
                SupportedNetworkElementTypes.VOLTAGE_LEVEL,
                {},
            ),
            (
                "unsupported_3",
                SupportedNetworkElementTypes.TWO_WINDINGS_TRANSFORMERS,
                {},
            ),
        ],
    )
    def test_unsupported_element_type_raises_error(
        self, element_id, element_type, element_metadata
    ):
        """Test that unsupported element types raise ValueError."""
        with pytest.raises(
            ValueError, match=f"Unsupported element type: {element_type}"
        ):
            PyPowsyblCompatService.element_from_pypowsybl(
                element_id=element_id,
                element_type=element_type,
                element_metadata_pypowsybl=element_metadata,
                operational_constraints=[],
                timestamp=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                network_id="network_1",
            )


class TestNetworkToPypowsybl:
    """Tests for the `network_to_pypowsybl` function."""

    @pytest.mark.parametrize(
        "network_elements, expected_timestamps",
        [
            # Valid single timestamp
            (
                [
                    NetworkElement(
                        uid="uid_voltage",
                        id="VL1",
                        timestamp="2024-01-01T00:00:00+0000",
                        type=SupportedNetworkElementTypes.VOLTAGE_LEVEL,
                        element_metadata=VoltageLevelsMetadata(
                            state=State.STATIC,
                            static=VoltageLevelsStaticAttributes(
                                topology_kind="BUS_BREAKER",
                                Vnominal=11.0,
                            ),
                        ),
                        network_id="network_1",
                        operational_constraints=[],
                    ),
                    NetworkElement(
                        uid="uid_bus",
                        id="bus_1",
                        timestamp="2024-01-01T00:00:00+0000",
                        type=SupportedNetworkElementTypes.BUS,
                        element_metadata=BusMetadata(
                            state=State.STATIC,
                            static=BusStaticAttributes(voltage_level_id="VL1"),
                        ),
                        network_id="network_1",
                        operational_constraints=[],
                    ),
                    NetworkElement(
                        uid="uid_gen",
                        id="gen_1",
                        timestamp="2024-01-01T00:00:00+0000",
                        type=SupportedNetworkElementTypes.GENERATOR,
                        element_metadata=GeneratorMetadata(
                            state=State.DYNAMIC,
                            static=GeneratorStaticAttributes(
                                status=ElementStatus.ON,
                                voltage_level_id="VL1",
                                bus_id="bus_1",
                                Pmax=100.0,
                                Pmin=50.0,
                                is_voltage_regulator=True,
                            ),
                            dynamic=GeneratorDynamicAttributes(
                                Ptarget=75.0,
                                Vtarget=1.02,
                                Qtarget=None,
                                Srated=200.0,
                            ),
                        ),
                        network_id="network_1",
                        operational_constraints=[],
                    ),
                ],
                ["2024-01-01T00:00:00+0000"],
            ),
            # Multiple timestamps
            (
                [
                    NetworkElement(
                        uid="uid_voltage",
                        id="VL1",
                        timestamp="2024-01-01T00:00:00+0000",
                        type=SupportedNetworkElementTypes.VOLTAGE_LEVEL,
                        element_metadata=VoltageLevelsMetadata(
                            state=State.STATIC,
                            static=VoltageLevelsStaticAttributes(
                                topology_kind="BUS_BREAKER",
                                Vnominal=11.0,
                            ),
                        ),
                        network_id="network_1",
                        operational_constraints=[],
                    ),
                    NetworkElement(
                        uid="uid_bus_1",
                        id="bus_1",
                        timestamp="2024-01-01T00:00:00+0000",
                        type=SupportedNetworkElementTypes.BUS,
                        element_metadata=BusMetadata(
                            state=State.STATIC,
                            static=BusStaticAttributes(voltage_level_id="VL1"),
                        ),
                        network_id="network_2",
                        operational_constraints=[],
                    ),
                    NetworkElement(
                        uid="uid_voltage",
                        id="VL1",
                        timestamp="2024-01-02T00:00:00+0000",
                        type=SupportedNetworkElementTypes.VOLTAGE_LEVEL,
                        element_metadata=VoltageLevelsMetadata(
                            state=State.STATIC,
                            static=VoltageLevelsStaticAttributes(
                                topology_kind="BUS_BREAKER",
                                Vnominal=11.0,
                            ),
                        ),
                        network_id="network_1",
                        operational_constraints=[],
                    ),
                    NetworkElement(
                        uid="uid_bus_1",
                        id="bus_1",
                        timestamp="2024-01-02T00:00:00+0000",
                        type=SupportedNetworkElementTypes.BUS,
                        element_metadata=BusMetadata(
                            state=State.STATIC,
                            static=BusStaticAttributes(voltage_level_id="VL1"),
                        ),
                        network_id="network_1",
                        operational_constraints=[],
                    ),
                ],
                [
                    "2024-01-01T00:00:00+0000",
                    "2024-01-02T00:00:00+0000",
                ],
            ),
            # Empty network
            (
                [],
                [],
            ),
        ],
    )
    def test_network_to_pypowsybl(self, network_elements, expected_timestamps):
        """
        Parameterized test for converting networks to PyPowSybl format.
        """
        network = Network(uid="some_uid", id="test_network", elements=network_elements)
        result = PyPowsyblCompatService.network_to_pypowsybl(network)

        # Assert the correct timestamps are present in the result
        assert sorted(
            [
                parse_datetime_to_str(i, format=DATETIME_FORMAT, tz=DEFAULT_TIMEZONE)
                for i in result.data.keys()
            ]
        ) == sorted(expected_timestamps)

        # Assert the PyPowSybl network is created for each timestamp
        for timestamp in expected_timestamps:
            assert isinstance(result, PyPowSyblNetworkWrapper)
            assert list(
                result.get_active_network()[timestamp].get_voltage_levels().index
            ) == ["VL1"]

    @pytest.mark.parametrize(
        "network_elements",
        [
            # Valid single timestamp
            [
                NetworkElement(
                    uid="uid_voltage",
                    id="VL1",
                    timestamp="2024-01-01T00:00:00+0000",
                    type=SupportedNetworkElementTypes.VOLTAGE_LEVEL,
                    element_metadata=VoltageLevelsMetadata(
                        state=State.STATIC,
                        static=VoltageLevelsStaticAttributes(
                            topology_kind="BUS_BREAKER",
                            Vnominal=11.0,
                        ),
                    ),
                    network_id="network_1",
                    operational_constraints=[],
                ),
                NetworkElement(
                    uid="uid_bus",
                    id="bus1",
                    timestamp="2024-01-01T00:00:00+0000",
                    type=SupportedNetworkElementTypes.BUS,
                    element_metadata=BusMetadata(
                        state=State.STATIC,
                        static=BusStaticAttributes(voltage_level_id="VL1"),
                    ),
                    network_id="network_1",
                    operational_constraints=[],
                ),
                NetworkElement(
                    uid="uid_bus2",
                    id="bus2",
                    timestamp="2024-01-01T00:00:00+0000",
                    type=SupportedNetworkElementTypes.BUS,
                    element_metadata=BusMetadata(
                        state=State.STATIC,
                        static=BusStaticAttributes(voltage_level_id="VL1"),
                    ),
                    network_id="network_1",
                    operational_constraints=[],
                ),
                NetworkElement(
                    uid="line1_uid",
                    id="line_1",
                    timestamp="2024-01-01T00:00:00+0000",
                    type=SupportedNetworkElementTypes.LINE,
                    element_metadata=LineMetadata(
                        state=State.STATIC,
                        static=LineStaticAttributes(
                            status=ElementStatus.OFF,
                            voltage_level1_id="VL1",
                            voltage_level2_id="VL1",
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
                    network_id="network_1",
                    operational_constraints=[],
                ),
                NetworkElement(
                    uid="line2_uid",
                    id="line_2",
                    timestamp="2024-01-01T00:00:00+0000",
                    type=SupportedNetworkElementTypes.LINE,
                    element_metadata=LineMetadata(
                        state=State.STATIC,
                        static=LineStaticAttributes(
                            status=ElementStatus.ON,
                            voltage_level1_id="VL1",
                            voltage_level2_id="VL1",
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
                    network_id="network_1",
                    operational_constraints=[],
                ),
            ],
        ],
    )
    def test_network_to_pypowsybl_with_lines(
        self, network_elements: list[NetworkElement]
    ):
        network = Network(uid="some_uid", id="test_network", elements=network_elements)
        result = PyPowsyblCompatService.network_to_pypowsybl(network)
        result_active = result.get_active_network()

        assert list(result_active["2024-01-01T00:00:00+0000"].get_lines().index) == [
            "line_2"
        ]
