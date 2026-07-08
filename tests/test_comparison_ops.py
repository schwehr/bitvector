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


@pytest.mark.parametrize(
    ("bv_val", "other", "op", "expected"),
    [
        (51, 51, "==", True),
        (51, 52, "==", False),
        (51, 51, "!=", False),
        (51, 52, "!=", True),
        (51, 52, "<", True),
        (51, 51, "<=", True),
        (51, 50, ">", True),
        (51, 51, ">=", True),
        # Float comparisons
        (51, 51.0, "==", True),
        (51, 51.5, "==", False),
        (51, 51.0, "!=", False),
        (51, 51.5, "!=", True),
        (51, 52.0, "<", True),
        (51, 51.0, "<=", True),
        (51, 50.0, ">", True),
        (51, 51.0, ">=", True),
    ],
)
def test_comparison_with_numeric_types(
    bv_val: int, other: int | float, op: ComparisonOp, expected: bool
) -> None:
    """Tests comparisons between BitVector and int/float."""
    bv = BitVector.BitVector(intVal=bv_val)
    compare_func = OP_MAP[op]
    assert compare_func(bv, other) is expected


def test_eq_ne_with_unsupported_types() -> None:
    """Tests that == and != work with any type and don't raise TypeError."""
    bv = BitVector.BitVector(intVal=51)
    assert (bv == "hello") is False
    assert (bv != "hello") is True
    assert (bv == [51]) is False
    assert (bv != [51]) is True
    assert (bv == None) is False  # noqa: E711
    assert (bv != None) is True  # noqa: E711


@pytest.mark.parametrize("op", ["<", "<=", ">", ">="])
def test_order_comparisons_with_unsupported_types_raise_type_error(
    op: ComparisonOp,
) -> None:
    """Tests that <, <=, >, and >= raise TypeError for unsupported types."""
    bv = BitVector.BitVector(intVal=51)
    compare_func = OP_MAP[op]
    with pytest.raises(TypeError):
        compare_func(bv, "hello")
    with pytest.raises(TypeError):
        compare_func(bv, [51])
    with pytest.raises(TypeError):
        compare_func(bv, None)
