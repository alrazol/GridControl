from sqlalchemy import Column, String, JSON, ForeignKey, Float, Integer
from src.core.infrastructure.database_base import Base
from sqlalchemy.orm import relationship


class NetworkSchema(Base):
    __tablename__ = "network"

    uid = Column(String, primary_key=True, nullable=False)
    id = Column(String, nullable=False)

    # Relationships
    elements = relationship(
        "NetworkElementSchema", back_populates="network", cascade="all, delete-orphan"
    )


class NetworkElementSchema(Base):
    __tablename__ = "network_element"

    uid = Column(String, primary_key=True, nullable=False)
    id = Column(String, nullable=False)
    timestamp = Column(String, nullable=True)
    type = Column(String, nullable=False)
    element_metadata = Column(JSON, nullable=False)
    network_id = Column(String, ForeignKey("network.id"), nullable=False)

    # Relationship
    network = relationship("NetworkSchema", back_populates="elements")
    operational_constraints = relationship(
        "OperationalConstraintSchema",
        back_populates="network_element",
        cascade="all, delete-orphan",
    )


class OperationalConstraintSchema(Base):
    __tablename__ = "network_element_operational_constraint"

    uid = Column(String, primary_key=True, nullable=False)
    element_uid = Column(String, ForeignKey("network_element.uid"), nullable=False)
    element_id = Column(String, nullable=False)
    side = Column(String, nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    acceptable_duration = Column(Integer, nullable=False)

    # Relationship
    network_element = relationship(
        "NetworkElementSchema", back_populates="operational_constraints"
    )
