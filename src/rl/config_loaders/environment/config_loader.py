from typing import Self, Any
from pathlib import Path
from pydantic import BaseModel, ConfigDict
from src.rl.config_loaders.utils import load_yaml


# TODO: Ultimately, we'll specify some config names mapped to a dict of dependencies.
# Instead of specifying all the dependencies in the config file. This will ensure
# that used dependencies are consistent with each other.
class EnvironmentConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    config_path: Path
    one_hot_map_builder: str
    network_transition_handler: str
    network_snapshot_builder: str
    outage_handler_config: dict[str, Any] | None

    @classmethod
    def from_yaml(cls, config_path: Path) -> Self:
        config_json = load_yaml(config_path)
        return cls(
            config_path=config_path,
            one_hot_map_builder=config_json.get("PARAMETERS").get(
                "one_hot_map_builder"
            ),
            network_snapshot_builder=config_json.get("PARAMETERS").get("network_snapshot_builder"),
            network_transition_handler=config_json.get("PARAMETERS").get(
                "network_transition_handler"
            ),
            outage_handler_config=config_json.get("PARAMETERS").get(
                "outage_handler_config"
            ),
        )
