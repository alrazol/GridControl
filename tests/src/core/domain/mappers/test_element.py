import pytest
from src.core.domain.models.element import NetworkElement
from src.core.infrastructure.schemas import (
    NetworkElementSchema,
    OperationalConstraintSchema,
)
from src.core.domain.models.elements_metadata.line import (
    LineMetadata,
    LineStaticAttributes,
)
from src.core.domain.mappers.element import NetworkElementMapper
from src.core.domain.models.operational_constraint import OperationalConstraint
from src.core.constants import SupportedNetworkElementTypes, ElementStatus
from src.core.domain.enums import State, BranchSide, OperationalConstraintType
from src.core.utils import generate_hash


@pytest.mark.parametrize(
    "schema, expected_domain",
    [
        # Test case: Valid Generator schema to domain mapping
        (
            NetworkElementSchema(
                uid=generate_hash(s="element_1_2025-01-01T12:00:00+0000"),
                id="element_1",
                timestamp="2025-01-01T12:00:00+0000",
                type="LINE",
                element_metadata={
                    "state": "STATIC",
                    "static": {
                        "status": "ON",
                        "voltage_level1_id": "VL1",
                        "voltage_level2_id": "VL2",
                        "bus1_id": "bus1",
                        "bus2_id": "bus2",
                        "b1": 0.1,
                        "b2": 0.1,
                        "g1": 0.1,
                        "g2": 0.1,
                        "r": 0.1,
                        "x": 0.1,
                        "connectable_bus1_id": None,
                        "connectable_bus2_id": None,
                        "name": None,
                    },
                    "solved": None,
                },
                network_id="network_1",
                # network=NetworkSchema(
                #    uid="net",
                #    id="network",
                # ),
                operational_constraints=[
                    OperationalConstraintSchema(
                        uid=generate_hash(
                            s=f"{generate_hash("element_1_2025-01-01T12:00:00+0000")}_TWO_CURRENT"
                        ),
                        element_uid=generate_hash("element_1_2025-01-01T12:00:00+0000"),
                        element_id="element_1",
                        side="TWO",
                        name="Constraint 1",
                        type="CURRENT",
                        value=100.0,
                        acceptable_duration=60,
                    )
                ],
            ),
            NetworkElement(
                uid=generate_hash(s="element_1_2025-01-01T12:00:00+0000"),
                id="element_1",
                timestamp="2025-01-01T12:00:00+0000",
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
                network_id="network_1",
                operational_constraints=[
                    OperationalConstraint(
                        uid=generate_hash(
                            s=f"{generate_hash(s="element_1_2025-01-01T12:00:00+0000")}_TWO_CURRENT"
                        ),
                        element_uid=generate_hash(
                            s="element_1_2025-01-01T12:00:00+0000"
                        ),
                        element_id="element_1",
                        side=BranchSide.TWO,
                        name="Constraint 1",
                        type=OperationalConstraintType.CURRENT,
                        value=100.0,
                        acceptable_duration=60,
                    )
                ],
            ),
        ),
        # Test case: Timestamp is None
        (
            NetworkElementSchema(
                uid=generate_hash(s="element_1_None"),
                id="element_1",
                timestamp=None,
                type="LINE",
                element_metadata={
                    "state": "STATIC",
                    "static": {
                        "status": "ON",
                        "voltage_level1_id": "VL1",
                        "voltage_level2_id": "VL2",
                        "bus1_id": "bus1",
                        "bus2_id": "bus2",
                        "b1": 0.1,
                        "b2": 0.1,
                        "g1": 0.1,
                        "g2": 0.1,
                        "r": 0.1,
                        "x": 0.1,
                        "connectable_bus1_id": None,
                        "connectable_bus2_id": None,
                        "name": None,
                    },
                    "solved": None,
                },
                network_id="network_1",
                operational_constraints=[],
            ),
            NetworkElement(
                uid=generate_hash(s="element_1_None"),
                id="element_1",
                timestamp=None,
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
                network_id="network_1",
                operational_constraints=[],
            ),
        ),
    ],
)
def test_schema_to_domain(schema, expected_domain):
    """Parameterized test for schema to domain mapping."""
    mapper = NetworkElementMapper()
    domain = mapper.schema_to_domain(schema)

    # Assert all fields
    assert domain == expected_domain


