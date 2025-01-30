# from itertools import chain
# from src.core.constants import SupportedNetworkElementTypes
# from src.core.domain.models.elements_metadata.bus import BusMetadata
# from src.core.domain.models.elements_metadata.generator import (
#    GeneratorMetadata,
#    #SolvedGeneratorMetadata,
#    #StaticGeneratorMetadata,
# )
# from src.core.domain.models.elements_metadata.line import (
#    LineMetadata,
#    #SolvedLineMetadata,
# )
# from src.core.domain.models.elements_metadata.load import (
#    LoadMetadata,
#    #StaticLoadMetadata,
#    #SolvedLoadMetadata,
# )
# from src.core.domain.models.elements_metadata.substation import SubstationMetadata
# from src.core.domain.models.elements_metadata.transformer import (
#    TwoWindingsTransformersMetadata,
# )
# from src.core.domain.models.elements_metadata.voltage_level import VoltageLevelsMetadata
# from src.core.domain.enums import State
#
# MetadataRegistry = {
#    SupportedNetworkElementTypes.LINE: {
#        State.STATIC: LineMetadata,
#        State.DYNAMIC: LineMetadata,
#        State.SOLVED: LineMetadata,
#    },
#    SupportedNetworkElementTypes.GENERATOR: {
#        State.STATIC: GeneratorMetadata,
#        State.DYNAMIC: GeneratorMetadata,
#        State.SOLVED: GeneratorMetadata,
#    },
#    SupportedNetworkElementTypes.LOAD: {
#        State.STATIC: LoadMetadata,
#        State.DYNAMIC: LoadMetadata,
#        State.SOLVED: LoadMetadata,
#    },
#    SupportedNetworkElementTypes.BUS: {
#        State.STATIC: BusMetadata,
#        State.DYNAMIC: BusMetadata,
#        State.SOLVED: BusMetadata,
#    },
#    SupportedNetworkElementTypes.SUBSTATION: {
#        State.STATIC: SubstationMetadata,
#        State.DYNAMIC: SubstationMetadata,
#        State.SOLVED: SubstationMetadata,
#    },
#    SupportedNetworkElementTypes.VOLTAGE_LEVEL: {
#        State.STATIC: VoltageLevelsMetadata,
#        State.DYNAMIC: VoltageLevelsMetadata,
#        State.SOLVED: VoltageLevelsMetadata,
#    },
#    SupportedNetworkElementTypes.TWO_WINDINGS_TRANSFORMERS: {
#        State.STATIC: TwoWindingsTransformersMetadata,
#        State.DYNAMIC: TwoWindingsTransformersMetadata,
#        State.SOLVED: TwoWindingsTransformersMetadata,
#    },
# }
#
# MetadataTypes = list(
#    set(
#        chain.from_iterable(
#            element_state.values() for element_state in MetadataRegistry.values()
#        )
#    )
# )
#
# StaticMetadataTypes = [entry[State.STATIC] for entry in MetadataRegistry.values()]
#
# DynamicMetadataTypes = [entry[State.DYNAMIC] for entry in MetadataRegistry.values()]
#
# SolvedMetadataTypes = [entry[State.SOLVED] for entry in MetadataRegistry.values()]
#
#
# ElementMetadataTypes = [LoadMetadata, LineMetadata, GeneratorMetadata, VoltageLevelsMetadata]

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
