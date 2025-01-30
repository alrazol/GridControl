import numpy as np
import pandas as pd
from typing import NamedTuple
from pathlib import Path
from gym.spaces import Space
from src.rl.action.action_space import ActionSpace
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
        self.obs_shape = observation_space.shape[0]
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

    def save_buffer(self, directory: Path):
        """Save the buffer as a df."""

        def _concat_single_obs_to_all_timestamps(
            d: list[dict[str, pd.DataFrame]],
        ) -> dict[str, pd.DataFrame]:
            """
            Make a list of dicts with single row obs dfs a dict with dfs of all timestamps.
            """
            all_data = {}
            for df_dict in d:
                for k, df in df_dict.items():
                    if k not in all_data.keys():
                        all_data[k] = df
                    else:
                        all_data[k] = pd.concat([all_data[k], df], axis=0)
            return all_data

        observations_dfs: list[dict[str, pd.DataFrame]] = [
            obs.to_dataframe() for obs in self.observations_objects
        ]
        next_observations_dfs = [
            next_obs.to_dataframe() for next_obs in self.next_observations_objects
        ]
        actions = [
            self.action_space.valid_actions[np.argmax(act)]
            for act in self.actions
            if np.max(act) == 1
        ]
        actions_dfs = []
        for act in actions:
            actions_dict = {
                "action": [act.action_type],
                "target_element": [act.element_id],
            }
            actions_dfs.append(pd.DataFrame(data=actions_dict))
        rewards_dfs = []
        for reward in self.rewards:
            reward_dict = {"reward": [reward]}
            rewards_dfs.append(pd.DataFrame(reward_dict))

        rewards_dfs = rewards_dfs[0 : self.pos]

        all_data_obs = _concat_single_obs_to_all_timestamps(d=observations_dfs)
        all_data_next_obs = _concat_single_obs_to_all_timestamps(
            d=next_observations_dfs
        )
        all_data_actions = pd.concat([i for i in actions_dfs], axis=0)
        all_data_rewards = pd.concat([i for i in rewards_dfs], axis=0)

        directory.mkdir(parents=True, exist_ok=True)

        all_data_obs["GENERATOR"].to_csv(directory / "obs_generators.csv")
        all_data_obs["LOAD"].to_csv(directory / "obs_loads.csv")
        all_data_obs["LINE"].to_csv(directory / "obs_lines.csv")
        all_data_next_obs["GENERATOR"].to_csv(directory / "next_obs_generators.csv")
        all_data_next_obs["LOAD"].to_csv(directory / "next_obs_loads.csv")
        all_data_next_obs["LINE"].to_csv(directory / "next_obs_lines.csv")
        all_data_actions.to_csv(directory / "actions.csv")
        all_data_rewards.to_csv(directory / "rewards.csv")
