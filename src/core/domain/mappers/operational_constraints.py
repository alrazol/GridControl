from src.core.domain.models.operational_constraint import OperationalConstraint
from src.core.infrastructure.schemas import (
    OperationalConstraintSchema,
)
from src.core.domain.mappers.base import BaseMapper
from src.core.domain.enums import BranchSide, OperationalConstraintType


class OperationalConstraintsMapper(
    BaseMapper[OperationalConstraintSchema, OperationalConstraint]
):
    """
    Mapper for OperationalConstraint schema and domain model.
    """

    def schema_to_domain(
        self, schema: OperationalConstraintSchema
    ) -> OperationalConstraint:
        return OperationalConstraint(
            uid=schema.uid,
            element_uid=schema.element_uid,
            element_id=schema.element_id,
            side=BranchSide(schema.side),
            name=schema.name,
            type=OperationalConstraintType(schema.type),
            value=schema.value,
            acceptable_duration=schema.acceptable_duration,
        )

    def domain_to_schema(
        self, domain: OperationalConstraint
    ) -> OperationalConstraintSchema:
        return OperationalConstraintSchema(
            uid=domain.uid,
            element_uid=domain.element_uid,
            element_id=domain.element_id,
            side=domain.side.value,
            name=domain.name,
            type=domain.type.value,
            value=domain.value,
            acceptable_duration=domain.acceptable_duration,
        )
