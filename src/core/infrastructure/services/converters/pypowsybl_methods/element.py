from datetime import datetime
from src.core.domain.models.element import NetworkElement
from src.core.domain.enums import State
from src.core.domain.models.elements_metadata import (
    GeneratorMetadata,
    LoadMetadata,
    BusMetadata,
    LineMetadata,
    TwoWindingsTransformersMetadata,
    VoltageLevelsMetadata,
    SubstationMetadata,
)
from src.core.constants import SupportedNetworkElementTypes, ElementStatus
from src.core.domain.models.operational_constraint import OperationalConstraint

# To Pypowsybl


def _bus_metadata_to_pypowsybl(element_id: str, element_metadata: BusMetadata) -> dict:
    """This converts the metadata for a 'BusMetadata' object to a pypowsybl compatible dict.'"""

    return {
        key: value
        for key, value in {
            "id": element_id,
            "voltage_level_id": element_metadata.static.voltage_level_id,
        }.items()
        if value is not None
    }


def _generator_metadata_to_pypowsybl(
    element_id: str, element_metadata: GeneratorMetadata
) -> dict:
    """Converts the metadata for a 'GeneratorMetadata' object to a pypowsybl-compatible dict."""

    if element_metadata.state != State.DYNAMIC:
        m = "State has to be dynamic to convert to Pypowsybl"
        raise ValueError(m)

    metadata_dict = {
        key: value
        for key, value in {
            "id": element_id,
            "voltage_level_id": element_metadata.static.voltage_level_id,
            "bus_id": element_metadata.static.bus_id,
            "max_p": element_metadata.static.Pmax,
            "min_p": element_metadata.static.Pmin,
            "target_p": element_metadata.dynamic.Ptarget,
            "target_v": element_metadata.dynamic.Vtarget,
            "voltage_regulator_on": element_metadata.static.is_voltage_regulator,
            "target_q": element_metadata.dynamic.Qtarget,
            "rated_s": element_metadata.dynamic.Srated,
        }.items()
        if value is not None
    }

    return metadata_dict


def _line_metadata_to_pypowsybl(
    element_id: str, element_metadata: LineMetadata
) -> dict:
    """Converts the metadata for a 'LineMetadata' object to a pypowsybl-compatible dict."""

    metadata_dict = {
        key: value
        for key, value in {
            "id": element_id,
            "voltage_level1_id": element_metadata.static.voltage_level1_id,
            "voltage_level2_id": element_metadata.static.voltage_level2_id,
            "bus1_id": element_metadata.static.bus1_id,
            "bus2_id": element_metadata.static.bus2_id,
            "b1": element_metadata.static.b1,
            "b2": element_metadata.static.b2,
            "g1": element_metadata.static.g1,
            "g2": element_metadata.static.g2,
            "r": element_metadata.static.r,
            "x": element_metadata.static.x,
            "connectable_bus1_id": element_metadata.static.connectable_bus1_id,
            "connectable_bus2_id": element_metadata.static.connectable_bus2_id,
            "name": element_metadata.static.name,
        }.items()
        if value is not None
    }
    return metadata_dict


def _load_metadata_to_pypowsybl(
    element_id: str, element_metadata: LoadMetadata
) -> dict:
    """Converts the metadata for a 'LoadMetadata' object to a pypowsybl-compatible dict."""

    if element_metadata.state != State.DYNAMIC:
        m = "State has to be dynamic to convert to Pypowsybl"
        raise ValueError(m)

    metadata_dict = {
        key: value
        for key, value in {
            "id": element_id,
            "name": element_metadata.static.name,
            "voltage_level_id": element_metadata.static.voltage_level_id,
            "bus_id": element_metadata.static.bus_id,
            "connectable_bus_id": element_metadata.static.connectable_bus_id,
            "node": element_metadata.static.node,
            "type": element_metadata.static.type,
            "p0": element_metadata.dynamic.Pd,
            "q0": element_metadata.dynamic.Qd,
        }.items()
        if value is not None
    }
    return metadata_dict


