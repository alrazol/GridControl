from pathlib import Path
import mlflow
from plotly import graph_objects as go


class ArtifactsHandler:
    """
    This class is used to store and compute different kinds of artifacts
    related to the training of the RL agent.
    """

    def __init__(self):
        self.losses = []
        self.reward_history = []
        self.max_reward_history = []

    def add_loss(self, loss, episode, timestamp):
        """Add a new loss value to the history with episode and timestamp."""
        self.losses.append({"loss": loss, "episode": episode, "timestamp": timestamp})

    def add_reward(self, reward, episode):
        """Add a new reward value to the history with episode and timestamp."""
        self.reward_history.append({"reward": reward, "episode": episode})

    def add_max_reward(self, reward, episode):
        """Add a new reward value to the history with episode and timestamp."""
        self.max_reward_history.append({"reward": reward, "episode": episode})

    def compute_average_loss(self, window_size=10):
        """
        Compute the average loss over the last `window_size` steps.
        If there are fewer than `window_size` losses, compute over all available.
        """
        if len(self.losses) == 0:
            return 0
        start_index = max(0, len(self.losses) - window_size)
        losses = [entry["loss"] for entry in self.losses[start_index:]]
        return sum(losses) / len(losses)

    def compute_average_reward(self, window_size=10):
        """
        Compute the average reward over the last `window_size` steps.
        If there are fewer than `window_size` rewards, compute over all available.
        """
        if len(self.reward_history) == 0:
            return 0
        start_index = max(0, len(self.reward_history) - window_size)
        rewards = [entry["reward"] for entry in self.reward_history[start_index:]]
        return sum(rewards) / len(rewards)

    def plot_rolling_average_loss(self, directory: Path, window_size=10):
        """
        Plot the rolling average loss for each episode on the same graph.
        """
        fig = go.Figure()

        # Group losses by episode
        losses_by_episode = {}
        for entry in self.losses:
            episode = entry["episode"]
            if episode not in losses_by_episode:
                losses_by_episode[episode] = []
            losses_by_episode[episode].append(entry["loss"])

        # Compute rolling averages and plot
        for episode, episode_losses in losses_by_episode.items():
            if len(episode_losses) > 0:
                rolling_avg = self.compute_rolling_average_loss(
                    episode_losses, window_size
                )
                fig.add_trace(
                    go.Scatter(
                        x=list(range(len(rolling_avg))),
                        y=rolling_avg,
                        mode="lines",
                        name=f"Episode {episode}",
                    )
                )

        fig.update_layout(
            title="Rolling Average Loss per Episode",
            xaxis_title="Timestep",
            yaxis_title="Loss",
            legend_title="Episodes",
            template="plotly_white",
        )

        fig.write_html(directory / "loss_per_episode.html")
        mlflow.log_artifact(
            local_path=(directory / "loss_per_episode.html").as_posix(),
        )

    def plot_rewards(self, directory: Path, window_size=3):
        """
        Plot the rewards per episode, with an option to include a rolling average.

        Parameters:
        - rolling_window (int, optional): If provided, computes and plots a rolling average
        of rewards over the specified number of episodes.
        """
        fig = go.Figure()

        # Extract rewards and episodes
        episodes = [entry["episode"] for entry in self.reward_history]
        rewards = [entry["reward"] for entry in self.reward_history]

        # Plot the raw rewards
        fig.add_trace(
            go.Scatter(
                x=episodes,
                y=rewards,
                mode="lines+markers",
                name="Reward per Episode",
            )
        )

        # Plot rolling average if specified
        if window_size:
            rolling_avg = self.compute_rolling_average_reward(rewards, window_size)
            fig.add_trace(
                go.Scatter(
                    x=episodes,
                    y=rolling_avg,
                    mode="lines",
                    name=f"Rolling Average (Window: {window_size})",
                )
            )

        fig.update_layout(
            title="Reward per Episode",
            xaxis_title="Episode",
            yaxis_title="Reward",
            legend_title="Legend",
            template="plotly_white",
        )

        fig.write_html(directory / "rewards_per_episode.html")
        mlflow.log_artifact(
            local_path=(directory / "rewards_per_episode.html").resolve().as_posix(),
        )

    def compute_rolling_average_reward(self, rewards, window_size):
        """
        Compute the rolling average for a list of rewards over a specified window size.

        Parameters:
        - rewards (list): The list of rewards.
        - window_size (int): The size of the rolling window.

        Returns:
        - list: A list of rolling average rewards.
        """
        rolling_avg = []
        for i in range(len(rewards)):
            start_index = max(0, i - window_size + 1)
            rolling_avg.append(
                sum(rewards[start_index : i + 1]) / (i - start_index + 1)
            )
        return rolling_avg

    def compute_rolling_average_loss(self, losses, window_size=10):
        """
        Compute the rolling average loss over the provided losses with a specified window size.
        """
        rolling_avg = []
        for i in range(len(losses)):
            start_index = max(0, i - window_size + 1)
            rolling_avg.append(sum(losses[start_index : i + 1]) / (i - start_index + 1))
        return rolling_avg

    def reset(self):
        """Reset the stored losses and rewards."""
        self.losses = []
        self.reward_history = []
