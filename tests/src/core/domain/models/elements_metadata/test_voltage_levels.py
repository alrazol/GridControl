import pytest
from src.core.domain.enums import State
from src.core.domain.models.elements_metadata.voltage_level import (
    VoltageLevelsStaticAttributes,
    VoltageLevelsMetadata,
)


# Fixture for static attributes
@pytest.fixture
def static_attributes():
    """Fixture for static attributes of a voltage level."""
    return VoltageLevelsStaticAttributes(
        topology_kind="BUS_BREAKER",
        Vnominal=220.0,
        substation_id="sub_1",
        Vlimitlow=200.0,
        Vlimithigh=240.0,
        name="Voltage Level 1",
    )


# Test class for VoltageLevelsMetadata
class TestVoltageLevelsMetadata:
    def test_valid_static_state(self, static_attributes):
        """Test valid STATIC state with correct metadata."""
        metadata = VoltageLevelsMetadata(state=State.STATIC, static=static_attributes)
        assert metadata.state == State.STATIC
        assert metadata.static == static_attributes

    def test_invalid_state_raises_error(self, static_attributes):
        """Test invalid states raise a ValueError."""
        invalid_states = [State.DYNAMIC, State.SOLVED]
        for state in invalid_states:
            with pytest.raises(ValueError, match=f"State has to be {State.STATIC}"):
                VoltageLevelsMetadata(state=state, static=static_attributes)

    @pytest.mark.parametrize("invalid_state", [State.DYNAMIC, State.SOLVED])
    def test_invalid_states(self, static_attributes, invalid_state):
        """Parameterized test for invalid states."""
        with pytest.raises(ValueError, match=f"State has to be {State.STATIC}"):
            VoltageLevelsMetadata(state=invalid_state, static=static_attributes)
