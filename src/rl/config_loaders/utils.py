import yaml
from pathlib import Path


def load_yaml(file_path: str):
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    with open(file_path, "r") as file:
        return yaml.safe_load(file)
