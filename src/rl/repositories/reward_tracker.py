from abc import ABC, abstractmethod
from plotly import graph_objects as go


class RewardTrackerRepository(ABC):
    @abstractmethod
    def add_reward(self):
        pass

    @abstractmethod
    def generate_figure(self) -> go.Figure:
        pass
