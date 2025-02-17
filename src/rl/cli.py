from pathlib import Path
import typer
import mlflow
from src.rl.environment import make_env
from src.rl.train import train
from src.rl.repositories import Repositories
from src.core.constants import LoadFlowType
from src.core.infrastructure.settings import Settings
from src.rl.config_loaders.experiment import ExperimentConfig
from src.rl import agent as agent_module
from src.rl.logger.logger import logger
import cProfile

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
    log_model: bool = typer.Option(
        False, help="Whether to log the model as an artifact."
    ),
    registered_model_name: str = typer.Option(
        None, help="The name of the model in the registry."
    ),
    seed: int = typer.Option(42, help="Seed for reproducibility."),
) -> None:
    """
    Train an RL agent in a specified environment.
    """

    try:
        config = ExperimentConfig.from_yaml(config_path=agent_config_path)
        repositories = Repositories(s=settings)

        logger.info(event="Initialising environment.", id=network_id)

        env = make_env(
            network_id=network_id,
            network_repository=repositories.get_network_repository(),
            loadflow_solver=repositories.get_solver(),
            network_builder=repositories.get_network_builder(),
            network_snapshot_observation_builder=repositories.get_network_snapshot_observation_builder(),
            action_space_builder=repositories.get_action_space_builder(),
            one_hot_map_builder=repositories.get_one_hot_map_builder(),
            network_observation_handler=repositories.get_network_observation_handler(),
            network_transition_handler=repositories.get_network_transition_handler(),
            loadflow_type=loadflow_type,
            reward_handler=repositories.get_reward_handler(
                aggregator_name=config.rewards.get("rewards_aggregator"),
                rewards=config.rewards.get("rewards"),
            ),
            action_types=config.action_types,
            observation_memory_length=config.hyperparameters.get(
                "observation_memory_length"
            ),
        )

        logger.info(event="Initialising the agent.", config_path=agent_config_path)

        if config.agent == "DQNAgent":
            config.hyperparameters.update(
                {
                    "action_space": env.action_space,
                    "observation_space": env.observation_space,
                    "one_hot_map": env.one_hot_map,
                    "seed": seed,
                }
            )
        agent = getattr(agent_module, config.agent)(**config.hyperparameters)

        logger.info(event="Starting training.")

        train(
            experiment_name=experiment_name,
            env=env,
            agent=agent,
            num_episodes=num_episodes,
            num_timesteps=num_timesteps,
            timestep_to_start_updating=timestep_to_start_updating,
            timestep_update_freq=timestep_update_freq,
            artifacts_location=artifacts_location,
            loss_tracker=repositories.get_loss_tracker(),
            reward_tracker=repositories.get_reward_tracker(),
            log_model=log_model,
            registered_model_name=registered_model_name,
            seed=seed,
        )

        logger.info(event="Finished training.")

    except Exception as _:
        logger.error("Unhandled exception", exc_info=True)
        raise


if __name__ == "__main__":
    import cProfile
    import pstats

    profile_filename = "profile_output.prof"

    def run():
        app()  # Runs the typer CLI

    cProfile.run("run()", profile_filename)
    print(f"Profiling complete. Output saved to {profile_filename}")