def _substation_metadata_to_pypowsybl(
    element_id: str, element_metadata: SubstationMetadata
) -> dict:
    """This converts the metadata for a 'GeneratorMetadata' object to a pypowsybl compatible dict.'"""

    return {
        key: value
        for key, value in {
            "id": element_id,
            "name": element_metadata.static.name,
            "country": element_metadata.static.country,
            "tso": element_metadata.static.tso,
        }.items()
        if value is not None
    }


def _transformer_metadata_to_pypowsybl(
    element_id: str, element_metadata: TwoWindingsTransformersMetadata
) -> dict:
    return {
        key: value
        for key, value in {
            "id": element_id,
            "voltage_level1_id": element_metadata.static.voltage_level1_id,
            "voltage_level2_id": element_metadata.static.voltage_level2_id,
            "bus1_id": element_metadata.static.bus1_id,
            "bus2_id": element_metadata.static.bus2_id,
            "rated_u1": element_metadata.static.rated_u1,
            "rated_u2": element_metadata.static.rated_u2,
            "rated_s": element_metadata.static.rated_s,
            "b": element_metadata.static.b,
            "g": element_metadata.static.g,
            "r": element_metadata.static.r,
            "x": element_metadata.static.x,
            "name": element_metadata.static.name,
        }.items()
        if value is not None
    }


def _voltage_level_metadata_to_pypowsybl(
    element_id: str, element_metadata: VoltageLevelsMetadata
) -> dict:
    return {
        key: value
        for key, value in {
            "id": element_id,
            "substation_id": element_metadata.static.substation_id,
            "topology_kind": element_metadata.static.topology_kind,
            "nominal_v": int(element_metadata.static.Vnominal),
            "low_voltage_limit": element_metadata.static.Vlimitlow,
            "high_voltage_limit": element_metadata.static.Vlimithigh,
            "name": element_metadata.static.name,
        }.items()
        if value is not None
    }


# From Pypowsybl


def _load_metadata_from_pypowsybl(element_metadata: dict) -> LoadMetadata:
    """Convert SOLVED metadata from Pypowsybl to our internal models."""
    from src.core.domain.models.elements_metadata.load import (
        LoadStaticAttributes,
        LoadDynamicAttributes,
        LoadSolvedAttributes,
    )

    static_dict = {
        "name": element_metadata.get("name"),
        "voltage_level_id": element_metadata.get("voltage_level_id"),
        "bus_id": element_metadata.get("bus_id"),
    }
    static = LoadStaticAttributes(**static_dict)

    dynamic_dict = {
        "Pd": element_metadata.get("p0"),
        "Qd": element_metadata.get("q0"),
    }
    dynamic = LoadDynamicAttributes(**dynamic_dict)

    solved_dict = {
        "p": element_metadata.get("p"),
        "q": element_metadata.get("q"),
        "i": element_metadata.get("i", None),
    }
    solved = LoadSolvedAttributes(**solved_dict)

    return LoadMetadata(
        state=State.SOLVED, static=static, dynamic=dynamic, solved=solved
    )


def _generator_metadata_from_pypowsybl(element_metadata: dict) -> GeneratorMetadata:
    """Convert SOLVED metadata from Pypowsybl to our internal models."""
    from src.core.domain.models.elements_metadata.generator import (
        GeneratorStaticAttributes,
        GeneratorDynamicAttributes,
        GeneratorSolvedAttributes,
    )

    static_dict = {
        "status": ElementStatus.ON,
        "voltage_level_id": element_metadata.get("voltage_level_id"),
        "bus_id": element_metadata.get("bus_id"),
        "Pmax": element_metadata.get("max_p"),
        "Pmin": element_metadata.get("min_p"),
        "is_voltage_regulator": element_metadata.get("voltage_regulator_on"),
    }
    static = GeneratorStaticAttributes(**static_dict)

    dynamic_dict = {
        "Ptarget": element_metadata.get("target_p"),
        "Vtarget": element_metadata.get("target_v"),
        "Qtarget": element_metadata.get("target_q"),
        "Srated": element_metadata.get("rated_s"),
    }
    dynamic = GeneratorDynamicAttributes(**dynamic_dict)

    solved_dict = {
        "p": element_metadata.get("p"),
        "q": element_metadata.get("q"),
        "i": element_metadata.get("i", None),
        "connected": element_metadata.get("connected"),
    }
    solved = GeneratorSolvedAttributes(**solved_dict)

    return GeneratorMetadata(
        state=State.SOLVED,
        static=static,
        dynamic=dynamic,
        solved=solved,
    )


