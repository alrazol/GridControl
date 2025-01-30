import pytest
from src.core.domain.models.elements_metadata.generator import (
    GeneratorStaticAttributes,
    GeneratorDynamicAttributes,
    GeneratorSolvedAttributes,
    GeneratorMetadata,
)
from src.core.domain.enums import State
from src.core.constants import ElementStatus


# Fixtures for metadata attributes
@pytest.fixture
def static_metadata():
    """Fixture for static attributes of a 'GENERATOR'."""
    return GeneratorStaticAttributes(
        status=ElementStatus.ON,
        voltage_level_id="vl_1",
        bus_id="bus_1",
        Pmax=100.0,
        Pmin=10.0,
        is_voltage_regulator=True,
    )


@pytest.fixture
def dynamic_metadata():
    """Fixture for dynamic attributes of a 'GENERATOR'."""
    return GeneratorDynamicAttributes(
        Ptarget=50.0,
        Vtarget=220.0,
        Qtarget=30.0,
        Srated=120.0,
    )


@pytest.fixture
def solved_metadata():
    """Fixture for solved attributes of a 'GENERATOR'."""
    return GeneratorSolvedAttributes(
        p=48.0,
        q=25.0,
        i=12.0,
        connected=True,
    )


# Test class for GeneratorMetadata
class TestGeneratorMetadata:
    def test_valid_static_state(self, static_metadata):
        """Test valid STATIC state with only static metadata."""
        metadata = GeneratorMetadata(state=State.STATIC, static=static_metadata)
        assert metadata.state == State.STATIC
        assert metadata.static == static_metadata
        assert metadata.dynamic is None
        assert metadata.solved is None

    def test_valid_dynamic_state(self, static_metadata, dynamic_metadata):
        """Test valid DYNAMIC state with static and dynamic metadata."""
        metadata = GeneratorMetadata(
            state=State.DYNAMIC, static=static_metadata, dynamic=dynamic_metadata
        )
        assert metadata.state == State.DYNAMIC
        assert metadata.static == static_metadata
        assert metadata.dynamic == dynamic_metadata
        assert metadata.solved is None

    def test_valid_solved_state(
        self, static_metadata, dynamic_metadata, solved_metadata
    ):
        """Test valid SOLVED state with static, dynamic, and solved metadata."""
        metadata = GeneratorMetadata(
            state=State.SOLVED,
            static=static_metadata,
            dynamic=dynamic_metadata,
            solved=solved_metadata,
        )
        assert metadata.state == State.SOLVED
        assert metadata.static == static_metadata
        assert metadata.dynamic == dynamic_metadata
        assert metadata.solved == solved_metadata

    @pytest.mark.parametrize(
        "state, dynamic, solved, error_message",
        [
            (
                State.STATIC,
                GeneratorDynamicAttributes(Ptarget=50.0, Vtarget=220.0),
                None,
                "State is not consistent",
            ),
            (
                State.STATIC,
                None,
                GeneratorSolvedAttributes(p=48.0, q=25.0, connected=True),
                "State is not consistent",
            ),
            (State.DYNAMIC, None, None, "State is not consistent"),
            (
                State.DYNAMIC,
                None,
                GeneratorSolvedAttributes(p=48.0, q=25.0, connected=True),
                "State is not consistent",
            ),
            (
                State.SOLVED,
                None,
                GeneratorSolvedAttributes(p=48.0, q=25.0, connected=True),
                "State is not consistent",
            ),
            (
                State.SOLVED,
                GeneratorDynamicAttributes(Ptarget=50.0, Vtarget=220.0),
                None,
                "State is not consistent",
            ),
        ],
    )
    def test_invalid_states(
        self, static_metadata, state, dynamic, solved, error_message
    ):
        """Test invalid combinations of state, dynamic, and solved metadata."""
        with pytest.raises(ValueError, match=error_message):
            GeneratorMetadata(
                state=state, static=static_metadata, dynamic=dynamic, solved=solved
            )
