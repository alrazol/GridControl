import pytest
from src.core.domain.enums import State
from src.core.domain.models.elements_metadata.transformer import (
    TwoWindingsTransformersStaticAttributes,
    TwoWindingsTransformersMetadata,
)


# Fixture for static attributes
@pytest.fixture
def static_attributes():
    """Fixture for static attributes of a 2-windings transformer."""
    return TwoWindingsTransformersStaticAttributes(
        voltage_level1_id="vl_1",
        voltage_level2_id="vl_2",
        bus1_id="bus_1",
        bus2_id="bus_2",
        rated_u1=220.0,
        rated_u2=110.0,
        rated_s=100.0,
        b=0.01,
        g=0.001,
        r=0.02,
        x=0.03,
        name="Main Transformer",
    )


# Test class for TwoWindingsTransformersMetadata
class TestTwoWindingsTransformersMetadata:
    def test_valid_static_state(self, static_attributes):
        """Test valid STATIC state with correct metadata."""
        metadata = TwoWindingsTransformersMetadata(
            state=State.STATIC, static=static_attributes
        )
        assert metadata.state == State.STATIC
        assert metadata.static == static_attributes

    def test_invalid_state_raises_error(self, static_attributes):
        """Test invalid states raise a ValueError."""
        invalid_states = [State.DYNAMIC, State.SOLVED]
        for state in invalid_states:
            with pytest.raises(ValueError, match=f"State has to be {State.STATIC}"):
                TwoWindingsTransformersMetadata(state=state, static=static_attributes)

    @pytest.mark.parametrize("invalid_state", [State.DYNAMIC, State.SOLVED])
    def test_invalid_states(self, static_attributes, invalid_state):
        """Parameterized test for invalid states."""
        with pytest.raises(ValueError, match=f"State has to be {State.STATIC}"):
            TwoWindingsTransformersMetadata(
                state=invalid_state, static=static_attributes
            )
