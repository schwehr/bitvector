"""Tests for rich comparison operators (==, !=, <, <=, >, >=) on BitVector."""

import operator
from typing import Any, Callable, Literal

import pytest

import BitVector

ComparisonOp = Literal["==", "!=", "<", "<=", ">", ">="]

OP_MAP: dict[ComparisonOp, Callable[[Any, Any], bool]] = {
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
}


@pytest.fixture
def bv1() -> BitVector.BitVector:
    """Returns an 8-bit vector constructed from a bitstring (value 51)."""
    return BitVector.BitVector(bitstring="00110011")


@pytest.fixture
def bv2() -> BitVector.BitVector:
    """Returns an 8-bit vector constructed from a bitlist (value 51)."""
    return BitVector.BitVector(bitlist=[0, 0, 1, 1, 0, 0, 1, 1])


@pytest.fixture
def bv3() -> BitVector.BitVector:
    """Returns a 13-bit vector constructed from an integer (value 5678)."""
    return BitVector.BitVector(intVal=5678)


@pytest.mark.parametrize(
    ("left_name", "right_name", "op", "expected"),
    [
        ("bv1", "bv2", "==", True),
        ("bv1", "bv2", "!=", False),
        ("bv1", "bv2", "<", False),
        ("bv1", "bv2", "<=", True),
        ("bv1", "bv2", ">", False),
        ("bv1", "bv2", ">=", True),
        ("bv1", "bv3", "==", False),
        ("bv1", "bv3", "!=", True),
        ("bv1", "bv3", "<", True),
        ("bv1", "bv3", "<=", True),
        ("bv1", "bv3", ">", False),
        ("bv1", "bv3", ">=", False),
        ("bv3", "bv1", "==", False),
        ("bv3", "bv1", "!=", True),
        ("bv3", "bv1", "<", False),
        ("bv3", "bv1", "<=", False),
        ("bv3", "bv1", ">", True),
        ("bv3", "bv1", ">=", True),
    ],
)
def test_comparison_operators(
    request: pytest.FixtureRequest,
    left_name: str,
    right_name: str,
    op: ComparisonOp,
    expected: bool,
) -> None:
    """Tests rich comparison operators across various BitVector instances.

    Args:
        request: The pytest fixture request object used for dynamic fixture lookup.
        left_name: The fixture name of the left-hand operand.
        right_name: The fixture name of the right-hand operand.
        op: The comparison operator string ('==', '!=', '<', '<=', '>', '>=').
        expected: The expected boolean result of the comparison.
    """
    left: BitVector.BitVector = request.getfixturevalue(left_name)
    right: BitVector.BitVector = request.getfixturevalue(right_name)
    compare_func = OP_MAP[op]
    assert compare_func(left, right) is expected
