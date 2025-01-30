from abc import ABC, abstractmethod
from src.rl.action.base import BaseAction


class BaseAgent(ABC):
    """
    Base class for RL agents.
    """

    @abstractmethod
    def act(self) -> BaseAction:
        """
        Get an action from the agent.
        """
        pass

    @staticmethod
    @abstractmethod
    def update() -> float | None:
        """
        Update the agent policy. Staticmethod because of jax compat.
        Return the loss if relevant.
        """
        pass
