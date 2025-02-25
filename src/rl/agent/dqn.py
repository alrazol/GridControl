import jax
import optax
import numpy as np
import jax.numpy as jnp
from typing import TypedDict
from gym.spaces import Space
from flax import nnx
from gym.spaces import Discrete, Box, Dict
from src.rl.agent.replay_buffer import ReplayBuffer
from src.rl.agent.base import BaseAgent
from src.rl.action_space import ActionSpace
from src.rl.observation.network import NetworkObservation


class DQNEnvVariables(TypedDict):
    action_space: ActionSpace
    observation_space: Discrete | Box | Dict
    one_hot_map: dict
    observation_memory_length: int


class DQNHyperParameters(TypedDict):
    learning_rate: float
    buffer_size: int
    gamma: float
    tau: float
    batch_size: int
    start_e: float
    end_e: float
    exploration_fraction: float
    timestep_target_network_update_freq: int


class QNetwork(nnx.Module):
    def __init__(
        self, action_dim: int, in_features: int, hidden_features: int, rngs: nnx.Rngs
    ):
        self.rngs = rngs
        self.action_dim = action_dim
        self.dense1 = nnx.Linear(in_features, hidden_features, rngs=self.rngs)
        self.dense2 = nnx.Linear(hidden_features, action_dim, rngs=self.rngs)

    def __call__(self, x: jax.Array) -> jax.Array:
        x = self.dense1(x)
        x = jax.nn.relu(x)
        x = self.dense2(x)
        return x


class DQNAgent(BaseAgent):
    def __init__(
        self,
        seed: int,
        action_space: ActionSpace,
        observation_space: Box,
        one_hot_map: dict,
        learning_rate: float,
        buffer_size: int,
        gamma: float,
        tau: float,
        batch_size: int,
        start_e: float,
        end_e: float,
        exploration_fraction: float,
        timestep_target_network_update_freq: int,
        observation_memory_length: int,
    ):
        self.env_variables: DQNEnvVariables = {
            "action_space": action_space,
            "observation_space": observation_space,
            "one_hot_map": one_hot_map,
            "observation_memory_length": observation_memory_length,
        }

        self.hyperparameters: DQNHyperParameters = {
            "learning_rate": learning_rate,
            "buffer_size": buffer_size,
            "gamma": gamma,
            "tau": tau,
            "batch_size": batch_size,
            "start_e": start_e,
            "end_e": end_e,
            "exploration_fraction": exploration_fraction,
            "timestep_target_network_update_freq": timestep_target_network_update_freq,
        }

        self.q_network = QNetwork(
            action_dim=action_space.to_gym().n,
            in_features=observation_space.shape[0],
            hidden_features=20,
            rngs=nnx.Rngs(seed),
        )

        self.target_network = QNetwork(
            action_dim=action_space.to_gym().n,
            in_features=observation_space.shape[0],
            hidden_features=20,
            rngs=nnx.Rngs(seed),
        )

        tx = optax.adam(self.hyperparameters.get("learning_rate"))
        self.optimizer = nnx.Optimizer(self.q_network, tx)

        self.replay_buffer = ReplayBuffer(
            buffer_size=buffer_size,
            observation_space=observation_space,
            action_space=action_space,
            one_hot_map=one_hot_map,
            seed=seed,
            device="cpu",
        )

        # We need this for selecting actions later on
        self.rng = np.random.default_rng(seed)

    def linear_schedule(
        self,
        start_e: float,
        end_e: float,
        num_timesteps: int,
        current_timestep: int,
    ):
        """
        This gives the formula for decaying epsilon. That is the probablity that an action is taken randomly.

        Params:
        - start_e (float): Start epsilon for decaying
        - end_e (float): End epsilon for decaying
        - num_timesteps (int): Total number of timesteps within an episode.
        - current_timestep (int): Current timestep.

        Returns:
            int: The decaying factor.
        """
        slope = (end_e - start_e) / num_timesteps
        return max(slope * current_timestep + start_e, end_e)

    def act(
        self,
        network_observation: NetworkObservation,
        current_timestep: int,
        num_timesteps: int,
        episode: int,
        seed: int,
    ) -> int:
        """
        Select an action based on the epsilon-greedy policy.

        Params:
        - state (NetworkState): The current NetworkState from which to decide action.
        - current_timestep (int): The current timestep, used for epsilon decaying.
        - num_timesteps (int): The total number of timesteps in the episode, used for epsilon decaying.

        Returns:
            - BaseAction: The chosen action.
        """

        epsilon = (
            self.linear_schedule(
                start_e=self.hyperparameters.get("start_e"),
                end_e=self.hyperparameters.get("end_e"),
                num_timesteps=self.hyperparameters.get("exploration_fraction")
                * num_timesteps,
                current_timestep=current_timestep,
            )
            if episode < 100  # TODO: Take this as an argument.
            else 0
        )
        if self.rng.random() < epsilon:
            # Exploration
            space: Space = self.env_variables.get("action_space").to_gym()
            space.seed(seed)
            action_idx = space.sample()
        else:
            # Exploitation
            q_values = self.q_network(
                network_observation.to_array(
                    one_hot_map=self.env_variables.get("one_hot_map")
                )
            )
            action_idx = jax.device_get(np.argmax(q_values))

        return self.env_variables.get("action_space").valid_actions[action_idx]

    @staticmethod
    # @nnx.jit
    def update(
        target_network: QNetwork,
        q_network: QNetwork,
        optimizer: optax.GradientTransformation,
        gamma: float,
        current_observations: np.ndarray,
        actions: np.ndarray,
        next_observations: np.ndarray,
        rewards: np.ndarray,
        dones: np.ndarray,
    ):
        """Learn procedure -> Will be passed with random samples from stored exp from memory buffer."""

        q_network.train()
        q_next_target = target_network(jnp.array(next_observations))
        q_next_target = jnp.max(q_next_target, axis=-1)
        next_q_value = (
            rewards + (1 - dones) * gamma * q_next_target
        )  # If gamma = 0, next q_value is simplu the reward and we don't need the target_net.

        def loss_fn(model: QNetwork):
            q_pred = model(
                jnp.array(current_observations)
            )  # What the model would have predicted for q_values in the situation.
            q_pred_reshaped = q_pred[  # We select the q_value predicted for the action that was actually taken in the current_observations situation.
                jnp.arange(q_pred.shape[0]), jnp.argmax(actions, axis=-1)
            ]
            return (
                (q_pred_reshaped - next_q_value) ** 2
            ).mean()  # We check the diff btw the estimation we had of the reward for that action and actual reward we got.

        # Update the Q network weights
        loss, grads = nnx.value_and_grad(loss_fn)(q_network)
        optimizer.update(grads)
        return loss
