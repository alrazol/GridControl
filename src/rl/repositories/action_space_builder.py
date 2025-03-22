from src.rl.outage.outage_handler import OutageHandler
from src.rl.action_space_builder import ActionSpaceBuilder
from src.rl.action.enums import DiscreteActionTypes
from src.core.domain.models.network import Network
from src.rl.action_space import ActionSpace
from src.rl.action import (
    BaseAction,
    SwitchAction,
    DoNothingAction,
    StartMaintenanceAction,
)


class DefaultActionSpaceBuilder(ActionSpaceBuilder):
    @staticmethod
    def from_action_types(
        action_types: list[DiscreteActionTypes],
        network: Network,
        outage_handler: OutageHandler,
    ) -> ActionSpace:
        """
        Build an ActionSpace from a list of BaseAction.
        """

        def _check_network_is_unique_timestamp(network: Network) -> None:
            """
            An ActionSpace can only cover a unique timestamped Network.
            """
            if len(set([i.timestamp for i in network.elements])) > 1:
                raise ValueError(
                    "Can't have more than one timestamp for an ActionSpace."
                )

        def _instanciate_actions(
            action_types: list[DiscreteActionTypes],
            network: Network,
        ) -> list[BaseAction]:
            """
            Instanciate all actions regardless of validity.
            """
            all_actions = []
            if DiscreteActionTypes.DO_NOTHING in action_types:
                all_actions.append(DoNothingAction())
            for element in network.elements:
                for action_type in action_types:
                    if action_type == DiscreteActionTypes.DO_NOTHING:
                        continue
                    elif action_type == DiscreteActionTypes.SWITCH:
                        all_actions.append(SwitchAction(element_id=element.id))
                    elif action_type == DiscreteActionTypes.START_MAINTENANCE:
                        all_actions.append(
                            StartMaintenanceAction(element_id=element.id)
                        )
            return all_actions

        def _validate_actions(
            actions: list[BaseAction],
            network: Network,
            outage_handler: OutageHandler,
        ) -> tuple[list[BaseAction], list[BaseAction]]:
            """
            Given instanciated BaseAction, validate them against the network.
            """
            valid_actions = []
            invalid_actions = []
            if len(set(actions)) != len(actions):
                raise ValueError("Some actions in the list are duplicated.")
            for action in actions:
                try:
                    if isinstance(action, SwitchAction):
                        action.validate(
                            network=network,
                            element_id=action.element_id,
                            outage_handler=outage_handler,
                        )
                    elif isinstance(action, DoNothingAction):
                        valid_actions.append(action)
                        continue
                    elif isinstance(action, StartMaintenanceAction):
                        action.validate(network=network, element_id=action.element_id)
                    valid_actions.append(action)
                except ValueError as _:
                    invalid_actions.append(action)
            return valid_actions, invalid_actions

        _check_network_is_unique_timestamp(network)
        valid_actions, invalid_actions = _validate_actions(
            _instanciate_actions(action_types=action_types, network=network),
            network,
            outage_handler,
        )
        return ActionSpace(
            action_types=action_types,
            valid_actions=valid_actions,
            invalid_actions=invalid_actions,
        )
