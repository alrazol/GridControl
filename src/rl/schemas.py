from sqlalchemy import Column, String, JSON, ForeignKey, Float, Integer
from src.core.infrastructure.database_base import Base
from sqlalchemy.orm import relationship


class ExperimentRecordsCollectionSchema(Base):
    __tablename__ = "experiment_records_collection"

    uid = Column(String, primary_key=True, nullable=False)
    id = Column(String, nullable=False)
    type = Column(String, nullable=False)
    episode = Column(Integer, nullable=True)
    created_at = Column(String, nullable=False)

    # Relationships
    records = relationship(
        "ExperimentRecordSchema",
        back_populates="collection",
        cascade="all, delete-orphan",
    )


class ExperimentRecordSchema(Base):
    __tablename__ = "experiment_record"

    uid = Column(String, primary_key=True, nullable=False)
    timestamp = Column(String, nullable=False)
    observation = Column(JSON, nullable=False)
    next_observation = Column(JSON, nullable=False)
    action = Column(JSON, nullable=False)
    reward = Column(Float, nullable=False)
    collection_uid = Column(
        String, ForeignKey("experiment_records_collection.uid"), nullable=False
    )

    # Relationship
    collection = relationship(
        "ExperimentRecordsCollectionSchema", back_populates="records"
    )
