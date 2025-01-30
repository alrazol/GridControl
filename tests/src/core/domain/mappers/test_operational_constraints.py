import pytest
from src.core.domain.models.operational_constraint import OperationalConstraint
from src.core.infrastructure.schemas import OperationalConstraintSchema
from src.core.domain.mappers.operational_constraints import OperationalConstraintsMapper
from src.core.domain.enums import BranchSide, OperationalConstraintType
from src.core.utils import generate_hash


@pytest.mark.parametrize(
    "schema, expected_domain",
    [
        # Test case: Valid OperationalConstraintSchema to OperationalConstraint mapping
        (
            OperationalConstraintSchema(
                uid=generate_hash(s="constraint_1"),
                element_uid=generate_hash(s="element_1"),
                element_id="element_1",
                side="TWO",
                name="Constraint 1",
                type="CURRENT",
                value=100.0,
                acceptable_duration=60,
            ),
            OperationalConstraint(
                uid=generate_hash(s="constraint_1"),
                element_uid=generate_hash(s="element_1"),
                element_id="element_1",
                side=BranchSide.TWO,
                name="Constraint 1",
                type=OperationalConstraintType.CURRENT,
                value=100.0,
                acceptable_duration=60,
            ),
        ),
    ],
)
def test_schema_to_domain(schema, expected_domain):
    """Test schema-to-domain mapping for OperationalConstraint."""
    mapper = OperationalConstraintsMapper()
    domain = mapper.schema_to_domain(schema)
    assert domain == expected_domain


@pytest.mark.parametrize(
    "domain, expected_schema",
    [
        # Test case: Valid OperationalConstraint to OperationalConstraintSchema mapping
        (
            OperationalConstraint(
                uid=generate_hash(s="constraint_1"),
                element_uid=generate_hash(s="element_1"),
                element_id="element_1",
                side=BranchSide.TWO,
                name="Constraint 1",
                type=OperationalConstraintType.CURRENT,
                value=100.0,
                acceptable_duration=60,
            ),
            OperationalConstraintSchema(
                uid=generate_hash(s="constraint_1"),
                element_uid=generate_hash(s="element_1"),
                element_id="element_1",
                side="TWO",
                name="Constraint 1",
                type="CURRENT",
                value=100.0,
                acceptable_duration=60,
            ),
        ),
    ],
)
def test_domain_to_schema(domain, expected_schema: OperationalConstraintSchema):
    """Test domain-to-schema mapping for OperationalConstraint."""
    mapper = OperationalConstraintsMapper()
    schema = mapper.domain_to_schema(domain)
    expected_schema_dict = expected_schema.__dict__.copy()
    schema_dict = schema.__dict__.copy()

    expected_schema_dict.pop("_sa_instance_state", None)
    schema_dict.pop("_sa_instance_state", None)

    # Convert to dict for easier comparison
    assert schema_dict == expected_schema_dict


@pytest.mark.parametrize(
    "schema, domain",
    [
        # Test case: Bidirectional consistency
        (
            OperationalConstraintSchema(
                uid=generate_hash(s="constraint_1"),
                element_uid=generate_hash(s="element_1"),
                element_id="element_1",
                side="TWO",
                name="Constraint 1",
                type="CURRENT",
                value=100.0,
                acceptable_duration=60,
            ),
            OperationalConstraint(
                uid=generate_hash(s="constraint_1"),
                element_uid=generate_hash(s="element_1"),
                element_id="element_1",
                side=BranchSide.TWO,
                name="Constraint 1",
                type=OperationalConstraintType.CURRENT,
                value=100.0,
                acceptable_duration=60,
            ),
        ),
    ],
)
def test_bidirectional_mapping(schema, domain):
    """Test bidirectional mapping consistency for OperationalConstraint."""
    mapper = OperationalConstraintsMapper()

    # Domain -> Schema -> Domain
    domain_from_schema = mapper.schema_to_domain(
        mapper.domain_to_schema(mapper.schema_to_domain(schema))
    )
    assert domain_from_schema == domain
