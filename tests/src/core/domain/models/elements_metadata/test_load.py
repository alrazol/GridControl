import pytest
from src.core.domain.models.elements_metadata.load import (
    LoadMetadata,
    LoadStaticAttributes,
    LoadDynamicAttributes,
    LoadSolvedAttributes,
)
from src.core.domain.enums import State


@pytest.fixture
def static_attributes():
    return LoadStaticAttributes(voltage_level_id="vl_1", bus_id="bus_1")


@pytest.fixture
def dynamic_attributes():
    return LoadDynamicAttributes(Pd=100.0, Qd=50.0)


@pytest.fixture
def solved_attributes():
    return LoadSolvedAttributes(p=95.0, q=45.0, i=10.0)


class TestLoadMetadata:
    def test_static_state_valid(self, static_attributes):
        """Test valid STATIC state with only static attributes."""
        metadata = LoadMetadata(state=State.STATIC, static=static_attributes)
        assert metadata.state == State.STATIC

    def test_dynamic_state_valid(self, static_attributes, dynamic_attributes):
        """Test valid DYNAMIC state with static and dynamic attributes."""
        metadata = LoadMetadata(
            state=State.DYNAMIC, static=static_attributes, dynamic=dynamic_attributes
        )
        assert metadata.state == State.DYNAMIC

    def test_solved_state_valid(
        self, static_attributes, dynamic_attributes, solved_attributes
    ):
        """Test valid SOLVED state with static, dynamic, and solved attributes."""
        metadata = LoadMetadata(
            state=State.SOLVED,
            static=static_attributes,
            dynamic=dynamic_attributes,
            solved=solved_attributes,
        )
        assert metadata.state == State.SOLVED


@pytest.mark.parametrize(
    "state, dynamic, solved, expected_error",
    [
        (
            State.STATIC,
            LoadDynamicAttributes(Pd=100.0, Qd=50.0),
            None,
            "State is not consistent with data provided.",
        ),
        (
            State.STATIC,
            None,
            LoadSolvedAttributes(p=95.0, q=45.0),
            "State is not consistent with data provided.",
        ),
        (State.DYNAMIC, None, None, "State is not consistent with data provided."),
        (
            State.DYNAMIC,
            None,
            LoadSolvedAttributes(p=95.0, q=45.0),
            "State is not consistent with data provided.",
        ),
        (State.SOLVED, None, None, "State is not consistent with data provided."),
        (
            State.SOLVED,
            LoadDynamicAttributes(Pd=100.0, Qd=50.0),
            None,
            "State is not consistent with data provided.",
        ),
    ],
)
def test_invalid_states(static_attributes, state, dynamic, solved, expected_error):
    """Test invalid state scenarios."""
    with pytest.raises(ValueError, match=expected_error):
        LoadMetadata(
            state=state,
            static=static_attributes,
            dynamic=dynamic,
            solved=solved,
        )
