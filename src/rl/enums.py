from enum import Enum


class ActionTypes(str, Enum):
    SWITCH_ACTION = "SWITCH_ACTION"
    DO_NOTHING = "DO_NOTHING"


class Granularity(Enum):
    HOUR = 1
    DAY = 24
    WEEK = 168


class OutageType(Enum):
    SHORT_TERM = (24, 48)
    MID_TERM = (48, 72)
    LONG_TERM = (72, 150)

    @property
    def lower_duration(self):
        return self.value[0]

    @property
    def upper_duration(self):
        return self.value[1]
