from src.rl.mappers.base import BaseMapper
from src.rl.schemas import ExperimentRecordSchema
from src.rl.simulation.models import ExperimentRecord
from src.core.utils import parse_datetime_to_str, parse_datetime


class ExperimentRecordMapper(BaseMapper[ExperimentRecordSchema, ExperimentRecord]):
    """
    Mapper for an ExperimentRecord schema and domain model.
    """

    def schema_to_domain(self, schema: ExperimentRecordSchema) -> ExperimentRecord:
        return ExperimentRecord(
            uid=schema.uid,
            timestamp=parse_datetime(schema.timestamp),
            observation=schema.observation,
            next_observation=schema.next_observation,
            action=schema.action,
            reward=schema.reward,
            collection_uid=schema.collection_uid,
        )

    def domain_to_schema(self, domain: ExperimentRecord) -> ExperimentRecordSchema:
        return ExperimentRecordSchema(
            uid=domain.uid,
            timestamp=parse_datetime_to_str(d=domain.timestamp),
            observation=domain.observation.to_dict(),
            next_observation=domain.next_observation.to_dict(),
            action=domain.action.__dict__,
            reward=domain.reward,
            collection_uid=domain.collection_uid,
        )
