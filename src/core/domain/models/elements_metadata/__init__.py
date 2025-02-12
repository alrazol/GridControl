from src.core.domain.models.elements_metadata.base import BaseMetadata
from src.core.domain.models.elements_metadata.bus import BusMetadata
from src.core.domain.models.elements_metadata.load import LoadMetadata
from src.core.domain.models.elements_metadata.line import LineMetadata
from src.core.domain.models.elements_metadata.generator import GeneratorMetadata
from src.core.domain.models.elements_metadata.substation import SubstationMetadata
from src.core.domain.models.elements_metadata.transformer import (
    TwoWindingsTransformersMetadata,
)
from src.core.domain.models.elements_metadata.voltage_level import VoltageLevelsMetadata
from src.core.constants import SupportedNetworkElementTypes


__all__ = [
    "BaseMetadata",
    "BusMetadata",
    "LoadMetadata",
    "LineMetadata",
    "GeneratorMetadata",
    "SubstationMetadata",
    "TwoWindingsTransformersMetadata",
    "VoltageLevelsMetadata",
]

MetadataRegistry = {
    SupportedNetworkElementTypes.LINE: LineMetadata,
    SupportedNetworkElementTypes.BUS: BusMetadata,
    SupportedNetworkElementTypes.GENERATOR: GeneratorMetadata,
    SupportedNetworkElementTypes.LOAD: LoadMetadata,
    SupportedNetworkElementTypes.SUBSTATION: SubstationMetadata,
    SupportedNetworkElementTypes.VOLTAGE_LEVEL: VoltageLevelsMetadata,
    SupportedNetworkElementTypes.TWO_WINDINGS_TRANSFORMERS: TwoWindingsTransformersMetadata,
}
