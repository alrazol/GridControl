import pytest
import copy
from src.core.domain.models.network import Network
from src.core.domain.models.element import NetworkElement
from src.rl.action.maintenance import StartMaintenanceAction
from src.core.constants import ElementStatus, SupportedNetworkElementTypes
from src.core.utils import parse_datetime
from src.core.constants import DATETIME_FORMAT, DEFAULT_TIMEZONE
from datetime import datetime


# @pytest.fixture
# def mock_network_elements() -> list[NetworkElement]:


# @pytest.fixture
# def mock_network() -> Network:
#     """Fixture to create a sample network with a single timestamp."""
#     # Mock network object with necessary elements
#     # Mock elements (assuming a method to create elements exists)
#     elements = [
#         MockElement(
#             id="line_1",
#             type=SupportedNetworkElementTypes.LINE,
#             status=ElementStatus.OPERATIONAL,
#             timestamp=timestamp,
#         ),
#         MockElement(
#             id="gen_1",
#             type=SupportedNetworkElementTypes.GENERATOR,
#             status=ElementStatus.OPERATIONAL,
#             timestamp=timestamp,
#         ),
#         MockElement(
#             id="load_1",
#             type=SupportedNetworkElementTypes.LOAD,
#             status=ElementStatus.OPERATIONAL,
#             timestamp=timestamp,
#         ),  # Unsupported type
#     ]

#     return MockNetwork(elements=elements)


# @pytest.fixture
# def action():
#     """Fixture to create a StartMaintenanceAction instance."""
#     return lambda element_id, network: StartMaintenanceAction.from_network(
#         element_id=element_id, network=network
#     )


# def test_validate_valid_action(action, sample_network):
#     """Test that validation passes for a valid action."""
#     start_maintenance = action("line_1", sample_network)
#     assert start_maintenance.validate(sample_network) is True


# def test_validate_invalid_element_id(action, sample_network):
#     """Test that validation fails if the element ID does not exist."""
#     with pytest.raises(
#         ValueError, match="Element ID invalid_id does not exist in the network state."
#     ):
#         action("invalid_id", sample_network)


# def test_validate_invalid_element_type(action, sample_network):
#     """Test that validation fails if the element type is not supported."""
#     with pytest.raises(
#         ValueError,
#         match="StartMaintenance action only applies to 'LINE' and 'GENERATOR'.",
#     ):
#         action("load_1", sample_network)


# def test_validate_multiple_timestamps(action):
#     """Test that validation fails if the network has multiple timestamps."""
#     elements = [
#         MockElement(
#             id="line_1",
#             type=SupportedNetworkElementTypes.LINE,
#             status=ElementStatus.OPERATIONAL,
#             timestamp=datetime(2024, 1, 1),
#         ),
#         MockElement(
#             id="gen_1",
#             type=SupportedNetworkElementTypes.GENERATOR,
#             status=ElementStatus.OPERATIONAL,
#             timestamp=datetime(2024, 1, 2),
#         ),
#     ]
#     network = MockNetwork(elements=elements)

#     with pytest.raises(
#         ValueError, match="Action can only apply to single timestamp Network."
#     ):
#         action("line_1", network)


# def test_execute_changes_status(action, sample_network):
#     """Test that executing the action changes the status of the element."""
#     start_maintenance = action("line_1", sample_network)
#     modified_network = start_maintenance.execute(sample_network)

#     element = modified_network.get_element("line_1")
#     assert element.element_metadata.static.status == ElementStatus.MAINTENANCE


# def test_execute_does_not_modify_original_network(action, sample_network):
#     """Test that executing the action does not modify the original network instance."""
#     original_network = copy.deepcopy(sample_network)
#     start_maintenance = action("line_1", sample_network)
#     _ = start_maintenance.execute(sample_network)

#     assert (
#         sample_network.get_element("line_1").element_metadata.static.status
#         == ElementStatus.OPERATIONAL
#     )
#     assert (
#         sample_network == original_network
#     )  # Ensure the original network is unchanged
