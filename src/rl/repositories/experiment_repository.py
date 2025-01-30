from abc import ABC, abstractmethod
from src.rl.simulation.models import ExperimentRecordsCollection


class ExperimentRepository(ABC):
    @abstractmethod
    def get(self, collection_id: str) -> ExperimentRecordsCollection:
        """
        Retrieve a ExperimentRecordsCollection from repo.
        """
        pass

    @abstractmethod
    def add(self, collection: ExperimentRecordsCollection) -> None:
        """
        Add an ExperimentRecordsCollection to the repo.
        """
        pass
