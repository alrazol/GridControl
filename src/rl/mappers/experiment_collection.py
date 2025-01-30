from src.rl.mappers.base import BaseMapper
from src.rl.mappers.experiment_record import ExperimentRecordMapper
from src.rl.schemas import ExperimentRecordsCollectionSchema
from src.rl.simulation.models import ExperimentRecordsCollection
from src.core.utils import parse_datetime, parse_datetime_to_str


class ExperimentRecordsCollectionMapper(BaseMapper):
    """
    Mapper for ExperimentRecordsCollection schema and domain model.
    """

    def __init__(self) -> None:
        self.experiment_record_mapper = ExperimentRecordMapper()

    def schema_to_domain(
        self, schema: ExperimentRecordsCollectionSchema
    ) -> ExperimentRecordsCollection:
        domain_records = [
            self.experiment_record_mapper.schema_to_domain(record)
            for record in schema.records
        ]
        return ExperimentRecordsCollection.from_records(
            id=schema.id,
            type=schema.type,
            episode=schema.episode,
            created_at=parse_datetime(d=schema.created_at),
            records=domain_records,
        )

    def domain_to_schema(
        self, domain: ExperimentRecordsCollection
    ) -> ExperimentRecordsCollectionSchema:
        schema_records = [
            self.experiment_record_mapper.domain_to_schema(record)
            for record in domain.records
        ]
        return ExperimentRecordsCollectionSchema(
            uid=domain.uid,
            id=domain.id,
            type=domain.type,
            episode=domain.episode,
            created_at=parse_datetime_to_str(d=domain.created_at),
            records=schema_records,
        )
