import numpy as np

class StableGenerator:
    def __init__(self, value: float):
        """
        Initialize the constant generator.

        Args:
            value (float): The constant value to generate.
        """
        self.value = value

    def generate(self, timestamps):
        """
        Generate a constant value for each timestamp.

        Args:
            timestamps (list or array-like): A list of timestamps.

        Returns:
            np.ndarray: A series of constant values.
        """
        return np.full(len(timestamps), self.value)
