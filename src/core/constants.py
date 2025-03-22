from enum import Enum
import datetime as dt

DEFAULT_TIMEZONE = dt.timezone.utc

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


class SupportedBackends(str, Enum):
    PYPOWSYBL = "PYPOWSYBL"


class LoadFlowType(str, Enum):
    AC = "AC"
    DC = "DC"


class State(str, Enum):
    STATIC = "STATIC"
    DYNAMIC = "DYNAMIC"
    SOLVED = "SOLVED"


class SupportedNetworkElementTypes(str, Enum):
    LINE = "LINE"
    GENERATOR = "GENERATOR"
    LOAD = "LOAD"
    BUS = "BUS"
    SUBSTATION = "SUBSTATION"
    VOLTAGE_LEVEL = "VOLTAGE_LEVEL"
    TWO_WINDINGS_TRANSFORMERS = "TWO_WINDINGS_TRANSFORMERS"


class SupportedNetworkElementMetadataTypes(str, Enum):
    LOAD = "LOAD_METADATA"


class BusTypes(str, Enum):
    SLACK = "SLACK"
    PQ = "PQ"
    PV = "PV"


class ElementStatus(str, Enum):
    ON = "ON"
    OFF = "OFF"
    OUTAGE = "OUTAGE"
    MAINTENANCE = "MAINTENANCE"


PYPOWSYBL_CREATION_METHODS = {
    SupportedNetworkElementTypes.SUBSTATION: ("create_substations", True),
    SupportedNetworkElementTypes.VOLTAGE_LEVEL: (
        "create_voltage_levels",
        True,
    ),
    SupportedNetworkElementTypes.BUS: ("create_buses", True),
    SupportedNetworkElementTypes.TWO_WINDINGS_TRANSFORMERS: (
        "create_2_windings_transformers",
        True,
    ),
    SupportedNetworkElementTypes.LINE: ("create_lines", False),
    SupportedNetworkElementTypes.LOAD: ("create_loads", False),
    SupportedNetworkElementTypes.GENERATOR: ("create_generators", False),
}
