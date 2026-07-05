"""Tests file and stream I/O methods (read_bits, write_to_file, close)."""

import io
from pathlib import Path

import pytest

import BitVector


def test_read_bits_from_file_no_filename_raises_error() -> None:
    """Verifies read_bits_from_file without a filename raises SyntaxError."""
    bv = BitVector.BitVector(size=8)
    with pytest.raises(SyntaxError, match="You need to first construct a BitVector"):
        bv.read_bits_from_file(8)


def test_read_bits_from_file_invalid_blocksize_raises_error(
    tmp_path: Path,
) -> None:
    """Verifies reading a block size not a multiple of 8 raises ValueError.

    Args:
        tmp_path: Pytest temporary directory path fixture.
    """
    file_path = tmp_path / "test_stream.bin"
    file_path.write_bytes(b"AB")
    bv = BitVector.BitVector(filename=str(file_path))
    try:
        with pytest.raises(ValueError, match="block size must be a multiple of 8"):
            bv.read_bits_from_file(10)
    finally:
        bv.close_file_object()


def test_read_bits_from_file_sequential(tmp_path: Path) -> None:
    """Tests sequentially reading 8-bit blocks and reaching EOF.

    Args:
        tmp_path: Pytest temporary directory path fixture.
    """
    file_path = tmp_path / "test_stream.bin"
    file_path.write_bytes(b"AB")
    bv = BitVector.BitVector(filename=str(file_path))
    try:
        bv1 = bv.read_bits_from_file(8)
        assert str(bv1) == "01000001"
        assert bv.more_to_read is True

        bv2 = bv.read_bits_from_file(8)
        assert str(bv2) == "01000010"
        assert bv.more_to_read is False

        bv3 = bv.read_bits_from_file(8)
        assert bv3.size == 0
        assert str(bv3) == ""
    finally:
        bv.close_file_object()


def test_read_bits_from_file_partial(tmp_path: Path) -> None:
    """Tests reading more bits than available in the file (EOF mid-block).

    Args:
        tmp_path: Pytest temporary directory path fixture.
    """
    file_path = tmp_path / "test_partial.bin"
    file_path.write_bytes(b"A")
    bv = BitVector.BitVector(filename=str(file_path))
    try:
        bv_read = bv.read_bits_from_file(16)
        assert str(bv_read) == "01000001"
        assert bv.more_to_read is False
    finally:
        bv.close_file_object()


def test_read_bits_from_fileobject() -> None:
    """Tests reading individual bit characters from a text stream object."""
    fp = io.StringIO("11010011")
    bv = BitVector.BitVector(size=0)
    bitlist = bv.read_bits_from_fileobject(fp)
    assert bitlist == ["1", "1", "0", "1", "0", "0", "1", "1"]


def test_write_bits_to_stream_object() -> None:
    """Tests writing ASCII bit characters to a text stream object."""
    bv = BitVector.BitVector(bitstring="101100101")
    fp = io.StringIO()
    bv.write_bits_to_stream_object(fp)
    assert fp.getvalue() == "101100101"


def test_write_to_file_raises_error() -> None:
    """Verifies writing a vector not a multiple of 8 bits raises ValueError."""
    bv = BitVector.BitVector(bitstring="10101")
    with pytest.raises(
        ValueError, match="Only a bit vector whose length is a multiple of 8"
    ):
        bv.write_to_file(io.BytesIO())


def test_write_to_file() -> None:
    """Tests writing packed bytes to a binary stream and appending."""
    bv = BitVector.BitVector(bitstring="0100000101000010")  # 'AB'
    out_stream = io.BytesIO()
    bv.write_to_file(out_stream)
    assert out_stream.getvalue() == b"AB"

    bv.write_to_file(out_stream)
    assert out_stream.getvalue() == b"ABAB"


def test_close_file_object_raises_error() -> None:
    """Verifies closing when no file is open raises SyntaxError."""
    bv = BitVector.BitVector(size=8)
    with pytest.raises(SyntaxError, match="No associated open file"):
        bv.close_file_object()


def test_close_file_object(tmp_path: Path) -> None:
    """Tests closing an associated open input file handle.

    Args:
        tmp_path: Pytest temporary directory path fixture.
    """
    file_path = tmp_path / "test_close.bin"
    file_path.write_bytes(b"test")
    bv = BitVector.BitVector(filename=str(file_path))
    assert bv.FILEIN is not None
    assert bv.FILEIN.closed is False
    bv.close_file_object()
    assert bv.FILEIN.closed is True
