from enum import Enum


class ActionTypes(str, Enum):
    SWITCH_ACTION = "SWITCH_ACTION"
    DO_NOTHING = "DO_NOTHING"

class DoNothingFlag(str, Enum):
    DO_NOTHING = "DO_NOTHING"
    ACT = "ACT"
