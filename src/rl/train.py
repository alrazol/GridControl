from pathlib import Path
from datetime import datetime
import mlflow
import gc
from src.rl.environment import NetworkEnvironment
from src.rl.agent.base import BaseAgent
from src.rl.artifacts.utils import create_experiment
from src.rl.agent.dqn import DQNAgent
from src.rl.artifacts.experiment_record import (
    ExperimentRecord,
    ExperimentRecordsCollection,
)
from src.rl.artifacts.loss import LossTrackerRepository
from src.rl.artifacts.reward import RewardTrackerRepository
from src.core.constants import DEFAULT_TIMEZONE
from src.core.utils import generate_hash
from src.rl.artifacts.utils import (
    log_fig_as_artifact,
    log_json_as_artifact,
    log_pytorch_model_as_artifact,
)
from src.rl.logger.logger import logger


def train(
    experiment_name: str,
    env: NetworkEnvironment,
    agent: BaseAgent,
    num_episodes: int,
    num_timesteps: int,
    seed: int,
    timestep_to_start_updating: int,
    timestep_update_freq: int,
    artifacts_location: Path,
    loss_tracker: LossTrackerRepository,
    reward_tracker: RewardTrackerRepository,
    log_model: bool,
    log_rollout_freq: int,
    registered_model_name: str | None,
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

    tags = {"experiment_type": "training"}
    logger.info(event="Creating experiment.", name=experiment_name)
    experiment_id = create_experiment(
        experiment_name=experiment_name,
        artifacts_location=artifacts_location / experiment_name,
        tags=tags,
    )

    experiment = mlflow.get_experiment(experiment_id=experiment_id)
    with mlflow.start_run(
        experiment_id=experiment_id,
    ):
        mlflow.log_params(
            params={
                "num_episodes": num_episodes,
                "num_timesteps": num_timesteps,
                "seed": seed,
                "timestep_to_start_updating": timestep_to_start_updating,
                "timestep_update_freq": timestep_update_freq,
                "agent_hyperparameters": agent.hyperparameters,
            }
        )

        for episode in range(1, num_episodes + 1):
            observation = env.reset()[0]
            total_reward = 0
            done = False
            episode_experiment_records = []

            for t in range(num_timesteps):
                action = agent.act(
                    network_observation=observation,
                    current_timestep=t,
                    num_timesteps=num_timesteps,
                    episode=episode,
                    seed=seed,
                )

                # Apply the action in the environment
                next_observation, reward, done, _ = env.step(action)
                total_reward += reward

                episode_experiment_records.append(
                    ExperimentRecord.from_record(
                        timestamp=observation.list_network_snapshot_observations()[
                            -1
                        ].timestamp,
                        observation=observation,
                        next_observation=next_observation,
                        action=action,
                        reward=reward,
                        collection_uid=generate_hash(f"{experiment.name}_{episode}"),
                    )
                )

                if isinstance(agent, DQNAgent):
                    agent.replay_buffer.add(
                        obs=observation,
                        next_obs=next_observation,
                        action=action,
                        reward=reward,
                        done=done,
                    )

                if t >= timestep_to_start_updating:
                    if t % timestep_update_freq == 0:
                        if isinstance(agent, DQNAgent):
                            data = agent.replay_buffer.sample(
                                agent.hyperparameters.get("batch_size")
                            )
                            loss = agent.update(
                                q_network=agent.q_network,
                                target_network=agent.target_network,
                                optimizer=agent.optimizer,
                                gamma=agent.hyperparameters.get("gamma"),
                                current_observations=data.observations,
                                actions=data.actions,
                                next_observations=data.next_observations,
                                rewards=data.rewards,
                                dones=data.dones,
                            )
                        loss_tracker.add_loss(loss=loss, episode=episode, timestamp=t)
                        logger.debug(episode=episode, timestamp=t, loss=loss)

                # if isinstance(agent, DQNAgent):
                #    if agent.timestep_target_network_update_freq:
                #        if t % agent.timestep_target_network_update_freq == 0:
                #            # TODO: We need equivalent of the state_dict
                #            agent.target_network.dense1 = agent.q_network.dense1
                #            agent.target_network.dense2 = agent.q_network.dense2

                observation = next_observation

                if done or t == num_timesteps:
                    break

            reward_tracker.add_reward(episode=episode, reward=total_reward)
            logger.info(episode=episode, episode_reward=total_reward)

            experiment_collection = ExperimentRecordsCollection.from_records(
                id=f"{experiment_name}",
                type="training",
                episode=episode,
                created_at=datetime.now(DEFAULT_TIMEZONE),
                records=episode_experiment_records,
            )
            if episode % log_rollout_freq == 0:
                log_json_as_artifact(
                    data=experiment_collection.to_dict(),
                    file_name=f"{experiment_name}_rollout_episode_{episode}.json",
                )

        log_fig_as_artifact(
            fig=reward_tracker.generate_figure(),
            file_name="reward_through_episodes.html",
        )
        log_fig_as_artifact(
            fig=loss_tracker.generate_figure(),
            file_name="loss_through_episodes.html",
        )

        if log_model:
            logger.info(event="Logging the model.")
            logger.info(
                event="Registering the model.", model_name=registered_model_name
            )
            log_pytorch_model_as_artifact(
                model=agent.q_network,
                X=agent.replay_buffer.observations[0],
                registered_model_name=registered_model_name
                if registered_model_name
                else experiment_name,
            )
