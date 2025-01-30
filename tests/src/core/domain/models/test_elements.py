import pytest
from src.core.constants import State, SupportedNetworkElementTypes
from src.core.utils import generate_hash
from src.core.domain.models.element import NetworkElement
from src.core.domain.models.elements_metadata.load import (
    LoadMetadata,
    LoadStaticAttributes,
)
from src.core.domain.models.elements_metadata.line import (
    LineMetadata,
    LineStaticAttributes,
    LineSolvedAttributes,
)
from src.core.domain.models.operational_constraint import OperationalConstraint
from datetime import datetime, timezone
from src.core.constants import ElementStatus


class TestNetworkElement:
    @pytest.mark.parametrize(
        "element_id, network_id, element_metadata, element_type, constraints, timestamp, expected_state, expected_uid, expected_constraints_count",
        [
            # Test case 1: Static LOAD without constraints
            (
                "load_1",
                "network_1",
                LoadMetadata(
                    state=State.STATIC,
                    static=LoadStaticAttributes(
                        voltage_level_id="VL1",
                        bus_id="bus1",
                    ),
                ),
                SupportedNetworkElementTypes.LOAD,
                [],
                None,
                State.STATIC,
                generate_hash("load_1_None"),
                0,
            ),
            # Test case 2: Solved LINE with constraints
            (
                "line_1",
                "network_1",
                LineMetadata(
                    state=State.SOLVED,
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
                    solved=LineSolvedAttributes(
                        p1=50.0,
                        q1=1.2,
                        i1=1,
                        p2=1,
                        q2=1,
                        i2=1,
                    ),
                ),
                SupportedNetworkElementTypes.LINE,
                [
                    OperationalConstraint(
                        uid="uid1",
                        element_uid="element_uid1",
                        element_id="line_1",
                        side="ONE",
                        name="constraint1",
                        type="APPARENT_POWER",
                        value=1.5,
                        acceptable_duration=1,
                    ),
                    OperationalConstraint(
                        uid="uid2",
                        element_uid="element_uid2",
                        element_id="line_2",
                        side="TWO",
                        name="constraint2",
                        type="APPARENT_POWER",
                        value=1.5,
                        acceptable_duration=1,
                    ),
                ],
                datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                State.SOLVED,
                generate_hash("line_1_2025-01-01T12:00:00+0000"),
                2,
            ),
        ],
    )
    def test_from_metadata(
        self,
        element_id,
        network_id,
        element_metadata,
        element_type,
        constraints,
        timestamp,
        expected_state,
        expected_uid,
        expected_constraints_count,
    ):
        """Test creating a NetworkElement from valid metadata and constraints."""

        element = NetworkElement.from_metadata(
            id=element_id,
            timestamp=timestamp,
            type=element_type,
            element_metadata=element_metadata,
            operational_constraints=constraints,
            network_id=network_id,
        )

        assert element.uid == expected_uid
        assert element.type == element_type
        assert len(element.operational_constraints) == expected_constraints_count

        assert element.element_metadata.state == expected_state
