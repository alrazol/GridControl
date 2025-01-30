import os
from typing import Generator
from dataclasses import dataclass
from src.core.infrastructure.settings import Settings


@dataclass
class Fixture:
    env: Settings


class Env:
    def __init__(self, env: dict):
        self.env_vars = {k: str(v) for k, v in env.items()}

    def __enter__(self):
        self.old_environ = dict(os.environ)
        os.environ.update(self.env_vars)
        return Settings()

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.environ.clear()
        os.environ.update(self.old_environ)


def fixture() -> Generator[Fixture, None, None]:
    env = {
        "DB_URL": "sqlite:///test.db",
        "SHOULD_CREATE_TABLES": True,
    }
    with Env(env=env) as settings:
        yield Fixture(env=settings) # TODO: The DB does not close at the end
