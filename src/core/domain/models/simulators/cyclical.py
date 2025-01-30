import numpy as np


class CyclicalGenerator:
    def __init__(self, amplitude, period, offset, phase_shift=0):
        """
        Initialize the generator with parameters.

        Args:
            amplitude (float): The amplitude of the sine wave.
            period (int): The period of the sine wave.
            phase_shift (float): The phase shift of the sine wave (in radians).
        """
        self.amplitude = amplitude
        self.period = period
        self.phase_shift = phase_shift
        self.offset = offset

    def generate(self, base_array: np.ndarray) -> np.ndarray:
        """
        Apply a cyclical transformation to the base array.

        Args:
            base_array (np.ndarray): The base array to transform.

        Returns:
            np.ndarray: The transformed array.
        """
        time_steps = np.arange(len(base_array))
        transformation = self.amplitude * np.sin(
            (2 * np.pi * time_steps / self.period) + self.phase_shift
        )

        return base_array + self.offset + transformation
