import pytest
from src.core.domain.enums import State
from src.core.domain.models.elements_metadata.substation import (
    SubstationStaticAttributes,
    SubstationMetadata,
)


# Fixture for static attributes
@pytest.fixture
def static_attributes():
    """Fixture for static attributes of a substation."""
    return SubstationStaticAttributes(
        name="Main Substation",
        country="Country A",
        tso="TSO A",
    )


# Test class for SubstationMetadata
class TestSubstationMetadata:
    def test_valid_static_state(self, static_attributes):
        """Test valid STATIC state with correct metadata."""
        metadata = SubstationMetadata(state=State.STATIC, static=static_attributes)
        assert metadata.state == State.STATIC
        assert metadata.static == static_attributes

    def test_invalid_state_raises_error(self, static_attributes):
        """Test invalid states raise a ValueError."""
        invalid_states = [State.DYNAMIC, State.SOLVED]
        for state in invalid_states:
            with pytest.raises(ValueError, match=f"State has to be {State.STATIC}"):
                SubstationMetadata(state=state, static=static_attributes)

    @pytest.mark.parametrize("invalid_state", [State.DYNAMIC, State.SOLVED])
    def test_invalid_states(self, static_attributes, invalid_state):
        """Parameterized test for invalid states."""
        with pytest.raises(ValueError, match=f"State has to be {State.STATIC}"):
            SubstationMetadata(state=invalid_state, static=static_attributes)
