from pathlib import Path
import typer
import mlflow
from src.rl.environment import NetworkEnvironment
from src.rl.train import train
from src.rl.repositories import Repositories
from src.core.constants import LoadFlowType
from src.core.infrastructure.settings import Settings
from src.rl.reward.line_overload import LineOverloadReward
from src.rl.reward.minimal_usage import MinimalUsageReward
from src.rl.reward.load_matching import LoadMatchingReward
from src.rl.reward.linear_aggregator import LinearRewardAggregator
from src.rl.config_loaders.experiment import ExperimentConfig
from src.rl import agent as agent_module
from src.rl.logger.logger import logger

app = typer.Typer()
settings = Settings()

mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)


@app.command()
def train_experiment(
    experiment_name: str = typer.Option(..., help="Name of the MLflow experiment."),
    network_id: str = typer.Option(..., help="The ID of the environment to train in."),
    agent_config_path: Path = typer.Option(
        ..., help="Path to the agent's config file."
    ),
    loadflow_type: LoadFlowType = typer.Option(
        ..., help="The loadflow used in simulation."
    ),
    num_episodes: int = typer.Option(..., help="Number of episodes to train for."),
    num_timesteps: int = typer.Option(..., help="Number of timesteps per episode."),
    timestep_to_start_updating: int = typer.Option(
        ..., help="At which timestep to start updating the agent's policy."
    ),
    timestep_update_freq: int = typer.Option(
        ..., help="Once updating has started, the number of timesteps btw each update"
    ),
    artifacts_location: Path = typer.Option(
        settings.ARTIFACTS_LOCATION,
        help="The directory in which to store the mlflow artifacts.",
    ),
) -> None:
    """
    Train an RL agent in a specified environment.
    """

    logger.info(
        event="Starting experiment.",
        name=experiment_name,
    )

    config = ExperimentConfig.from_yaml(config_path=agent_config_path)
    repositories = Repositories(s=settings)

    logger.info(event="Initialising environment.", id=network_id)

    env = NetworkEnvironment.from_network_id(
        network_id=network_id,
        network_repository=repositories.get_network_repository(),
        loadflow_solver=repositories.get_solver(),
        loadflow_type=loadflow_type,
        reward_handler=LinearRewardAggregator(
            rewards=[LineOverloadReward, MinimalUsageReward, LoadMatchingReward]
        ),
        action_types=config.action_types,
    )

    logger.info(event="Initialising the agent.", config_path=agent_config_path)

    if config.agent == "DQNAgent":
        config.hyperparameters.update(
            {
                "action_space": env.action_space,
                "observation_space": env.observation_space,
                "one_hot_map": env.one_hot_map,
            }
        )
    agent = getattr(agent_module, config.agent)(**config.hyperparameters)

    logger.info(event="Starting training.", agent_config=config.config_path)

    train(
        experiment_name=experiment_name,
        env=env,
        agent=agent,
        num_episodes=num_episodes,
        num_timesteps=num_timesteps,
        timestep_to_start_updating=timestep_to_start_updating,
        timestep_update_freq=timestep_update_freq,
        artifacts_location=artifacts_location,
        experiment_records_repository=repositories.get_experiment_repository(),
        loss_tracker=repositories.get_loss_tracker(),
        reward_tracker=repositories.get_reward_tracker()
    )
    typer.echo("Training complete!")


if __name__ == "__main__":
    app()
