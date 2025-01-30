import pytest
from src.core.domain.models.elements_metadata.bus import (
    BusMetadata,
    BusStaticAttributes,
)
from src.core.domain.enums import State


@pytest.fixture
def static_attributes():
    """Fixture for static attributes of a 'BUS'."""
    return BusStaticAttributes(voltage_level_id="vl_1")


class TestBusMetadata:
    def test_valid_static_state(self, static_attributes):
        """Test that valid STATIC state does not raise errors."""
        metadata = BusMetadata(state=State.STATIC, static=static_attributes)
        assert metadata.state == State.STATIC
        assert metadata.static == static_attributes

    def test_invalid_state_raises_error(self, static_attributes):
        """Test that invalid state raises a ValueError."""
        invalid_states = [State.DYNAMIC, State.SOLVED]
        for state in invalid_states:
            with pytest.raises(
                ValueError,
                match=f"State has to be {State.STATIC} for a 'BUS' metadata.",
            ):
                BusMetadata(state=state, static=static_attributes)

    @pytest.mark.parametrize("invalid_state", [State.DYNAMIC, State.SOLVED])
    def test_invalid_states(self, static_attributes, invalid_state):
        """Test that invalid states raise a ValueError."""
        with pytest.raises(
            ValueError, match=f"State has to be {State.STATIC} for a 'BUS' metadata."
        ):
            BusMetadata(state=invalid_state, static=static_attributes)
