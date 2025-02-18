import torch
import random
import torch.nn as nn
import torch.optim as optim
import numpy as np
from gym.spaces import Space
from src.rl.agent.replay_buffer import ReplayBuffer
from src.rl.agent.base import BaseAgent
from src.rl.action_space import ActionSpace
from src.rl.observation.network import NetworkObservation

torch.manual_seed(0)
np.random.seed(0)
random.seed(0)


class QNetwork(nn.Module):
    def __init__(
        self, action_dim: int, in_features: int, hidden_features: int, device: str
    ):
        super().__init__()
        self.device = device
        self.dense1 = nn.Linear(in_features, hidden_features)
        self.dense2 = nn.Linear(hidden_features, action_dim)

    def forward(self, x: np.ndarray) -> torch.Tensor:
        x = torch.tensor(x, dtype=torch.float32, device=self.device)
        x = self.dense1(x)
        x = torch.relu(x)
        x = self.dense2(x)
        return x


class DQNAgent(BaseAgent):
    def __init__(
        self,
        seed: int,
        action_space: ActionSpace,
        observation_space: Space,
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
        device: str = "cpu",
    ):
        # Env related info
        self.device = torch.device(device)
        self.action_space = action_space
        self.action_space_dim = action_space.to_gym().n
        self.observation_space = observation_space
        self.observation_space_dim = observation_space.shape[0]
        self.one_hot_map = one_hot_map
        self.seed = seed

        # Hyperparameters
        self.learning_rate = learning_rate
        self.buffer_size = buffer_size
        self.gamma = gamma
        self.tau = tau
        self.batch_size = batch_size
        self.start_e = start_e
        self.end_e = end_e
        self.exploration_fraction = exploration_fraction
        self.timestep_target_network_update_freq = timestep_target_network_update_freq

        # Network architecture
        self.q_network = QNetwork(
            action_dim=self.action_space_dim,
            in_features=self.observation_space_dim,
            hidden_features=20,
            device=self.device,
        ).to(self.device)

        self.target_network = QNetwork(
            action_dim=self.action_space_dim,
            in_features=self.observation_space_dim,
            hidden_features=20,
            device=self.device,
        ).to(self.device)
        self.target_network.load_state_dict(self.q_network.state_dict())
        self.target_network.eval()

        # Optimizer
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=self.learning_rate)

        # Replay buffer
        self.replay_buffer = ReplayBuffer(
            buffer_size=buffer_size,
            observation_space=observation_space,
            action_space=action_space,
            one_hot_map=self.one_hot_map,
            seed=seed,
        )

    def linear_schedule(
        self,
        start_e: float,
        end_e: float,
        num_timesteps: int,
        current_timestep: int,
    ):
        slope = (end_e - start_e) / num_timesteps
        return max(slope * current_timestep + start_e, end_e)

    def act(
        self,
        network_observation: NetworkObservation,
        current_timestep: int,
        num_timesteps: int,
        episode: int,
    ) -> int:
        """
        Select an action based on the epsilon-greedy policy.
        """
        epsilon = (
            self.linear_schedule(
                start_e=self.start_e,
                end_e=self.end_e,
                num_timesteps=self.exploration_fraction * num_timesteps,
                current_timestep=current_timestep,
            )
            if episode < 450
            else 0
        )

        if np.random.rand() < epsilon:
            action_idx = self.action_space.to_gym().sample()
        else:
            # obs_tensor = torch.tensor(
            #    network_observation.to_array(one_hot_map=self.one_hot_map),
            #    dtype=torch.float32,
            #    device=self.device,
            # )
            with torch.no_grad():
                q_values = self.q_network(
                    network_observation.to_array(one_hot_map=self.one_hot_map)
                )
                action_idx = torch.argmax(q_values).item()

        return self.action_space.valid_actions[action_idx]

    def update(
        self,
        current_observations: np.ndarray,
        actions: np.ndarray,
        next_observations: np.ndarray,
        rewards: np.ndarray,
        dones: np.ndarray,
    ):
        """
        Update the Q-network using experience replay.
        """
        self.q_network.train()

        # current_obs_tensor = torch.tensor(
        #    current_observations, dtype=torch.float32, device=self.device
        # )
        actions_tensor = torch.tensor(actions, dtype=torch.long, device=self.device)
        # next_obs_tensor = torch.tensor(
        #    next_observations, dtype=torch.float32, device=self.device
        # )
        rewards_tensor = torch.tensor(rewards, dtype=torch.float32, device=self.device)
        dones_tensor = torch.tensor(dones, dtype=torch.float32, device=self.device)

        with torch.no_grad():
            q_next_target = self.target_network(next_observations).max(dim=1)[0]
            next_q_value = (
                rewards_tensor + (1 - dones_tensor) * self.gamma * q_next_target
            )

        q_pred = self.q_network(current_observations)
        q_pred_selected = q_pred.gather(
            1, torch.argmax(actions_tensor, dim=-1).unsqueeze(-1)
        ).squeeze()

        loss = torch.nn.functional.mse_loss(q_pred_selected, next_q_value)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()

    def soft_update_target_network(self):
        """
        Soft update the target network parameters using Polyak averaging.
        """
        with torch.no_grad():
            for param, target_param in zip(
                self.q_network.parameters(), self.target_network.parameters()
            ):
                target_param.data.copy_(
                    self.tau * param.data + (1 - self.tau) * target_param.data
                )
