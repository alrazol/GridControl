import pytest
from datetime import datetime, timezone
from src.core.domain.models.operational_constraint import OperationalConstraint
from src.core.constants import (
    SupportedNetworkElementTypes,
    DATETIME_FORMAT,
    DEFAULT_TIMEZONE,
)
from src.core.domain.enums import OperationalConstraintType, BranchSide
from src.core.utils import generate_hash, parse_datetime_to_str


class TestOperationalConstraint:
    """Tests for the `OperationalConstraint` class."""

    @pytest.mark.parametrize(
        "element_id, element_uid, timestamp, element_type, side, name, type, value, acceptable_duration, expected_uid, should_raise_error",
        [
            # Valid case: LINE with timestamp
            (
                "line_1",
                generate_hash("line_1_2025-01-01T12:00:00+0000"),
                datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                SupportedNetworkElementTypes.LINE,
                BranchSide.ONE,
                "Max Current Limit",
                OperationalConstraintType.CURRENT,
                100.0,
                60,
                generate_hash(
                    f"{generate_hash("line_1_2025-01-01T12:00:00+0000")}_ONE_CURRENT"
                ),
                False,
            ),
            # Valid case: LINE without timestamp
            (
                "line_2",
                generate_hash("line_2_None"),
                None,
                SupportedNetworkElementTypes.LINE,
                BranchSide.TWO,
                "Voltage Limit",
                OperationalConstraintType.CURRENT,
                220.0,
                30,
                generate_hash(
                    f"{generate_hash("line_2_None")}_TWO_CURRENT"
                ),
                False,
            ),
            # Invalid case: Non-LINE element type
            (
                "gen_1",
                generate_hash("gen_1_2025-01-01T12:00:00+0000"),
                datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                SupportedNetworkElementTypes.GENERATOR,
                BranchSide.ONE,
                "Power Limit",
                OperationalConstraintType.CURRENT,
                500.0,
                120,
                None,
                True,
            ),
        ],
    )
    def test_from_element(
        self,
        element_id,
        element_uid,
        timestamp,
        element_type,
        side,
        name,
        type,
        value,
        acceptable_duration,
        expected_uid,
        should_raise_error,
    ):
        """Parameterized test for creating operational constraints."""
        if should_raise_error:
            with pytest.raises(
                ValueError, match="Only 'LINE' can have operational constraint."
            ):
                OperationalConstraint.from_element(
                    element_id=element_id,
                    timestamp=timestamp,
                    element_type=element_type,
                    side=side,
                    name=name,
                    type=type,
                    value=value,
                    acceptable_duration=acceptable_duration,
                )
        else:
            constraint = OperationalConstraint.from_element(
                element_id=element_id,
                timestamp=timestamp,
                element_type=element_type,
                side=side,
                name=name,
                type=type,
                value=value,
                acceptable_duration=acceptable_duration,
            )

            # Assertions
            assert constraint.uid == expected_uid
            assert constraint.element_uid == element_uid
            assert constraint.side == side
            assert constraint.name == name
            assert constraint.type == type
            assert constraint.value == value
            assert constraint.acceptable_duration == acceptable_duration
