from src.core.infrastructure.adapters import Adapters
from src.core.infrastructure.settings import Settings
from src.core.domain import UseCases


# TODO: Add logger here.
class Configuration:
    def __init__(self, s: Settings) -> None:
        self.settings = s
        self._adapters = None
        self._use_cases = None

    @property
    def adapters(self):
        return self._adapters

    @adapters.setter
    def adapters(self, value):
        self._adapters = value

    @property
    def use_cases(self):
        return self._use_cases

    @use_cases.setter
    def use_cases(self, value):
        self._use_cases = value

    def __enter__(self) -> UseCases:
        print("Start")
        self.adapters = Adapters(settings=self.settings)
        self.use_cases = UseCases(p=self.adapters)
        return self.use_cases

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("End")
