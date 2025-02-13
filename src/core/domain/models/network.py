from datetime import datetime
import pandas as pd
from pydantic import field_validator
from src.core.domain.models.element import NetworkElement
from src.core.constants import SupportedNetworkElementTypes
from src.core.utils import parse_datetime_to_str
from pydantic import BaseModel


class Network(BaseModel):
    """
    Model of a network.

    uid: Unique identifier, based on the id aka name.
    id: Identifier, aka name of the network.
    state: Related to the state of the elements within the network (TODO: Get rid of this and keep only element level.)
    """

    uid: str
    id: str
    elements: list[NetworkElement]

    @field_validator("elements", mode="after", check_fields=False)
    def validate_timestamps_are_provided_and_unique_over_ids(
        cls,
        v: list[NetworkElement],
    ) -> list[NetworkElement]:
        """
        Validate that each element has a timestamp associated and that the combination of id and timestamp is unique.
        """

        # Use a set to track unique (id, timestamp) pairs
        seen = set()
        for element in v:
            pair = (element.id, element.timestamp)
            if pair in seen:
                raise ValueError(
                    f"Duplicate id/timestamp pair found: id={element.id}, timestamp={parse_datetime_to_str(element.timestamp)}."
                )
            seen.add(pair)

        return v

    def list_timestamps(self) -> list[datetime]:
        return sorted(set([i.timestamp for i in self.elements]))

    def list_elements(
        self,
        timestamp: datetime,
        element_type: SupportedNetworkElementTypes | None = None,
    ) -> NetworkElement:
        """Return elements of the network for a given timestamp."""
        timestamp_elements = [i for i in self.elements if i.timestamp == timestamp]
        if element_type:
            return [i for i in timestamp_elements if i.type == element_type]
        else:
            return timestamp_elements

    def get_element(self, id: str, timestamp: datetime) -> NetworkElement:
        """Get a unique element, given id and timestamp."""
        timestamp_elements = [i for i in self.elements if i.timestamp == timestamp]
        return [i for i in timestamp_elements if i.id == id][0]

    def to_dataframe(self, element_id: str) -> pd.DataFrame:
        """Pick an element and have it as a df. Can't do more than 1 as would be potentialy too big."""

        # Have to unpack the model element_metadata 1st
        selected_elements = [i for i in self.elements if i.id == element_id]
        element_dumps = []
        for element in selected_elements:
            element_metadata_dump = element.element_metadata.model_dump()
            element_dump = element.model_dump()
            element_dump["element_metadata"] = element_metadata_dump
            element_dumps.append(element_dump)
        df = pd.DataFrame(element_dumps)
        metadata_df = pd.json_normalize(df["element_metadata"])
        df = pd.concat([df, metadata_df], axis=1)
        df = df.drop(columns=["element_metadata"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.set_index(df["timestamp"])
        return df

    def pop_element(self, element_id: str) -> NetworkElement:
        """Pops the element out of the 'Network'."""

        for index, element in enumerate(self.elements):
            if element.id == element_id:
                return self.elements.pop(index), index
        raise ValueError(f"Element with id '{id}' not found.")

    def insert_element(self, element: NetworkElement, index: int) -> None:
        """Inserts an element into the 'Network'."""
        if any(i.id == element.id for i in self.elements):
            raise ValueError(f"Element with id '{element.id}' already exists.")
        self.elements.insert(index, element)
