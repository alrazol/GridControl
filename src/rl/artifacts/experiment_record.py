from datetime import datetime
from typing import Self
from src.rl.action.base import BaseAction
from src.rl.observation.network import NetworkObservation
from typing import Literal
from src.core.utils import generate_hash, parse_datetime_to_str


class ExperimentRecord:
    """This class is used to represent a single record of an inference experiment."""

    def __init__(
        self,
        uid: str,
        timestamp: datetime,
        observation: NetworkObservation,
        next_observation: NetworkObservation,
        action: BaseAction,
        reward: float,
        collection_uid: str,
    ) -> None:
        self.uid = uid
        self.timestamp = timestamp
        self.observation = observation
        self.next_observation = next_observation
        self.action = action
        self.reward = reward
        self.collection_uid = collection_uid

    @classmethod
    def from_record(
        cls,
        timestamp: datetime,
        observation: NetworkObservation,
        next_observation: NetworkObservation,
        action: BaseAction,
        reward: float,
        collection_uid: str,
    ) -> Self:
        return cls(
            uid=generate_hash(s=f"{timestamp}_{collection_uid}"),
            timestamp=timestamp,
            observation=observation,
            next_observation=next_observation,
            action=action,
            reward=reward,
            collection_uid=collection_uid,
        )

    def to_dict(self) -> dict:
        return {
            "uid": self.uid,
            "timestamp": parse_datetime_to_str(self.timestamp),
            "observation": self.observation.to_dict(),
            "next_observation": self.next_observation.to_dict(),
            "action": self.action.__dict__,
            "reward": self.reward,
            "collection_uid": self.collection_uid,
        }


class ExperimentRecordsCollection:
    """This class is used to collect records."""

    def __init__(
        self,
        uid: str,
        id: str,
        type: Literal["training", "predict"],
        episode: int | None,
        created_at: datetime,
        records: list[ExperimentRecord],
    ) -> None:
        self.uid = uid
        self.id = id
        self.type = type
        self.episode = episode
        self.created_at = created_at
        self.records = records

    @classmethod
    def from_records(
        cls,
        id: str,
        type: Literal["training", "predict"],
        episode: int | None,
        created_at: datetime,
        records: list[ExperimentRecord],
    ) -> Self:
        return cls(
            uid=generate_hash(f"{id}_{episode}"),
            id=id,
            type=type,
            episode=episode,
            created_at=created_at,
            records=records,
        )

    def to_dict(self):
        return {
            "uid": self.uid,
            "id": self.id,
            "type": self.type,
            "episode": self.episode,
            "created_at": parse_datetime_to_str(self.created_at),
            "records": [i.to_dict() for i in self.records],
        }
