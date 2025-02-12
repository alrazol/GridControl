import numpy as np
from typing import NamedTuple
from gym.spaces import Space
from src.rl.action_space import ActionSpace
from src.rl.action.base import BaseAction
from src.rl.observation.network import NetworkObservation


class ReplayBufferSamples(NamedTuple):
    observations_objects: NetworkObservation
    observations: np.ndarray
    actions: np.ndarray
    next_observations: np.ndarray
    dones: np.ndarray
    rewards: np.ndarray


class ReplayBuffer:
    def __init__(
        self,
        buffer_size: int,
        observation_space: Space,
        action_space: ActionSpace,
        one_hot_map: dict,
        seed: int = None,
        device: str = "cpu",
    ) -> None:
        """This class represents a memory buffer."""
        self.buffer_size = buffer_size
        self.observation_space = observation_space
        self.action_space = action_space
        self.one_hot_map = one_hot_map
        self.obs_shape = observation_space.shape[0] #* 2 # TODO: Deal with
        self.action_dim = action_space.to_gym().n
        self.pos = 0
        self.full = False
        self.device = device
        self.observations_objects = []
        self.observations = np.zeros(
            (self.buffer_size, +self.obs_shape), dtype=observation_space.dtype
        )
        self.next_observations_objects = []
        self.next_observations = np.zeros(
            (self.buffer_size, +self.obs_shape), dtype=observation_space.dtype
        )
        self.actions_objects = []
        self.actions = np.zeros(
            (self.buffer_size, self.action_dim), dtype=action_space.to_gym().dtype
        )
        self.rewards = np.zeros((self.buffer_size), dtype=np.float32)
        self.dones = np.zeros((self.buffer_size), dtype=np.float32)
        self.rng = np.random.default_rng(seed)

    def add(
        self,
        obs: NetworkObservation,
        next_obs: NetworkObservation,
        action: BaseAction,
        reward: np.ndarray,
        done: np.ndarray,
    ) -> None:
        self.observations_objects.append(obs)
        self.observations[self.pos] = obs.to_array(one_hot_map=self.one_hot_map).copy()
        self.next_observations_objects.append(next_obs)
        self.next_observations[self.pos] = next_obs.to_array(
            one_hot_map=self.one_hot_map
        ).copy()
        one_hot = []  # TODO: Make a method with an inverse?
        for i in self.action_space.valid_actions:
            one_hot.append(1 if i == action else 0)
        self.actions_objects.append(action)
        self.actions[self.pos] = np.array(one_hot).copy()
        self.rewards[self.pos] = np.array(reward).copy()
        self.dones[self.pos] = np.array(0 if done is False else 1).copy()

        self.pos += 1
        if self.pos == self.buffer_size:
            self.full = True
            self.pos = 0

    def sample(self, batch_size: int) -> ReplayBufferSamples:
        """Sample from the buffer."""

        if self.full:
            batch_inds = (
                self.rng.integers(1, self.buffer_size, size=batch_size) + self.pos
            ) % self.buffer_size
        else:
            batch_inds = self.rng.integers(0, self.pos, size=batch_size)
        return self._get_samples(batch_inds)

    def _get_samples(self, batch_inds: np.ndarray) -> ReplayBufferSamples:
        data = (
            [self.observations_objects[i] for i in batch_inds],
            self.observations[batch_inds, :],
            self.actions[batch_inds, :],
            self.next_observations[batch_inds, :],
            self.dones[batch_inds],
            self.rewards[batch_inds],
        )
        return ReplayBufferSamples(*tuple(data))
