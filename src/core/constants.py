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


# TODO: Get rid of this, make it something linked to the to_pypowsybl methods
PYPOWSYBL_CANDIDATE_KEYS_MAPPING = {
    SupportedNetworkElementTypes.BUS: {
        "id",
        "voltage_level_id",
    },
    SupportedNetworkElementTypes.LINE: {
        "id",
        "voltage_level1_id",
        "voltage_level2_id",
        "bus1_id",
        "bus2_id",
        "b1",
        "b2",
        "g1",
        "g2",
        "r",
        "x",
        "connectable_bus1_id",
        "connectable_bus2_id",
        "name",
    },
    SupportedNetworkElementTypes.LOAD: {
        "id",
        "name",
        "voltage_level_id",
        "bus_id",
        "connectable_bus_id",
        "node",
        "type",
        "p0",
        "q0",
    },
    SupportedNetworkElementTypes.GENERATOR: {
        "id",
        "voltage_level_id",
        "bus_id",
        "max_p",
        "min_p",
        "target_p",
        "target_v",
        "voltage_regulator_on",
        "target_q",
        "rated_s",
    },
    SupportedNetworkElementTypes.SUBSTATION: {
        "id",
        "name",
        "country",
        "tso",
    },
    SupportedNetworkElementTypes.VOLTAGE_LEVEL: {
        "id",
        "substation_id",
        "topology_kind",
        "nominal_v",
        "low_voltage_limit",
        "high_voltage_limit",
        "name",
    },
    SupportedNetworkElementTypes.TWO_WINDINGS_TRANSFORMERS: {
        "id",
        "voltage_level1_id",
        "voltage_level2_id",
        "bus1_id",
        "bus2_id",
        "rated_u1",
        "rated_u2",
        "rated_s",
        "b",
        "g",
        "r",
        "x",
        "name",
    },
}


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