def _line_metadata_from_pypowsybl(element_metadata: dict) -> LineMetadata:
    """Convert SOLVED metadata from Pypowsybl to our internal models."""
    from src.core.domain.models.elements_metadata.line import (
        LineStaticAttributes,
        LineSolvedAttributes,
    )

    static_dict = {
        "status": ElementStatus.ON,  # Necessarily on if comes from pypowsybl
        "voltage_level1_id": element_metadata.get("voltage_level1_id"),
        "voltage_level2_id": element_metadata.get("voltage_level2_id"),
        "bus1_id": element_metadata.get("bus1_id"),
        "bus2_id": element_metadata.get("bus2_id"),
        "b1": element_metadata.get("b1"),
        "b2": element_metadata.get("b2"),
        "g1": element_metadata.get("g1"),
        "g2": element_metadata.get("g2"),
        "r": element_metadata.get("r"),
        "x": element_metadata.get("x"),
    }
    static = LineStaticAttributes(**static_dict)

    solved_dict = {
        "p1": element_metadata.get("p1"),
        "q1": element_metadata.get("q1"),
        "i1": element_metadata.get("i1", None),
        "p2": element_metadata.get("p2"),
        "q2": element_metadata.get("q2"),
        "i2": element_metadata.get("i2", None),
    }
    solved = LineSolvedAttributes(**solved_dict)

    return LineMetadata(state=State.SOLVED, static=static, solved=solved)


# Exposed methods


def element_to_pypowsybl(element: NetworkElement) -> dict:  # NOTE: Maybe add the status
    """This takes a 'NetworkElement' and returns a Pypowsybl compat element based on metadata type."""

    MAP_ELEMENT_TYPE_TO_CONVERT_METHOD = {
        SupportedNetworkElementTypes.BUS: _bus_metadata_to_pypowsybl,
        SupportedNetworkElementTypes.GENERATOR: _generator_metadata_to_pypowsybl,
        SupportedNetworkElementTypes.LINE: _line_metadata_to_pypowsybl,
        SupportedNetworkElementTypes.LOAD: _load_metadata_to_pypowsybl,
        SupportedNetworkElementTypes.SUBSTATION: _substation_metadata_to_pypowsybl,
        SupportedNetworkElementTypes.TWO_WINDINGS_TRANSFORMERS: _transformer_metadata_to_pypowsybl,
        SupportedNetworkElementTypes.VOLTAGE_LEVEL: _voltage_level_metadata_to_pypowsybl,
    }

    return MAP_ELEMENT_TYPE_TO_CONVERT_METHOD[element.type](
        element_id=element.id,
        element_metadata=element.element_metadata,
    )


def element_from_pypowsybl(
    element_id: str,
    element_type: SupportedNetworkElementTypes,
    timestamp: datetime | None,
    network_id: str,
    element_metadata_pypowsybl: dict,
    operational_constraints: list[OperationalConstraint],
) -> NetworkElement:
    if element_type not in [
        SupportedNetworkElementTypes.LINE,
        SupportedNetworkElementTypes.LOAD,
        SupportedNetworkElementTypes.GENERATOR,
    ]:
        raise ValueError(f"Unsupported element type: {element_type}")

    MAP_ELEMENT_TYPE_TO_CONVERT_METHODS = {
        SupportedNetworkElementTypes.GENERATOR: _generator_metadata_from_pypowsybl,
        SupportedNetworkElementTypes.LOAD: _load_metadata_from_pypowsybl,
        SupportedNetworkElementTypes.LINE: _line_metadata_from_pypowsybl,
    }
    element_metadata = MAP_ELEMENT_TYPE_TO_CONVERT_METHODS[element_type](
        element_metadata=element_metadata_pypowsybl,
    )

    return NetworkElement.from_metadata(
        id=element_id,
        timestamp=timestamp,
        type=element_type,
        element_metadata=element_metadata,
        operational_constraints=operational_constraints,
        network_id=network_id,
    )
