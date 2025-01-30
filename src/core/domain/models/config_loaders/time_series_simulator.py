from pathlib import Path
from typing import Any
from pydantic import BaseModel, field_validator
import yaml


class GeneratorStep(BaseModel):
    name: str
    parameters: dict[str, Any]


class ParameterConfig(BaseModel):
    steps: list[GeneratorStep]


class ElementConfig(BaseModel):
    id: str
    type: str
    parameters: dict[str, ParameterConfig]


class Config(BaseModel):
    network_id: str
    elements: list[ElementConfig]

    @classmethod
    def from_yaml(cls, path: Path):
        with open(path, "r") as file:
            config = yaml.safe_load(file)
        return cls(**config)

    @property
    def generators(self) -> dict[str, dict[str, list[GeneratorStep]]]:
        """
        Expose generators for each element in the configuration.

        Returns:
            Dict[str, dict[str, list[GeneratorStep]]]:
                A dictionary mapping element IDs to their parameters and associated generators.
        """
        return {
            element.id: {
                param_name: param_config
                for param_name, param_config in element.parameters.items()
            }
            for element in self.elements
        }

    @field_validator("elements", mode="after")
    def validate_unique_ids(cls, elements):
        ids = [element.id for element in elements]
        if len(ids) != len(set(ids)):
            raise ValueError("All elements must have unique IDs. Duplicate IDs found.")
        return elements
