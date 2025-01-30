from src.rl.agent.base import BaseAgent
from src.rl.action.do_nothing import DoNothingAction
from src.rl.action.base import BaseAction


class DoNothingAgent(BaseAgent):
    """
    This agent does not update its policy and always selects the DoNothing action.
    """

    def __init__(self) -> None:
        pass

    def act(self, **kwargs) -> BaseAction:
        return DoNothingAction()

    @staticmethod
    def update() -> int:
        return 0
