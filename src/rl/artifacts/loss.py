from abc import ABC, abstractmethod
from plotly import graph_objects as go


class LossTrackerRepository(ABC):
    @abstractmethod
    def add_loss(self):
        pass

    @abstractmethod
    def generate_figure(self) -> go.Figure:
        pass
