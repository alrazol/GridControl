from enum import Enum


class DiscreteActionTypes(str, Enum):
    """This is actions that are discrete by nature, either you pick or not."""

    SWITCH = "SwitchAction"
    DO_NOTHING = "DoNothingAction"


class ContinuousActionTypes(str, Enum):
    """This is actions that can't be easily discretised, like choosing a real value for a paramater."""
    pass
