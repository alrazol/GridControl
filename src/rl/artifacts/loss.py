import pandas as pd
from plotly import graph_objects as go
from src.rl.repositories.loss_tracker import LossTrackerRepository


class LossTracker(LossTrackerRepository):
    """
    Tracks loss values during training and generates a Plotly figure.
    """

    def __init__(self):
        self.loss_history = []

    def add_loss(self, episode: int, timestamp: int, loss: float):
        self.loss_history.append((episode, timestamp, loss))

    def generate_figure(self) -> go.Figure:
        """
        Generates a Plotly figure for the loss history.

        Returns:
            go.Figure: A Plotly figure object.
        """
        if not self.loss_history:
            raise ValueError("No loss data to generate figure.")

        df = pd.DataFrame(self.loss_history, columns=["episode", "timestamp", "loss"])

        fig = go.Figure()
        for episode, group in df.groupby("episode"):
            fig.add_trace(
                go.Scatter(
                    x=group["timestamp"],
                    y=group["loss"],
                    mode="lines+markers",
                    name=f"Episode {episode}",
                )
            )
        fig.update_layout(
            title="Loss History per Episode",
            xaxis_title="Timestamp",
            yaxis_title="Loss",
            legend_title="Episodes",
        )

        return fig
