"""Tests BitVector constructors and initialization error validation."""

import io
from pathlib import Path
from typing import Any

import pytest

import BitVector


class ZeroHex:
    """Helper class to test intVal == 0 branch with custom indexing."""

    def __eq__(self, other: object) -> bool:
        """Returns False to trigger fallback zero evaluation."""
        return False

    def __index__(self) -> int:
        """Returns 0 when converted to an integer index."""
        return 0


def test_positional_args_error() -> None:
    """Verifies that passing positional arguments raises TypeError."""
    with pytest.raises(TypeError, match="takes 1 positional argument"):
        BitVector.BitVector(123)  # type: ignore[misc,arg-type]  # ty: ignore[too-many-positional-arguments]


def test_invalid_keyword_error() -> None:
    """Verifies passing unexpected keyword arguments raises TypeError."""
    with pytest.raises(TypeError, match="unexpected keyword argument"):
        BitVector.BitVector(invalid_param=123)  # type: ignore[call-arg]  # ty: ignore[unknown-argument]


def test_filename_constructor(tmp_path: Path) -> None:
    """Tests initializing BitVector from a filename and conflicting errors.

    Args:
        tmp_path: Pytest temporary directory path fixture.
    """
    file_path = tmp_path / "test_init.bin"
    file_path.write_bytes(b"A")
    file_str = str(file_path)

    with pytest.raises(ValueError, match="When filename is specified"):
        BitVector.BitVector(filename=file_str, size=8)

    bv = BitVector.BitVector(filename=file_str)
    try:
        assert bv.filename == file_str
        assert bv.more_to_read is True
    finally:
        bv.close_file_object()


def test_fp_constructor() -> None:
    """Tests initializing from an open file object and conflicting errors."""
    fp_err = io.StringIO("1011000101110")
    with pytest.raises(ValueError, match="When fileobject is specified"):
        BitVector.BitVector(fp=fp_err, size=13)

    fp_valid = io.StringIO("1011000101110")
    bv = BitVector.BitVector(fp=fp_valid)
    assert str(bv) == "1011000101110"


@pytest.mark.parametrize(
    ("kwargs", "err_match"),
    [
        ({"intVal": 5, "bitstring": "101"}, "When intVal is specified"),
        (
            {"intVal": 0, "size": 0},
            "The value specified for size must be at least",
        ),
        (
            {"intVal": 0, "size": -1},
            "The value specified for size must be at least",
        ),
        (
            {"intVal": 5, "size": 0},
            "The value specified for size must be at least",
        ),
        (
            {"intVal": 255, "size": 2},
            "The value specified for size must be at least",
        ),
        (
            {"size": 10, "bitlist": [1, 0]},
            r"When size is specified \(without an intVal\)",
        ),
        ({"size": -5}, r"wrong arg\(s\) for constructor"),
        ({"bitstring": "1010", "rawbytes": b"xy"}, "When a bitstring is specified"),
        ({"bitlist": [1, 0], "hexstring": "a"}, "When bits are specified"),
        (
            {"textstring": "hello", "rawbytes": b"a"},
            "When bits are specified through textstring",
        ),
        (
            {"hexstring": "0f", "rawbytes": b"xy"},
            "When bits are specified through hexstring",
        ),
        (
            {"rawbytes": b"xy", "size": -5},
            "When bits are specified through rawbytes",
        ),
        ({}, r"wrong arg\(s\) for constructor"),
    ],
)
def test_constructor_conflicting_args_raises_error(
    kwargs: dict[str, Any], err_match: str
) -> None:
    """Verifies conflicting or invalid constructor arguments raise ValueError.

    Args:
        kwargs: Keyword arguments containing invalid or conflicting inputs.
        err_match: The expected regex error message pattern.
    """
    with pytest.raises(ValueError, match=err_match):
        BitVector.BitVector(**kwargs)


@pytest.mark.parametrize(
    ("kwargs", "expected_str", "expected_size"),
    [
        ({"intVal": 0}, "0", 1),
        ({"intVal": 0, "size": 5}, "00000", 5),
        ({"intVal": 5}, "101", 3),
        ({"intVal": 32}, "100000", 6),
        ({"intVal": 5, "size": 10}, "0000000101", 10),
        ({"size": 10}, "0000000000", 10),
        ({"size": 0}, "", 0),
        ({"bitstring": "00110011"}, "00110011", 8),
        ({"bitstring": ""}, "", 0),
        ({"bitlist": [1, 1, 0, 1]}, "1101", 4),
        ({"bitlist": []}, "", 0),
        ({"textstring": "A\x05"}, "0100000100000101", 16),
        ({"textstring": ""}, "", 0),
        ({"hexstring": "0FaE"}, "0000111110101110", 16),
        ({"hexstring": ""}, "", 0),
        ({"rawbytes": b"\x00\xff"}, "0000000011111111", 16),
        ({"rawbytes": b""}, "", 0),
    ],
)
def test_constructor_valid_kwargs(
    kwargs: dict[str, Any], expected_str: str, expected_size: int
) -> None:
    """Tests initializing BitVector from valid keyword arguments.

    Args:
        kwargs: Constructor keyword argument dictionary.
        expected_str: Expected bitstring representation.
        expected_size: Expected integer bit vector size.
    """
    bv = BitVector.BitVector(**kwargs)
    assert str(bv) == expected_str
    assert bv.size == expected_size


def test_intVal_zero_hex_helper() -> None:
    """Tests intVal zero evaluation using the ZeroHex helper class."""
    bv = BitVector.BitVector(
        intVal=ZeroHex(),  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]
        size=0,
    )
    assert bv.size == 0
    assert str(bv) == ""

    bv2 = BitVector.BitVector(
        intVal=ZeroHex(),  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]
        size=5,
    )
    assert bv2.size == 5
    assert str(bv2) == "00000"
