import copy
from typing import Self
from src.rl.outage.outage_handler import OutageHandler
from src.core.domain.models.network import Network
from src.rl.action.base import BaseAction
from src.core.constants import ElementStatus, SupportedNetworkElementTypes
from src.rl.action.enums import DiscreteActionTypes
from src.core.utils import parse_datetime
from src.core.constants import DATETIME_FORMAT, DEFAULT_TIMEZONE


class StartMaintenanceAction(BaseAction):
    """Represents an action to send an element into maintenance in the network."""

    def __init__(
        self,
        element_id: str,
    ) -> None:
        super().__init__(
            action_type=DiscreteActionTypes.START_MAINTENANCE,
        )
        self.element_id = element_id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StartMaintenanceAction):
            return False
        return self.element_id == other.element_id

    def __hash__(self) -> int:
        return hash(self.element_id)

    @property
    def original_status(self):
        """Used to store the status of the element before getting sent to maintenance."""
        return self._original_status

    @original_status.setter
    def original_status(self, value: ElementStatus) -> None:
        self._original_status = value

    @classmethod
    def from_network(
        cls,
        element_id: str | None,
        network: Network,
        parameters: dict | None = None,
    ) -> Self:
        """Build action instance from network, allows some validation at instantiation."""

        cls.validate(
            network=network,
            element_id=element_id,
        )

        instance = cls(
            network=network,
            element_id=element_id,
            parameters=parameters,
        )

        # Validation ensures that the network has only elements of a single timestamp.
        instance.original_status = network.get_element(
            id=element_id,
            timestamp=parse_datetime(
                network.elements[0].timestamp,
                format=DATETIME_FORMAT,
                tz=DEFAULT_TIMEZONE,
            ),
        ).element_metadata.static.status

        return instance

    def validate(
        self,
        network: Network,
        element_id: str,
    ) -> None:
        """Validates whether the action can be applied to a given Network."""

        elements = [i for i in network.elements]
        if element_id not in [i.id for i in elements]:
            raise ValueError(
                f"Element ID {element_id} does not exist in the network state."
            )

        if [i for i in elements if i.id == element_id][0].type not in [
            SupportedNetworkElementTypes.LINE,
        ]:
            raise ValueError("StartMaintenance action only applies to 'LINE'.")

        if isinstance(network, Network):
            if len(network.list_timestamps()) > 1:
                raise ValueError("Action can only apply to single timestamp Network.")

        if network.get_element(
            id=element_id, timestamp=network.elements[0].timestamp
        ).element_metadata.static.status in [
            ElementStatus.MAINTENANCE,
            ElementStatus.OUTAGE,
        ]:
            raise ValueError(
                "Can't send an element to maintenance that is already under maintenance or outage."
            )

        return True

    def execute(self, network: Network) -> Network:
        """Executes the maintenance action on the network."""

        if self.validate(network, self.element_id):
            network_copy = copy.deepcopy(network)
            element, index = network_copy.pop_element(element_id=self.element_id)

            # Set the element to maintenance state
            element.element_metadata.static.status = ElementStatus.MAINTENANCE

            network_copy.insert_element(element=element, index=index)
        return network_copy
