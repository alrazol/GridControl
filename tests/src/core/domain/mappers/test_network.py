import pytest
from datetime import datetime
from src.core.domain.models.network import Network
from src.core.infrastructure.schemas import NetworkSchema, NetworkElementSchema
from src.core.domain.mappers.network import NetworkMapper
from src.core.domain.models.element import NetworkElement
from src.core.constants import SupportedNetworkElementTypes, State, ElementStatus
from src.core.domain.models.elements_metadata.line import (
    LineMetadata,
    LineStaticAttributes,
)
from src.core.utils import generate_hash
from src.core.constants import DEFAULT_TIMEZONE


@pytest.mark.parametrize(
    "schema, expected_domain",
    [
        # Test case: Valid NetworkSchema to Network mapping
        (
            NetworkSchema(
                uid="network_uid",
                id="network_1",
                elements=[
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
                            },
                        },
                        network_id="network_1",
                        operational_constraints=[],
                    ),
                ],
            ),
            Network(
                uid="network_uid",
                id="network_1",
                elements=[
                    NetworkElement(
                        uid=generate_hash(s="element_1_2025-01-01T12:00:00+0000"),
                        id="element_1",
                        timestamp=datetime(2025, 1, 1, 12, 0, tzinfo=DEFAULT_TIMEZONE),
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
                ],
            ),
        ),
    ],
)
def test_schema_to_domain(schema, expected_domain):
    """Test schema-to-domain mapping for Network."""
    mapper = NetworkMapper()
    domain = mapper.schema_to_domain(schema)
    assert domain == expected_domain


@pytest.mark.parametrize(
    "domain, expected_schema",
    [
        # Test case: Valid Network to NetworkSchema mapping
        (
            Network(
                uid="network_uid",
                id="network_1",
                elements=[
                    NetworkElement(
                        uid=generate_hash(s="element_1_2025-01-01T12:00:00+0000"),
                        id="element_1",
                        timestamp=datetime(2025, 1, 1, 12, 0, tzinfo=DEFAULT_TIMEZONE),
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
                ],
            ),
            NetworkSchema(
                uid="network_uid",
                id="network_1",
                elements=[
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
                        operational_constraints=[],
                    ),
                ],
            ),
        ),
    ],
)
def test_domain_to_schema(domain, expected_schema):
    """Test domain-to-schema mapping for Network."""
    mapper = NetworkMapper()
    schema = mapper.domain_to_schema(domain)

    expected_schema_dict = expected_schema.__dict__.copy()
    schema_dict = schema.__dict__.copy()

    expected_schema_dict.pop("_sa_instance_state", None)
    schema_dict.pop("_sa_instance_state", None)

    expected_schema_elements = [
        element.__dict__.copy() for element in expected_schema_dict.get("elements", [])
    ]
    schema_elements = [
        element.__dict__.copy() for element in schema_dict.get("elements", [])
    ]

    for schema in expected_schema_elements:
        schema.pop("_sa_instance_state", None)
        schema.pop("network", None)

    for schema in schema_elements:
        schema.pop("_sa_instance_state", None)
        schema.pop("network", None)

    schema_dict["elements"] = schema_elements
    expected_schema_dict["elements"] = expected_schema_elements

    # Convert to dict for easier comparison
    assert schema_dict == expected_schema_dict


@pytest.mark.parametrize(
    "schema, domain",
    [
        # Test case: Bidirectional consistency
        (
            NetworkSchema(
                uid="network_uid",
                id="network_1",
                elements=[
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
                            },
                        },
                        network_id="network_1",
                        operational_constraints=[],
                    ),
                ],
            ),
            Network(
                uid="network_uid",
                id="network_1",
                elements=[
                    NetworkElement(
                        uid=generate_hash(s="element_1_2025-01-01T12:00:00+0000"),
                        id="element_1",
                        timestamp=datetime(2025, 1, 1, 12, 0, tzinfo=DEFAULT_TIMEZONE),
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
                ],
            ),
        ),
    ],
)
def test_bidirectional_mapping(schema, domain):
    """Test bidirectional mapping consistency for Network."""
    mapper = NetworkMapper()

    # Domain -> Schema -> Domain
    domain_from_schema = mapper.schema_to_domain(
        mapper.domain_to_schema(mapper.schema_to_domain(schema))
    )
    assert domain_from_schema == domain
