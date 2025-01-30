import pytest
from src.core.domain.enums import State
from src.core.constants import ElementStatus
from src.core.domain.models.elements_metadata.line import (
    LineStaticAttributes,
    LineSolvedAttributes,
    LineMetadata,
)


# Fixtures for attributes
@pytest.fixture
def static_attributes():
    """Fixture for static attributes of a 'LINE'."""
    return LineStaticAttributes(
        status=ElementStatus.ON,
        voltage_level1_id="vl_1",
        voltage_level2_id="vl_2",
        bus1_id="bus_1",
        bus2_id="bus_2",
        b1=0.01,
        b2=0.01,
        g1=0.001,
        g2=0.001,
        r=0.02,
        x=0.03,
        connectable_bus1_id=None,
        connectable_bus2_id=None,
        name="Main Line",
    )


@pytest.fixture
def solved_attributes():
    """Fixture for solved attributes of a 'LINE'."""
    return LineSolvedAttributes(
        p1=50.0,
        q1=30.0,
        i1=70.0,
        p2=50.0,
        q2=30.0,
        i2=70.0,
    )


# Test class
class TestLineMetadata:
    def test_valid_static_state(self, static_attributes):
        """Test valid STATIC state with only static metadata."""
        metadata = LineMetadata(state=State.STATIC, static=static_attributes)
        assert metadata.state == State.STATIC
        assert metadata.static == static_attributes
        assert metadata.solved is None

    def test_valid_solved_state(self, static_attributes, solved_attributes):
        """Test valid SOLVED state with static and solved metadata."""
        metadata = LineMetadata(
            state=State.SOLVED, static=static_attributes, solved=solved_attributes
        )
        assert metadata.state == State.SOLVED
        assert metadata.static == static_attributes
        assert metadata.solved == solved_attributes

    def test_invalid_dynamic_state(self, static_attributes):
        """Test invalid DYNAMIC state raises an error."""
        with pytest.raises(ValueError, match="State can't be State.DYNAMIC."):
            LineMetadata(state=State.DYNAMIC, static=static_attributes)

    def test_invalid_static_state_with_solved(
        self, static_attributes, solved_attributes
    ):
        """Test invalid STATIC state with solved metadata raises an error."""
        with pytest.raises(
            ValueError, match="State is not consistent with data provided."
        ):
            LineMetadata(
                state=State.STATIC,
                static=static_attributes,
                solved=solved_attributes,
            )

    @pytest.mark.parametrize(
        "state, solved, error_message",
        [
            (State.DYNAMIC, None, f"State can't be {State.DYNAMIC}."),
            (
                State.STATIC,
                LineSolvedAttributes(
                    p1=50.0, q1=30.0, i1=70.0, p2=50.0, q2=30.0, i2=70.0
                ),
                "State is not consistent with data provided.",
            ),
        ],
    )
    def test_invalid_states(self, static_attributes, state, solved, error_message):
        """Parameterized test for invalid states."""
        with pytest.raises(ValueError, match=error_message):
            LineMetadata(state=state, static=static_attributes, solved=solved)
