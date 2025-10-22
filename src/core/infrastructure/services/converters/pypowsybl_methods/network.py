import pypowsybl as pp
import pandas as pd
from src.core.domain.models.network import Network
from src.core.domain.models.element import NetworkElement
from src.core.constants import ElementStatus, SupportedNetworkElementTypes
from src.core.infrastructure.services.converters.pypowsybl_methods.element import (
    element_to_pypowsybl,
)
from src.core.infrastructure.services.converters.pypowsybl_methods.models.pypowsybl_network_wrapper import (
    PyPowSyblNetworkWrapper,
)
from pypowsybl.network import Network as Pypowsyblnetwork


def network_to_pypowsybl(network: Network) -> PyPowSyblNetworkWrapper:
    """
    Convert a network into PyPowSybl networks (one network per timestamp).

    :return: A dictionary mapping timestamps to PyPowSyblNetwork objects.
    """

    def _create_network_from_elements(
        elements: list[NetworkElement],
    ) -> tuple[Pypowsyblnetwork, list[NetworkElement]]:
        """This helper deals with converting a list of network elements into a PyPowSybl network."""

        PYPOWSYBL_CREATION_METHODS = {
            SupportedNetworkElementTypes.SUBSTATION: ("create_substations", True),
            SupportedNetworkElementTypes.VOLTAGE_LEVEL: (
                "create_voltage_levels",
                True,
            ),
            SupportedNetworkElementTypes.BUS: ("create_buses", False),
            SupportedNetworkElementTypes.TWO_WINDINGS_TRANSFORMERS: (
                "create_2_windings_transformers",
                True,
            ),
            SupportedNetworkElementTypes.LINE: ("create_lines", False),
            SupportedNetworkElementTypes.LOAD: ("create_loads", False),
            SupportedNetworkElementTypes.GENERATOR: ("create_generators", False),
        }

        network = pp.network.create_empty()
        data = {etype: [] for etype in SupportedNetworkElementTypes}
        off_elements = []
        for element in elements:
            element_dict = element_to_pypowsybl(element=element)
            if element.type in [
                SupportedNetworkElementTypes.LINE,
                SupportedNetworkElementTypes.GENERATOR,
            ]:  # Those elements have a status attribute.
                if element.element_metadata.static.status == ElementStatus.ON:
                    data[element.type].append(element_dict)
                else:
                    off_elements.append(element)
                    continue
            else:
                data[element.type].append(element_dict)

        # Create elements in the PyPowSybl network
        for element_type, (
            method_name,
            use_dataframe,
        ) in PYPOWSYBL_CREATION_METHODS.items():
            element_data = data.get(element_type, None)
            if element_data:
                create_method = getattr(network, method_name)
                if use_dataframe:
                    create_method(pd.DataFrame.from_records(element_data, index="id"))
                else:
                    for item in element_data:
                        create_method(**item)

        return network, off_elements

    result = {}
    unique_timestamps = sorted(set([i.timestamp for i in network.elements]))
    unique_timestamps = sorted({i.timestamp for i in network.elements})

    result = {
        t: _create_network_from_elements(
            [i for i in network.elements if i.timestamp == t]
        )
        for t in unique_timestamps
    }

    return PyPowSyblNetworkWrapper(data=result)