@pytest.mark.parametrize(
    "domain, expected_schema",
    [
        # Test case: Valid Generator domain to schema mapping
        (
            NetworkElement(
                uid=generate_hash(s="element_1_2025-01-01T12:00:00+0000"),
                id="element_1",
                timestamp="2025-01-01T12:00:00+0000",
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
                network_id="network_1",
                operational_constraints=[
                    OperationalConstraint(
                        uid=generate_hash(
                            s=f"{generate_hash(s="element_1_2025-01-01T12:00:00+0000")}_TWO_CURRENT"
                        ),
                        element_uid=generate_hash(
                            s="element_1_2025-01-01T12:00:00+0000"
                        ),
                        element_id="element_1",
                        side=BranchSide.TWO,
                        name="Constraint 1",
                        type=OperationalConstraintType.CURRENT,
                        value=100.0,
                        acceptable_duration=60,
                    )
                ],
            ),
            NetworkElementSchema(
                uid=generate_hash("element_1_2025-01-01T12:00:00+0000"),
                id="element_1",
                timestamp="2025-01-01T12:00:00+0000",
                type="LINE",
                element_metadata={
                    "state": "STATIC",
                    "static": {
                        "status": "ON",
                        "voltage_level1_id": "VL1",
                        "voltage_level2_id": "VL2",
                        "bus1_id": "bus1",
                        "bus2_id": "bus2",
                        "b1": 0.1,
                        "b2": 0.1,
                        "g1": 0.1,
                        "g2": 0.1,
                        "r": 0.1,
                        "x": 0.1,
                        "connectable_bus1_id": None,
                        "connectable_bus2_id": None,
                        "name": None,
                    },
                    "solved": None,
                },
                network_id="network_1",
                # network=NetworkSchema(
                #    uid="network_uid",
                #    id="network",
                # ),
                operational_constraints=[
                    OperationalConstraintSchema(
                        uid=generate_hash(
                            s=f"{generate_hash("element_1_2025-01-01T12:00:00+0000")}_TWO_CURRENT"
                        ),
                        element_uid=generate_hash("element_1_2025-01-01T12:00:00+0000"),
                        element_id="element_1",
                        side="TWO",
                        name="Constraint 1",
                        type="CURRENT",
                        value=100.0,
                        acceptable_duration=60,
                    )
                ],
            ),
        ),
    ],
)
def test_domain_to_schema(domain, expected_schema: NetworkElementSchema):
    """Parameterized test for domain to schema mapping."""
    mapper = NetworkElementMapper()
    schema = mapper.domain_to_schema(domain)

    schema_dict = schema.__dict__.copy()
    expected_schema_dict = expected_schema.__dict__.copy()

    schema_dict.pop("_sa_instance_state", None)
    expected_schema_dict.pop("_sa_instance_state", None)

    schema_constraints = [
        constraint.__dict__.copy()
        for constraint in schema_dict.get("operational_constraints", [])
    ]
    expected_schema_constraints = [
        constraint.__dict__.copy()
        for constraint in expected_schema_dict.get("operational_constraints", [])
    ]

    for constraint in schema_constraints:
        constraint.pop("_sa_instance_state", None)
        constraint.pop("network_element", None)

    for expected_constraint in expected_schema_constraints:
        expected_constraint.pop("_sa_instance_state", None)
        expected_constraint.pop("network_element", None)

    schema_dict["operational_constraints"] = schema_constraints
    expected_schema_dict["operational_constraints"] = expected_schema_constraints

    assert schema_dict == expected_schema_dict


@pytest.mark.parametrize(
    "schema, domain",
    [
        # Test case: Bidirectional consistency
        (
            NetworkElementSchema(
                uid=generate_hash(s="element_1_2025-01-01T12:00:00+0000"),
                id="element_1",
                timestamp="2025-01-01T12:00:00+0000",
                type="LINE",
                element_metadata={
                    "state": "STATIC",
                    "static": {
                        "status": "ON",
                        "voltage_level1_id": "VL1",
                        "voltage_level2_id": "VL2",
                        "bus1_id": "bus1",
                        "bus2_id": "bus2",
                        "b1": 0.1,
                        "b2": 0.1,
                        "g1": 0.1,
                        "g2": 0.1,
                        "r": 0.1,
                        "x": 0.1,
                        "connectable_bus1_id": None,
                        "connectable_bus2_id": None,
                        "name": None,
                    },
                },
                network_id="network_1",
                operational_constraints=[
                    OperationalConstraintSchema(
                        uid=generate_hash(
                            s=f"{generate_hash(s="element_1_2025-01-01T12:00:00+0000")}_TWO_CURRENT"
                        ),
                        element_uid=generate_hash(
                            s="element_1_2025-01-01T12:00:00+0000"
                        ),
                        element_id="element_1",
                        side="TWO",
                        name="Constraint 1",
                        type="CURRENT",
                        value=100.0,
                        acceptable_duration=60,
                    )
                ],
            ),
            NetworkElement(
                uid=generate_hash(s="element_1_2025-01-01T12:00:00+0000"),
                id="element_1",
                timestamp="2025-01-01T12:00:00+0000",
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
                network_id="network_1",
                operational_constraints=[
                    OperationalConstraint(
                        uid=generate_hash(
                            s=f"{generate_hash(s="element_1_2025-01-01T12:00:00+0000")}_TWO_CURRENT"
                        ),
                        element_uid=generate_hash(
                            s="element_1_2025-01-01T12:00:00+0000"
                        ),
                        element_id="element_1",
                        side=BranchSide.TWO,
                        name="Constraint 1",
                        type=OperationalConstraintType.CURRENT,
                        value=100.0,
                        acceptable_duration=60,
                    )
                ],
            ),
        ),
    ],
)
def test_bidirectional_mapping(schema, domain):
    """Test bidirectional mapping consistency."""
    mapper = NetworkElementMapper()

    # Domain -> Schema -> Domain
    domain_from_schema = mapper.schema_to_domain(
        mapper.domain_to_schema(mapper.schema_to_domain(schema))
    )
    assert domain_from_schema == domain
