import numpy as np


class NoiseGenerator:
    def __init__(self, mean=0, std=1, allow_negative=True):
        """
        Initialize the noise generator with parameters.

        Args:
            mean (float): Mean of the Gaussian noise.
            std (float): Standard deviation of the Gaussian noise.
            allow_negative (bool): Whether to allow negative values.
        """
        self.mean = mean
        self.std = std
        self.allow_negative = allow_negative

    def generate(self, base_array: np.ndarray) -> np.ndarray:
        """
        Add Gaussian noise to the base array.

        Args:
            base_array (np.ndarray): The base array to transform.

        Returns:
            np.ndarray: The transformed array with added noise.
        """
        noise = np.random.normal(self.mean, self.std, size=len(base_array))
        if not self.allow_negative:
            noise = np.maximum(noise, 0)
        return base_array + noise
