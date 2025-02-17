import pandas as pd
from plotly import graph_objects as go
from src.rl.artifacts.reward import RewardTrackerRepository


class RewardTracker(RewardTrackerRepository):
    """
    Tracks reward values during training and generates a Plotly figure.
    """

    def __init__(self):
        self.reward_history = []

    def add_reward(self, episode: int, reward: float):
        self.reward_history.append((episode, reward))

    def generate_figure(self) -> go.Figure:
        """
        Generates a Plotly figure for the loss history.

        Returns:
            go.Figure: A Plotly figure object.
        """
        if not self.reward_history:
            raise ValueError("No reward data to generate figure.")

        df = pd.DataFrame(self.reward_history, columns=["episode", "reward"])

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["episode"],
                y=df["reward"],
                mode="lines+markers",
                name="Reward per Episode",
            )
        )
        fig.update_layout(
            title="Reward History",
            xaxis_title="Episode",
            yaxis_title="Reward",
            legend_title="Reward",
        )

        return fig
