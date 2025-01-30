from pathlib import Path
from datetime import datetime
import mlflow
from src.rl.environment import NetworkEnvironment
from src.rl.agent.base import BaseAgent
from src.rl.artifacts.utils import create_experiment
from src.rl.artifacts.plotting import ArtifactsHandler
from src.rl.agent.dqn import DQNAgent
from src.rl.simulation.models import ExperimentRecord, ExperimentRecordsCollection
from src.rl.repositories.experiment_repository import ExperimentRepository
from src.core.constants import DEFAULT_TIMEZONE
from src.core.utils import generate_hash


def train(
    experiment_name: str,
    env: NetworkEnvironment,
    agent: BaseAgent,
    num_episodes: int,
    num_timesteps: int,
    timestep_to_start_updating: int,
    timestep_update_freq: int,
    experiments_dir: Path,
    experiment_records_repository: ExperimentRepository,
):
    """
    Train an agent's policy.

    Params:
    - experiment_name (str): The name for th mlflow experiment.
    - env (NetworkEnvironment): The simulator the agent interacts with.
    - agent (BaseAgent): The agent to train.
    - num_episodes (int): Number of episodes to train for.
    - num_timesteps (int): Number of timesteps to run within each episode.
    - timestep_to_start_updating (int): At which timestep to start updating the agent's policy.
    - timestep_update_freq (int): Once updating has started, the number of timesteps btw each update.
    - experiment_dir (Path): The directory in which to store the mlflow artifacts.
    """

    experiment_id = create_experiment(
        experiment_name=experiment_name, experiment_dir=experiments_dir
    )
    experiment = mlflow.get_experiment(experiment_id=experiment_id)
    loss_logger = ArtifactsHandler()

    with mlflow.start_run(
        experiment_id=experiment_id,
        run_name=experiment_name,
    ):
        for episode in range(1, num_episodes + 1):
            observation = env.reset()[0]
            total_reward = 0
            done = False
            episode_experiment_records = []

            for t in range(num_timesteps):
                # Select an action using the agent

                action = agent.act(
                    network_observation=observation,
                    current_timestep=t,
                    num_timesteps=num_timesteps,
                    episode=episode,
                )

                # Apply the action in the environment
                next_state, reward, done, _ = env.step(action)
                total_reward += reward

                episode_experiment_records.append(
                    ExperimentRecord.from_record(
                        timestamp=observation.timestamp,
                        observation=observation,
                        next_observation=next_state,
                        action=action,
                        reward=reward,
                        collection_uid=generate_hash(f"{experiment.name}_{episode}"),
                    )
                )

                if isinstance(agent, DQNAgent):
                    agent.replay_buffer.add(
                        obs=observation,
                        next_obs=next_state,
                        action=action,
                        reward=reward,
                        done=done,
                    )

                if t >= timestep_to_start_updating:
                    if t % timestep_update_freq == 0:
                        if isinstance(agent, DQNAgent):
                            data = agent.replay_buffer.sample(agent.batch_size)
                            loss = agent.update(
                                q_network=agent.q_network,
                                target_network=agent.target_network,
                                optimizer=agent.optimizer,
                                gamma=agent.gamma,
                                current_observations=data.observations,
                                actions=data.actions,
                                next_observations=data.next_observations,
                                rewards=data.rewards,
                                dones=data.dones,
                            )
                        loss_logger.add_loss(loss=loss, episode=episode, timestamp=t)

                if isinstance(agent, DQNAgent):
                    if agent.timestep_target_network_update_freq:
                        if t % agent.timestep_target_network_update_freq == 0:
                            # TODO: We need equivalent of the state_dict
                            agent.target_network.dense1 = agent.q_network.dense1
                            agent.target_network.dense2 = agent.q_network.dense2

                observation = next_state

                if done:
                    break

            experiment_collection = ExperimentRecordsCollection.from_records(
                id=f"{experiment_name}",
                type="training",
                episode=episode,
                created_at=datetime.now(DEFAULT_TIMEZONE),
                records=episode_experiment_records,
            )

            experiment_records_repository.add(collection=experiment_collection)

            print(f"Total reward for episode {episode} is {total_reward}")
            loss_logger.add_reward(reward=total_reward, episode=episode)
            loss_logger.plot_rolling_average_loss(
                directory=Path(experiment.artifact_location), window_size=20
            )
            loss_logger.plot_rewards(
                directory=Path(experiment.artifact_location), window_size=3
            )
