from typing import Any, Self
from pathlib import Path
from pydantic import BaseModel, ConfigDict
from src.rl.config_loaders.utils import load_yaml


class AgentConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    config_path: Path
    agent: str
    description: dict[str, Any]
    action_types: list[str]
    rewards: Any
    hyperparameters: dict[str, Any]

    @classmethod
    def from_yaml(cls, config_path: Path) -> Self:
        config_json = load_yaml(config_path)
        return cls(
            config_path=config_path,
            agent=config_json.get("DESCRIPTION").get("agent"),
            action_types=config_json.get("ACTION_TYPES"),
            rewards=config_json.get("REWARDS"),
            description=config_json.get("DESCRIPTION"),
            hyperparameters=config_json.get("HYPER_PARAMETERS"),
        )
