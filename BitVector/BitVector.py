# SPDX-License-Identifier: PSF-2.0
# Copyright (c) 2021 Avinash Kak

"""A memory-efficient packed representation of bit arrays."""

from __future__ import annotations

__version__ = "3.5.0"

import array
import binascii
import copy
import operator
import random
from typing import Any, BinaryIO, Self, Sequence

_hexdict = {
    "0": "0000",
    "1": "0001",
    "2": "0010",
    "3": "0011",
    "4": "0100",
    "5": "0101",
    "6": "0110",
    "7": "0111",
    "8": "1000",
    "9": "1001",
    "a": "1010",
    "b": "1011",
    "c": "1100",
    "d": "1101",
    "e": "1110",
    "f": "1111",
}


def _readblock(blocksize: int, bitvector: BitVector) -> str:
    """Reads a block of bits from a file stream into a binary bitstring.

    If this function succeeds in reading all blocksize bits, it uses a
    tell-read-seek mechanism to peek ahead and check if any data remains in
    the file. If there is nothing further to read, it sets the more_to_read
    attribute of the bitvector instance to False. This peek mechanism is
    supported on seekable streams such as disk files. A similar feature could
    be implemented for socket streams using recv() with MSG_PEEK.

    Args:
        blocksize: The requested number of bits to read from the stream. Must
            be a multiple of 8.
        bitvector: The target BitVector instance whose FILEIN file stream is
            read and whose more_to_read state is updated.

    Returns:
        A string of binary characters ('0's and '1's) representing the read
        bits, up to blocksize in length.
    """
    assert bitvector.FILEIN is not None

    bitstring = ""
    i = 0
    while i < blocksize / 8:
        i += 1
        byte = bitvector.FILEIN.read(1)
        if byte == b"":
            if len(bitstring) < blocksize:
                bitvector.more_to_read = False
            return bitstring
        hexvalue = "%02x" % byte[0]
        bitstring += _hexdict[hexvalue[0]]
        bitstring += _hexdict[hexvalue[1]]

    file_pos = bitvector.FILEIN.tell()
    # Peek at the next byte; moves file position only if a byte is read.
    next_byte = bitvector.FILEIN.read(1)
    if next_byte:
        # pretend we never read the byte
        bitvector.FILEIN.seek(file_pos)
    else:
        bitvector.more_to_read = False

    return bitstring


class BitVector:
    filename: str | None
    size: int
    FILEIN: BinaryIO | None
    FILEOUT: BinaryIO | None
    more_to_read: bool
    vector: array.array[int] | list[int]

    def __init__(
        self,
        *,
        filename: str | None = None,
        fp: Any = None,
        size: int | None = None,
        intVal: int | None = None,
        bitlist: Any = None,
        bitstring: str | None = None,
        hexstring: str | None = None,
        textstring: str | None = None,
        rawbytes: bytes | None = None,
    ) -> None:
        """Initializes a BitVector instance from one of several possible input sources.

        You must specify exactly one keyword argument to determine the data
        source and size of the bit vector. Providing multiple data source
        arguments will raise a ValueError.

        Args:
            filename: Path to a disk file to open for streaming input.
            fp: An open file-like stream object to read bits from.
            size: The desired number of bits for a zero-initialized vector (or
                used in conjunction with intVal).
            intVal: An integer value to convert into a bit vector.
            bitlist: A sequence or list of integers (0s and 1s) representing bits.
            bitstring: A string of binary characters ('0's and '1's).
            hexstring: A string of hexadecimal characters to convert to bits.
            textstring: An ASCII or text string to convert to character bits.
            rawbytes: A bytes object to unpack into a bit vector.

        Raises:
            ValueError: If no argument is provided, if mutually exclusive
                arguments are specified together, or if input values are invalid.
        """
        self.filename = None
        self.size = 0
        self.FILEIN = None
        self.FILEOUT = None
        if filename is not None:
            if (
                fp is not None
                or size is not None
                or intVal is not None
                or bitlist is not None
                or bitstring is not None
                or hexstring is not None
                or textstring is not None
                or rawbytes is not None
            ):
                raise ValueError(
                    "When filename is specified, you cannot give values "
                    "to any other constructor args"
                )
            self.filename = filename
            self.FILEIN = open(filename, "rb")
            self.more_to_read = True
            return
        elif fp is not None:
            if (
                filename is not None
                or size is not None
                or intVal is not None
                or bitlist is not None
                or bitstring is not None
                or hexstring is not None
                or textstring is not None
                or rawbytes is not None
            ):
                raise ValueError(
                    "When fileobject is specified, you cannot give "
                    "values to any other constructor args"
                )
            bits = self.read_bits_from_fileobject(fp)
            bitlist = list(map(int, bits))
            self.size = len(bitlist)
        elif intVal is not None:
            if (
                filename is not None
                or fp is not None
                or bitlist is not None
                or bitstring is not None
                or hexstring is not None
                or textstring is not None
                or rawbytes is not None
            ):
                raise ValueError(
                    "When intVal is specified, you can only give a "
                    "value to the 'size' constructor arg"
                )
            if intVal == 0:
                bitlist = [0]
                if size is None:
                    self.size = 1
                elif size == 0:
                    raise ValueError(
                        "The value specified for size must be at least "
                        "as large as for the smallest bit vector possible "
                        "for intVal"
                    )
                else:
                    if size < len(bitlist):
                        raise ValueError(
                            "The value specified for size must be at least "
                            "as large as for the smallest bit vector "
                            "possible for intVal"
                        )
                    n = size - len(bitlist)
                    bitlist = [0] * n + bitlist
                    self.size = len(bitlist)
            else:
                hexVal = hex(intVal).lower().rstrip("l")
                hexVal = hexVal[2:]
                if len(hexVal) == 1:
                    hexVal = "0" + hexVal
                bitlist = "".join(map(lambda x: _hexdict[x], hexVal))
                bitlist = list(map(int, bitlist))
                i = 0
                while i < len(bitlist):
                    if bitlist[i] == 1:
                        break
                    i += 1
                del bitlist[0:i]
                if size is None:
                    self.size = len(bitlist)
                elif size == 0:
                    if size < len(bitlist):
                        raise ValueError(
                            "The value specified for size must be at least "
                            "as large as for the smallest bit vector possible "
                            "for intVal"
                        )
                else:
                    if size < len(bitlist):
                        raise ValueError(
                            "The value specified for size must be at least "
                            "as large as for the smallest bit vector possible "
                            "for intVal"
                        )
                    n = size - len(bitlist)
                    bitlist = [0] * n + bitlist
                    self.size = len(bitlist)
        elif size is not None and size >= 0:
            if (
                filename is not None
                or fp is not None
                or intVal is not None
                or bitlist is not None
                or bitstring is not None
                or hexstring is not None
                or textstring is not None
                or rawbytes is not None
            ):
                raise ValueError(
                    "When size is specified (without an intVal), you cannot "
                    "give values to any other constructor args"
                )
            self.size = size
            two_byte_ints_needed = (size + 15) // 16
            self.vector = array.array("H", [0] * two_byte_ints_needed)
            return
        elif bitstring is not None:
            if (
                filename is not None
                or fp is not None
                or size is not None
                or intVal is not None
                or bitlist is not None
                or hexstring is not None
                or textstring is not None
                or rawbytes is not None
            ):
                raise ValueError(
                    "When a bitstring is specified, you cannot give "
                    "values to any other constructor args"
                )
            bitlist = list(map(int, list(bitstring)))
            self.size = len(bitlist)
        elif bitlist is not None:
            if (
                filename is not None
                or fp is not None
                or size is not None
                or intVal is not None
                or bitstring is not None
                or hexstring is not None
                or textstring is not None
                or rawbytes is not None
            ):
                raise ValueError(
                    "When bits are specified, you cannot give values "
                    "to any other constructor args"
                )
            self.size = len(bitlist)
        elif textstring is not None:
            if (
                filename is not None
                or fp is not None
                or size is not None
                or intVal is not None
                or bitlist is not None
                or bitstring is not None
                or hexstring is not None
                or rawbytes is not None
            ):
                raise ValueError(
                    "When bits are specified through textstring, you "
                    "cannot give values to any other constructor args"
                )
            hexlist = "".join(
                map(
                    lambda x: x[2:],
                    map(
                        lambda x: (
                            hex(x)
                            if len(hex(x)[2:]) == 2
                            else hex(x)[:2] + "0" + hex(x)[2:]
                        ),
                        map(ord, list(textstring)),
                    ),
                )
            )
            bitlist = list(
                map(int, list("".join(map(lambda x: _hexdict[x], list(hexlist)))))
            )
            self.size = len(bitlist)
        elif hexstring is not None:
            if (
                filename is not None
                or fp is not None
                or size is not None
                or intVal is not None
                or bitlist is not None
                or bitstring is not None
                or textstring is not None
                or rawbytes is not None
            ):
                raise ValueError(
                    "When bits are specified through hexstring, you "
                    "cannot give values to any other constructor args"
                )
            bitlist = list(
                map(
                    int,
                    list("".join(map(lambda x: _hexdict[x], list(hexstring.lower())))),
                )
            )
            self.size = len(bitlist)
        elif rawbytes is not None:
            if (
                filename is not None
                or fp is not None
                or size is not None
                or intVal is not None
                or bitlist is not None
                or bitstring is not None
                or textstring is not None
                or hexstring is not None
            ):
                raise ValueError(
                    "When bits are specified through rawbytes, you "
                    "cannot give values to any other constructor args"
                )
            # TODO(https://github.com/schwehr/bitvector-modern/issues/23): Resolve hexlist type collision.
            hexlist = binascii.hexlify(rawbytes)  # type: ignore[assignment]
            bitlist = list(
                map(
                    int,
                    list(
                        "".join(
                            map(
                                lambda x: _hexdict[x],
                                list(map(chr, list(hexlist))),  # type: ignore[arg-type]
                            )
                        )
                    ),
                )
            )
            self.size = len(bitlist)
        else:
            raise ValueError("wrong arg(s) for constructor")
        two_byte_ints_needed = (len(bitlist) + 15) // 16
        self.vector = array.array("H", [0] * two_byte_ints_needed)
        list(map(self._setbit, range(len(bitlist)), bitlist))

    def _setbit(self, posn: int | tuple[Any, ...] | Any, val: int | Any) -> None:
        """Sets the bit at the designated position to the specified value.

        Args:
            posn: The target bit index (or a 1-element tuple containing the
                index) to modify. Negative indices count from the end.
            val: The binary integer value (0 or 1) to set at the position.

        Raises:
            ValueError: If val is not 0 or 1, or if posn is out of range.
        """
        if val not in (0, 1):
            raise ValueError("incorrect value for a bit")
        if isinstance(posn, (tuple)):
            posn = posn[0]
        if posn >= self.size or posn < -self.size:
            raise ValueError("index range error")
        if posn < 0:
            posn = self.size + posn
        block_index = posn // 16
        shift = posn & 15
        cv = self.vector[block_index]
        if (cv >> shift) & 1 != val:
            self.vector[block_index] = cv ^ (1 << shift)

    def _getbit(self, pos: int | slice | Any) -> Any:
        """Retrieves the bit or slice of bits from the designated position.

        Args:
            pos: An integer index or slice object specifying the bit position(s)
                to extract.

        Returns:
            An integer (0 or 1) if pos is an integer index, or a new BitVector
            instance containing the sliced bits if pos is a slice object.

        Raises:
            ValueError: If pos is out of valid bounds or if slice indices are
                illegal.
        """
        if not isinstance(pos, slice):
            if pos >= self.size or pos < -self.size:
                raise ValueError("index range error")
            if pos < 0:
                pos = self.size + pos
            return (self.vector[pos // 16] >> (pos & 15)) & 1
        else:
            slicebits = []
            i, j = pos.start, pos.stop
            if i is None and j is None:
                return copy.deepcopy(self)
            if i is None:
                if j >= 0:
                    if j > len(self):
                        raise ValueError("illegal slice index values")
                    for x in range(j):
                        slicebits.append(self[x])
                    return BitVector(bitlist=slicebits)
                else:
                    if abs(j) > len(self):
                        raise ValueError("illegal slice index values")
                    for x in range(len(self) - abs(j)):
                        slicebits.append(self[x])
                    return BitVector(bitlist=slicebits)
            if j is None:
                if i >= 0:
                    if i > len(self):
                        raise ValueError("illegal slice index values")
                    for x in range(i, len(self)):
                        slicebits.append(self[x])
                    return BitVector(bitlist=slicebits)
                else:
                    if abs(i) > len(self):
                        raise ValueError("illegal slice index values")
                    for x in range(len(self) - abs(i), len(self)):
                        slicebits.append(self[x])
                    return BitVector(bitlist=slicebits)
            if (i >= 0 and j >= 0) and i > j:
                raise ValueError("illegal slice index values")
            if (i < 0 and j >= 0) and (len(self) - abs(i)) > j:
                raise ValueError("illegal slice index values")
            if i >= 0 and j < 0:
                if len(self) - abs(j) < i:
                    raise ValueError("illegal slice index values")
                else:
                    for x in range(i, len(self) - abs(j)):
                        slicebits.append(self[x])
                    return BitVector(bitlist=slicebits)
            if self.size == 0:
                return BitVector(bitstring="")
            if i == j:
                return BitVector(bitstring="")
            for x in range(i, j):
                slicebits.append(self[x])
            return BitVector(bitlist=slicebits)

    def __xor__(self, other: BitVector) -> BitVector:
        """Performs a bitwise exclusive OR (XOR) with another bit vector.

        If the two bit vectors are not of equal length, the shorter vector is
        automatically padded with zero bits from the left before performing
        the XOR operation.

        Args:
            other: The second BitVector operand.

        Returns:
            A new BitVector instance containing the bitwise XOR result.
        """
        if self.size < other.size:
            bv1 = self._resize_pad_from_left(other.size - self.size)
            bv2 = other
        elif self.size > other.size:
            bv1 = self
            bv2 = other._resize_pad_from_left(self.size - other.size)
        else:
            bv1 = self
            bv2 = other
        res = BitVector(size=bv1.size)
        lpb = map(operator.__xor__, bv1.vector, bv2.vector)
        res.vector = array.array("H", lpb)
        return res

    def __and__(self, other: BitVector) -> BitVector:
        """Performs a bitwise AND with another bit vector.

        If the two bit vectors are not of equal length, the shorter vector is
        automatically padded with zero bits from the left before performing
        the AND operation.

        Args:
            other: The second BitVector operand.

        Returns:
            A new BitVector instance containing the bitwise AND result.
        """
        if self.size < other.size:
            bv1 = self._resize_pad_from_left(other.size - self.size)
            bv2 = other
        elif self.size > other.size:
            bv1 = self
            bv2 = other._resize_pad_from_left(self.size - other.size)
        else:
            bv1 = self
            bv2 = other
        res = BitVector(size=bv1.size)
        lpb = map(operator.__and__, bv1.vector, bv2.vector)
        res.vector = array.array("H", lpb)
        return res

    def __or__(self, other: BitVector) -> BitVector:
        """Performs a bitwise inclusive OR with another bit vector.

        If the two bit vectors are not of equal length, the shorter vector is
        automatically padded with zero bits from the left before performing
        the OR operation.

        Args:
            other: The second BitVector operand.

        Returns:
            A new BitVector instance containing the bitwise OR result.
        """
        if self.size < other.size:
            bv1 = self._resize_pad_from_left(other.size - self.size)
            bv2 = other
        elif self.size > other.size:
            bv1 = self
            bv2 = other._resize_pad_from_left(self.size - other.size)
        else:
            bv1 = self
            bv2 = other
        res = BitVector(size=bv1.size)
        lpb = map(operator.__or__, bv1.vector, bv2.vector)
        res.vector = array.array("H", lpb)
        return res

    def __invert__(self) -> BitVector:
        """Inverts all bits in the bit vector (bitwise NOT).

        Returns:
            A new BitVector instance where each 0 bit is replaced by 1 and
            each 1 bit is replaced by 0.
        """
        res = BitVector(size=self.size)
        lpb = list(map(operator.__inv__, self.vector))
        res.vector = array.array("H")
        for i in range(len(lpb)):
            res.vector.append(lpb[i] & 0x0000FFFF)
        return res

    def __add__(self, other: BitVector) -> BitVector:
        """Concatenates this bit vector with another bit vector.

        Creates a new bit vector containing all bits from this vector followed
        by all bits from the other vector.

        Args:
            other: The BitVector instance to append to the end of this vector.

        Returns:
            A new BitVector instance representing the concatenated bit string.
        """
        new_bv = BitVector(size=0)
        if isinstance(self.vector, array.array) and isinstance(
            new_bv.vector, array.array
        ):
            new_bv.vector.frombytes(self.vector.tobytes())
        elif isinstance(self.vector, list):
            new_bv.vector = self.vector.copy()
        else:
            out_str = str(self) + str(other)
            return BitVector(bitstring=out_str)
        new_bv.size = self.size
        new_bv += other
        return new_bv

    def __iadd__(self, other: BitVector) -> Self:
        """Appends another bit vector to this vector in-place.

        Extends the current bit vector's storage array by appending all bits
        from the argument vector without allocating a new BitVector object.

        Args:
            other: The BitVector instance to append to this vector.

        Returns:
            This BitVector instance (self) after in-place modification.

        Raises:
            TypeError: If the operand is not a BitVector instance.
        """
        if not isinstance(other, type(self)):
            raise TypeError(f"Can only join two BitVector objects, not {type(other)}")
        # Calculate number of two-byte ints we will need to add and extend the vector.
        two_byte_ints_to_add = (self.size + other.size + 15) // 16 - len(self.vector)
        self.vector.extend([0] * two_byte_ints_to_add)
        # Add the bits
        curr_bit = self.size % 16
        curr_two_byte_int = self.size // 16
        for bit in other:
            self.vector[curr_two_byte_int] = self.vector[curr_two_byte_int] | (
                bit << curr_bit
            )
            curr_bit += 1
            curr_two_byte_int += curr_bit // 16
            curr_bit %= 16

        self.size += other.size
        return self

    def _getsize(self) -> int:
        """Returns the number of bits stored in the bit vector.

        Returns:
            The integer number of valid bits in the vector.
        """
        return self.size

    def read_bits_from_file(self, blocksize: int) -> BitVector:
        """Reads a block of bits from the associated disk file.

        The BitVector instance must have been initialized with a filename. Reads up
        to blocksize bits from the file, updating the more_to_read attribute to
        False when the end of file is reached.

        Args:
            blocksize: The number of bits to read. Must be a multiple of 8.

        Returns:
            A new BitVector instance containing the bits read from the file.

        Raises:
            SyntaxError: If the instance was not initialized with a filename.
            ValueError: If blocksize is not a multiple of 8.
        """
        error_str = (
            "You need to first construct a BitVector "
            "object with a filename as  argument"
        )
        if not self.filename:
            raise SyntaxError(error_str)
        if blocksize % 8 != 0:
            raise ValueError("block size must be a multiple of 8")
        bitstr = _readblock(blocksize, self)
        if len(bitstr) == 0:
            return BitVector(size=0)
        else:
            return BitVector(bitstring=bitstr)

    def read_bits_from_fileobject(self, fp: Any) -> Any:
        """Reads characters sequentially from a text or stream file object.

        Args:
            fp: An open stream or file-like object supporting read().

        Returns:
            A list of character strings read from the stream object.
        """
        bitlist: list[str] = []
        while 1:
            bit = fp.read()
            if bit == "":
                return bitlist
            bitlist += bit

    def write_bits_to_stream_object(self, fp: Any) -> None:
        """Writes ASCII '0' and '1' characters representing vector bits to a stream.

        Unlike write_to_file, which writes packed binary bytes, this method
        outputs the text characters '0' and '1', making it suitable for text
        streams like io.StringIO.

        Args:
            fp: An open text stream or file-like object supporting write().
        """
        for bit_index in range(self.size):
            if self[bit_index] == 0:
                fp.write("0")
            else:
                fp.write("1")

    def divide_into_two(self) -> list[BitVector]:
        """Splits an even-length bit vector into two equal halves.

        Returns:
            A list of two new BitVector instances: [left_half, right_half].

        Raises:
            ValueError: If the vector length is not even.
        """
        if self.size % 2 != 0:
            raise ValueError("must have even num bits")
        i = 0
        outlist1 = []
        while i < self.size / 2:
            outlist1.append(self[i])
            i += 1
        outlist2 = []
        while i < self.size:
            outlist2.append(self[i])
            i += 1
        return [BitVector(bitlist=outlist1), BitVector(bitlist=outlist2)]

    def permute(self, permute_list: Sequence[int] | Any) -> BitVector:
        """Permutes the bits of the vector according to a permutation list.

        Args:
            permute_list: A sequence of integer indices specifying the new bit
                ordering.

        Returns:
            A new BitVector instance containing the permuted bits.

        Raises:
            ValueError: If any index in permute_list exceeds vector bounds.
        """
        if max(permute_list) > self.size - 1:
            raise ValueError("Bad permutation index")
        outlist = []
        i = 0
        while i < len(permute_list):
            outlist.append(self[permute_list[i]])
            i += 1
        return BitVector(bitlist=outlist)

    def unpermute(self, permute_list: Sequence[int] | Any) -> BitVector:
        """Restores the original bit ordering of a previously permuted vector.

        Args:
            permute_list: The sequence of integer indices that was originally
                used to permute the bit vector.

        Returns:
            A new BitVector instance with bits restored to their unpermuted order.

        Raises:
            ValueError: If indices are out of bounds or list size does not match.
        """
        if max(permute_list) > self.size - 1:
            raise ValueError("Bad permutation index")
        if self.size != len(permute_list):
            raise ValueError("Bad size for permute list")
        out_bv = BitVector(size=self.size)
        i = 0
        while i < len(permute_list):
            out_bv[permute_list[i]] = self[i]
            i += 1
        return out_bv

    def write_to_file(self, file_out: BinaryIO | Any) -> None:
        """Writes the packed binary byte representation of the vector to a file.

        The vector length must be an integral multiple of 8 bits. When opening
        files for writing on Windows, ensure binary mode ('wb') is used to avoid
        automatic newline translations.

        Args:
            file_out: An open binary file or stream object supporting write().

        Raises:
            ValueError: If the vector length is not a multiple of 8.
        """
        err_str = (
            "Only a bit vector whose length is a multiple of 8 can "
            "be written to a file. Use the padding functions to satisfy "
            "this constraint."
        )
        if not self.FILEOUT:
            self.FILEOUT = file_out
        if self.size % 8:
            raise ValueError(err_str)
        for byte in range(int(self.size / 8)):
            value = 0
            for bit in range(8):
                value += self._getbit(byte * 8 + (7 - bit)) << bit
            file_out.write(bytes([value]))

    def close_file_object(self) -> None:
        """Closes the input file stream associated with this BitVector.

        Raises:
            SyntaxError: If no input file object is currently associated.
        """
        if not self.FILEIN:
            raise SyntaxError("No associated open file")
        self.FILEIN.close()

    def int_val(self) -> int:
        """Calculates and returns the unsigned integer value of the bit vector.

        Returns:
            The integer represented by the binary bits in big-endian order.
        """
        intVal = 0
        for i in range(self.size):
            intVal += self[i] * (2 ** (self.size - i - 1))
        return intVal

    def get_bitvector_in_ascii(self) -> str:
        """Converts the bit vector into an ASCII character string.

        Every 8 bits in the vector are converted into their corresponding ASCII
        character. The vector size must be a multiple of 8.

        Returns:
            An ASCII string decoded from the 8-bit blocks of the vector.

        Raises:
            ValueError: If the vector size is not an integral multiple of 8.
        """
        if self.size % 8:
            raise ValueError(
                "The bitvector for get_bitvector_in_ascii() "
                "must be an integral multiple of 8 bits"
            )
        return "".join(
            map(chr, map(int, [self[i : i + 8] for i in range(0, self.size, 8)]))
        )

    def get_bitvector_in_hex(self) -> str:
        """Converts the bit vector into a hexadecimal representation string.

        Every 4 bits are converted into their corresponding hex digit (0-9, a-f).
        The vector size must be a multiple of 4.

        Returns:
            A lowercase hexadecimal string representing the vector bits.

        Raises:
            ValueError: If the vector size is not an integral multiple of 4.
        """
        if self.size % 4:
            raise ValueError(
                "The bitvector for get_bitvector_in_hex() "
                "must be an integral multiple of 4 bits"
            )
        return "".join(
            map(
                lambda x: x.replace("0x", ""),
                map(hex, map(int, [self[i : i + 4] for i in range(0, self.size, 4)])),
            )
        )

    def __lshift__(self, n: int) -> Self:
        """Performs an in-place circular left rotation by n bit positions.

        Rotates the bit vector circularly to the left n times. Negative values
        for n delegate to a circular right rotation. Modifies and returns the
        current instance to support method chaining.

        Args:
            n: The integer number of positions to circularly rotate left.

        Returns:
            This BitVector instance (self) after in-place rotation.

        Raises:
            ValueError: If attempting to rotate an empty bit vector.
        """
        if self.size == 0:
            raise ValueError("Circular shift of an empty vector makes no sense")
        if n < 0:
            return self >> abs(n)
        for i in range(n):
            self.circular_rotate_left_by_one()
        return self

    def __rshift__(self, n: int) -> Self:
        """Performs an in-place circular right rotation by n bit positions.

        Rotates the bit vector circularly to the right n times. Negative values
        for n delegate to a circular left rotation. Modifies and returns the
        current instance to support method chaining.

        Args:
            n: The integer number of positions to circularly rotate right.

        Returns:
            This BitVector instance (self) after in-place rotation.

        Raises:
            ValueError: If attempting to rotate an empty bit vector.
        """
        if self.size == 0:
            raise ValueError("Circular shift of an empty vector makes no sense")
        if n < 0:
            return self << abs(n)
        for i in range(n):
            self.circular_rotate_right_by_one()
        return self

    def circular_rotate_left_by_one(self) -> None:
        """Performs a one-bit in-place circular left rotation of the vector."""
        size = len(self.vector)
        bitstring_leftmost_bit = self.vector[0] & 1
        left_most_bits = list(map(operator.__and__, self.vector, [1] * size))
        left_most_bits.append(left_most_bits[0])
        del left_most_bits[0]
        self.vector = list(map(operator.__rshift__, self.vector, [1] * size))
        self.vector = list(
            map(
                operator.__or__,
                self.vector,
                list(map(operator.__lshift__, left_most_bits, [15] * size)),
            )
        )
        self._setbit(self.size - 1, bitstring_leftmost_bit)

    def circular_rotate_right_by_one(self) -> None:
        """Performs a one-bit in-place circular right rotation of the vector."""
        size = len(self.vector)
        bitstring_rightmost_bit = self[self.size - 1]
        right_most_bits = list(map(operator.__and__, self.vector, [0x8000] * size))
        self.vector = list(map(operator.__and__, self.vector, [~0x8000] * size))
        right_most_bits.insert(0, bitstring_rightmost_bit)
        right_most_bits.pop()
        self.vector = list(map(operator.__lshift__, self.vector, [1] * size))
        self.vector = list(
            map(
                operator.__or__,
                self.vector,
                list(map(operator.__rshift__, right_most_bits, [15] * size)),
            )
        )
        self._setbit(0, bitstring_rightmost_bit)

    def circular_rot_left(self) -> None:
        """Performs a one-bit in-place circular left rotation without map()."""
        max_index = (self.size - 1) // 16
        left_most_bit = self.vector[0] & 1
        self.vector[0] = self.vector[0] >> 1
        for i in range(1, max_index + 1):
            left_bit = self.vector[i] & 1
            self.vector[i] = self.vector[i] >> 1
            self.vector[i - 1] |= left_bit << 15
        self._setbit(self.size - 1, left_most_bit)

    def circular_rot_right(self) -> None:
        """Performs a one-bit in-place circular right rotation without map()."""
        max_index = (self.size - 1) // 16
        right_most_bit = self[self.size - 1]
        self.vector[max_index] &= ~0x8000
        self.vector[max_index] = self.vector[max_index] << 1
        for i in range(max_index - 1, -1, -1):
            right_bit = self.vector[i] & 0x8000
            self.vector[i] &= ~0x8000
            self.vector[i] = self.vector[i] << 1
            self.vector[i + 1] |= right_bit >> 15
        self._setbit(0, right_most_bit)

    def shift_left_by_one(self) -> None:
        """Performs a one-bit in-place logical left shift (zero-filling right)."""
        size = len(self.vector)
        left_most_bits = list(map(operator.__and__, self.vector, [1] * size))
        left_most_bits.append(left_most_bits[0])
        del left_most_bits[0]
        self.vector = list(map(operator.__rshift__, self.vector, [1] * size))
        self.vector = list(
            map(
                operator.__or__,
                self.vector,
                list(map(operator.__lshift__, left_most_bits, [15] * size)),
            )
        )
        self._setbit(self.size - 1, 0)

    def shift_right_by_one(self) -> None:
        """Performs a one-bit in-place logical right shift (zero-filling left)."""
        size = len(self.vector)
        right_most_bits = list(map(operator.__and__, self.vector, [0x8000] * size))
        self.vector = list(map(operator.__and__, self.vector, [~0x8000] * size))
        right_most_bits.insert(0, 0)
        right_most_bits.pop()
        self.vector = list(map(operator.__lshift__, self.vector, [1] * size))
        self.vector = list(
            map(
                operator.__or__,
                self.vector,
                list(map(operator.__rshift__, right_most_bits, [15] * size)),
            )
        )
        self._setbit(0, 0)

    def shift_left(self, n: int) -> Self:
        """Shifts the vector left by n bits in-place, filling right with zeros.

        Args:
            n: The integer number of bit positions to shift left.

        Returns:
            This BitVector instance (self) after in-place shifting.
        """
        for i in range(n):
            self.shift_left_by_one()
        return self

    def shift_right(self, n: int) -> Self:
        """Shifts the vector right by n bits in-place, filling left with zeros.

        Args:
            n: The integer number of bit positions to shift right.

        Returns:
            This BitVector instance (self) after in-place shifting.
        """
        for i in range(n):
            self.shift_right_by_one()
        return self

    # Allow array like subscripting for getting and setting:
    __getitem__ = _getbit

    def __setitem__(self, pos: int | slice | Any, item: int | BitVector | Any) -> Any:
        """Assigns a bit or slice of bits at the specified position.

        Supports both index assignment (setting a single bit to 0 or 1) and
        slice assignment (replacing a slice of bits with another BitVector).

        Args:
            pos: An integer index or slice object indicating where to assign.
            item: An integer (0 or 1) for index assignment, or a BitVector for
                slice assignment.

        Raises:
            TypeError: If the assigned item has an incompatible type.
            ValueError: If slice lengths are incompatible or index is out of range.
        """
        # The following section is for slice assignment:
        if isinstance(pos, slice):
            if not isinstance(item, BitVector):
                raise TypeError(
                    "For slice assignment, the right hand side must be a BitVector"
                )
            if pos.start is None and pos.stop is None:
                return copy.deepcopy(item)
            if pos.start is None:
                if pos.stop >= 0:
                    if pos.stop != len(item):
                        raise ValueError("incompatible lengths for slice assignment 1")
                    for i in range(pos.stop):
                        self[i] = item[i]
                else:
                    if len(self) - abs(pos.stop) != len(item):
                        raise ValueError("incompatible lengths for slice assignment 2")
                    for i in range(len(self) + pos.stop):
                        self[i] = item[i]
                return
            if pos.stop is None:
                if pos.start >= 0:
                    if (len(self) - pos.start) != len(item):
                        raise ValueError("incompatible lengths for slice assignment 3")
                    #                    for i in range(len(item)-1):
                    for i in range(len(item)):
                        self[pos.start + i] = item[i]
                else:
                    if abs(pos.start) != len(item):
                        raise ValueError("incompatible lengths for slice assignment 4")
                    for i in range(len(item)):
                        self[len(self) + pos.start + i] = item[i]
                return
            if pos.start >= 0 and pos.stop < 0:
                if (len(self) + pos.stop - pos.start) != len(item):
                    raise ValueError("incompatible lengths for slice assignment 5")
                for i in range(pos.start, len(self) + pos.stop):
                    self[i] = item[i - pos.start]
                return
            if pos.start < 0 and pos.stop >= 0:
                if (len(self) - pos.stop + pos.start) != len(item):
                    raise ValueError("incompatible lengths for slice assignment 6")
                for i in range(len(self) + pos.start, pos.stop):
                    self[i] = item[i - pos.start]
                return
            if (pos.stop - pos.start) != len(item):
                raise ValueError("incompatible lengths for slice assignment 7")
            for i in range(pos.start, pos.stop):
                self[i] = item[i - pos.start]
            return
        # For index assignment use _setbit()
        self._setbit(pos, item)

    # Allow len() to work:
    __len__ = _getsize
    # Allow int() to work:
    __int__ = int_val

    def __iter__(self) -> BitVectorIterator:
        """Returns an iterator over the individual bits in the vector.

        Returns:
            A BitVectorIterator instance stepping through bits sequentially.
        """
        return BitVectorIterator(self)

    def __str__(self) -> str:
        """Returns an ASCII string representation of the bit vector ('0's and '1's).

        Returns:
            A string of '0' and '1' characters matching the stored bits.
        """
        if self.size == 0:
            return ""
        return "".join(map(str, self))

    def __eq__(self, other: Any) -> bool:
        """Checks equality between this bit vector and another object.

        Args:
            other: The object to compare against.

        Returns:
            True if other is a BitVector of identical size and bit values,
            otherwise False.
        """
        if self.size != other.size:
            return False
        i = 0
        while i < self.size:
            if self[i] != other[i]:
                return False
            i += 1
        return True

    def __ne__(self, other: Any) -> bool:
        """Checks inequality between this bit vector and another object.

        Args:
            other: The object to compare against.

        Returns:
            True if the objects are not equal, otherwise False.
        """
        return not self == other

    def __lt__(self, other: Any) -> bool:
        """Checks if this bit vector is strictly less than another vector.

        Comparison is performed by evaluating integer values.

        Args:
            other: The BitVector instance to compare against.

        Returns:
            True if this vector's integer value is less than other's.
        """
        return self.int_val() < other.int_val()

    def __le__(self, other: Any) -> bool:
        """Checks if this bit vector is less than or equal to another vector.

        Comparison is performed by evaluating integer values.

        Args:
            other: The BitVector instance to compare against.

        Returns:
            True if this vector's integer value is less than or equal to other's.
        """
        return self.int_val() <= other.int_val()

    def __gt__(self, other: Any) -> bool:
        """Checks if this bit vector is strictly greater than another vector.

        Comparison is performed by evaluating integer values.

        Args:
            other: The BitVector instance to compare against.

        Returns:
            True if this vector's integer value is greater than other's.
        """
        return self.int_val() > other.int_val()

    def __ge__(self, other: Any) -> bool:
        """Checks if this bit vector is greater than or equal to another vector.

        Comparison is performed by evaluating integer values.

        Args:
            other: The BitVector instance to compare against.

        Returns:
            True if this vector's integer value is greater than or equal to other's.
        """
        return self.int_val() >= other.int_val()

    def __deepcopy__(self, memo: dict[int, Any] | None = None) -> Self:
        """Creates a deep copy of the bit vector for the copy module.

        Args:
            memo: An optional dictionary tracking copied objects to prevent
                infinite recursion.

        Returns:
            A new BitVector instance identical to this vector.
        """
        if memo is None:
            memo = {}
        new_bv = self.__class__(size=0)
        memo[id(self)] = new_bv
        if isinstance(self.vector, array.array):
            new_bv.vector = array.array("H", self.vector)
        elif isinstance(self.vector, list):
            new_bv.vector = self.vector.copy()
        else:
            new_bv.vector = copy.deepcopy(self.vector, memo)
        new_bv.size = self.size
        return new_bv

    def _resize_pad_from_left(self, n: int) -> BitVector:
        """Resizes the bit vector by padding with n zeros from the left.

        Args:
            n: The integer number of zero bits to prepend to the bit vector.

        Returns:
            A new BitVector instance containing the left-padded bits.
        """
        new_str = "0" * n + str(self)
        return BitVector(bitstring=new_str)

    def pad_from_left(self, n: int) -> None:
        """Pads the bit vector with n zeros from the left in-place.

        Args:
            n: The integer number of zero bits to prepend to the vector.
        """
        new_str = "0" * n + str(self)
        bitlist = list(map(int, list(new_str)))
        self.size = len(bitlist)
        two_byte_ints_needed = (len(bitlist) + 15) // 16
        self.vector = array.array("H", [0] * two_byte_ints_needed)
        list(map(self._setbit, enumerate(bitlist), bitlist))

    def pad_from_right(self, n: int) -> None:
        """Pads the bit vector with n zeros from the right in-place.

        Args:
            n: The integer number of zero bits to append to the vector.
        """
        new_str = str(self) + "0" * n
        bitlist = list(map(int, list(new_str)))
        self.size = len(bitlist)
        two_byte_ints_needed = (len(bitlist) + 15) // 16
        self.vector = array.array("H", [0] * two_byte_ints_needed)
        list(map(self._setbit, enumerate(bitlist), bitlist))

    def __contains__(self, otherBitVec: BitVector) -> bool:
        """Checks if a sub-vector is contained within this bit vector.

        Supports the 'in' and 'not in' operators for subsequence searching.

        Args:
            otherBitVec: The BitVector subsequence to search for.

        Returns:
            True if otherBitVec appears as a contiguous subsequence, else False.

        Raises:
            ValueError: If this vector is empty or shorter than otherBitVec.
        """
        if self.size == 0:
            raise ValueError("First arg bitvec has no bits")
        elif self.size < otherBitVec.size:
            raise ValueError("First arg bitvec too short")
        max_index = self.size - otherBitVec.size + 1
        for i in range(max_index):
            if self[i : i + otherBitVec.size] == otherBitVec:
                return True
        return False

    def reset(self, val: int | Any) -> Self:
        """Resets all bits in the vector to either 0 or 1 in-place.

        Args:
            val: The target bit value (0 or 1) to set across the entire vector.

        Returns:
            This BitVector instance (self) after resetting.

        Raises:
            ValueError: If val is not 0 or 1.
        """
        if val not in (0, 1):
            raise ValueError("Incorrect reset argument")
        bitlist = [val for i in range(self.size)]
        list(map(self._setbit, enumerate(bitlist), bitlist))
        return self

    def count_bits(self) -> int:
        """Counts the total number of set bits (1s) in the bit vector.

        Returns:
            The integer count of bits set to 1.
        """
        return sum(self)

    def set_value(self, *args: Any, **kwargs: Any) -> None:
        """Reinitializes the bit vector in-place with new data.

        Accepts the same keyword arguments as the class constructor to overwrite
        the current vector's size and contents.

        Args:
            *args: Positional arguments passed to constructor.
            **kwargs: Keyword arguments specifying the new data source and size.
        """
        BitVector.__init__(self, *args, **kwargs)

    def count_bits_sparse(self) -> int:
        """Counts set bits using Brian Kernighan's algorithm for sparse vectors.

        Optimized for large bit vectors where very few bits are set to 1.

        Returns:
            The integer count of bits set to 1.
        """
        num = 0
        for intval in self.vector:
            if intval == 0:
                continue
            c = 0
            iv = intval
            while iv > 0:
                iv = iv & (iv - 1)
                c = c + 1
            num = num + c
        return num

    def jaccard_similarity(self, other: BitVector) -> float:
        """Calculates the Jaccard similarity coefficient between two vectors.

        Args:
            other: A BitVector of equal length to compare against.

        Returns:
            A floating-point coefficient between 0.0 and 1.0.

        Raises:
            AssertionError: If vectors are of unequal length or both zero.
        """
        assert self.int_val() > 0 or other.int_val() > 0, (
            "Jaccard called on two zero vectors --- NOT ALLOWED"
        )
        assert self.size == other.size, (
            "bitvectors for comparing with Jaccard must be of equal length"
        )
        intersect = self & other
        union = self | other
        return intersect.count_bits_sparse() / float(union.count_bits_sparse())

    def jaccard_distance(self, other: BitVector) -> float:
        """Calculates the Jaccard distance coefficient between two vectors.

        Args:
            other: A BitVector of equal length to compare against.

        Returns:
            A floating-point distance between 0.0 and 1.0 (1 - similarity).

        Raises:
            AssertionError: If vectors are of unequal length.
        """
        assert self.size == other.size, "vectors of unequal length"
        return 1 - self.jaccard_similarity(other)

    def hamming_distance(self, other: BitVector) -> int:
        """Calculates the Hamming distance between two vectors of equal length.

        Args:
            other: A BitVector of equal length to compare against.

        Returns:
            The integer number of bit positions where the two vectors disagree.

        Raises:
            AssertionError: If vectors are of unequal length.
        """
        assert self.size == other.size, "vectors of unequal length"
        diff = self ^ other
        return diff.count_bits_sparse()

    def next_set_bit(self, from_index: int = 0) -> int:
        """Finds the index of the next set bit starting from from_index.

        Args:
            from_index: The non-negative bit index at which to start searching.

        Returns:
            The integer index of the next set bit (1), or -1 if none is found.

        Raises:
            AssertionError: If from_index is negative.
        """
        assert from_index >= 0, "from_index must be nonnegative"
        i = from_index
        v = self.vector
        vec_len = len(v)
        o = i >> 4
        s = i & 0x0F
        i = o << 4
        while o < vec_len:
            h = v[o]
            if h:
                i += s
                m = 1 << s
                while m != (1 << 0x10):
                    if h & m:
                        return i
                    m <<= 1
                    i += 1
            else:
                i += 0x10
            s = 0
            o += 1
        return -1

    def rank_of_bit_set_at_index(self, position: int) -> int:
        """Calculates the rank (count of set bits up to position) of a set bit.

        Args:
            position: The target bit index, which must currently be set to 1.

        Returns:
            The total number of set bits from index 0 up to position (inclusive).

        Raises:
            AssertionError: If the bit at position is not set to 1.
        """
        assert self[position] == 1, "the arg bit not set"
        bv = self[0 : position + 1]
        return bv.count_bits()

    def is_power_of_2(self) -> bool:
        """Checks whether the integer value of the vector is a power of two.

        Returns:
            True if the integer representation is a power of two, else False.
        """
        if self.int_val() == 0:
            return False
        bv = self & BitVector(intVal=self.int_val() - 1)
        if bv.int_val() == 0:
            return True
        return False

    def is_power_of_2_sparse(self) -> bool:
        """Checks whether the vector is a power of two using sparse bit counting.

        Optimized for large vectors where sparse bit counting is faster.

        Returns:
            True if exactly one bit is set to 1, else False.
        """
        if self.count_bits_sparse() == 1:
            return True
        return False

    def reverse(self) -> BitVector:
        """Reverses the order of bits in the vector (left-to-right becomes right-to-left).

        Returns:
            A new BitVector instance with bits in reversed order.
        """
        reverseList = []
        i = 1
        while i < self.size + 1:
            reverseList.append(self[-i])
            i += 1
        return BitVector(bitlist=reverseList)

    def gcd(self, other: BitVector) -> BitVector:
        """Calculates the greatest common divisor (GCD) using Euclid's algorithm.

        Args:
            other: A BitVector representing the second integer operand.

        Returns:
            A new BitVector instance containing the GCD of the two integer values.
        """
        a = self.int_val()
        b = other.int_val()
        if a < b:
            a, b = b, a
        while b != 0:
            a, b = b, a % b
        return BitVector(intVal=a)

    def multiplicative_inverse(self, modulus: BitVector) -> BitVector | None:
        """Calculates the modular multiplicative inverse using integer arithmetic.

        Uses the Extended Euclidean Algorithm. For field inverses in GF(2^n),
        use gf_MI instead.

        Args:
            modulus: A BitVector representing the integer modulus.

        Returns:
            A new BitVector with the multiplicative inverse modulo modulus,
            or None if no inverse exists.
        """
        MOD = mod = modulus.int_val()
        num = self.int_val()
        x, x_old = 0, 1
        y, y_old = 1, 0
        while mod:
            quotient = num // mod
            num, mod = mod, num % mod
            x, x_old = x_old - x * quotient, x
            y, y_old = y_old - y * quotient, y
        if num != 1:
            return None
        else:
            MI = (x_old + MOD) % MOD
            return BitVector(intVal=MI)

    def length(self) -> int:
        """Returns the number of bits stored in the vector.

        Returns:
            The integer count of valid bits.
        """
        return self.size

    def gf_multiply(self, b: BitVector) -> BitVector:
        """Multiplies two polynomials in Galois Field GF(2).

        Args:
            b: The second polynomial BitVector operand.

        Returns:
            A new BitVector containing the GF(2) product of the two polynomials.
        """
        a = copy.deepcopy(self)
        b_copy = copy.deepcopy(b)
        result = BitVector(size=a.length() + b_copy.length())
        a.pad_from_left(result.length() - a.length())
        b_copy.pad_from_left(result.length() - b_copy.length())
        for i, bit in enumerate(b_copy):
            if bit == 1:
                power = b_copy.length() - i - 1
                a_copy = copy.deepcopy(a)
                a_copy.shift_left(power)
                result ^= a_copy
        return result

    def gf_divide_by_modulus(
        self, mod: BitVector, n: int
    ) -> tuple[BitVector, BitVector]:
        """Divides this polynomial by a modulus polynomial in GF(2^n).

        Args:
            mod: A BitVector representing the modulus polynomial.
            n: The integer degree n of the Galois Field GF(2^n).

        Returns:
            A tuple of two BitVectors: (quotient, remainder).

        Raises:
            ValueError: If the modulus polynomial is too long for GF(2^n).
        """
        num = self
        if mod.length() > n + 1:
            raise ValueError("Modulus bit pattern too long")
        quotient = BitVector(intVal=0, size=num.length())
        remainder = copy.deepcopy(num)
        i = 0
        while 1:
            i = i + 1
            if i == num.length():
                break
            mod_highest_power = mod.length() - mod.next_set_bit(0) - 1
            if remainder.next_set_bit(0) == -1:
                remainder_highest_power = 0
            else:
                remainder_highest_power = (
                    remainder.length() - remainder.next_set_bit(0) - 1
                )
            if (remainder_highest_power < mod_highest_power) or int(remainder) == 0:
                break
            else:
                exponent_shift = remainder_highest_power - mod_highest_power
                quotient[quotient.length() - exponent_shift - 1] = 1
                quotient_mod_product = copy.deepcopy(mod)
                quotient_mod_product.pad_from_left(remainder.length() - mod.length())
                quotient_mod_product.shift_left(exponent_shift)
                remainder = remainder ^ quotient_mod_product
        if remainder.length() > n:
            remainder = remainder[remainder.length() - n :]
        return quotient, remainder

    def gf_multiply_modular(
        self, b: BitVector | Any, mod: BitVector, n: int
    ) -> BitVector:
        """Performs modular polynomial multiplication in Galois Field GF(2^n).

        Args:
            b: The second polynomial operand BitVector.
            mod: The modulus polynomial BitVector.
            n: The integer degree n of the Galois Field GF(2^n).

        Returns:
            A new BitVector containing the product modulo mod in GF(2^n).
        """
        a = self
        a_copy = copy.deepcopy(a)
        b_copy = copy.deepcopy(b)
        product = a_copy.gf_multiply(b_copy)
        quotient, remainder = product.gf_divide_by_modulus(mod, n)
        return remainder

    def gf_MI(self, mod: BitVector, n: int) -> BitVector | tuple[str, ...]:
        """Calculates the multiplicative inverse in Galois Field GF(2^n).

        Args:
            mod: The modulus polynomial BitVector.
            n: The integer degree n of the Galois Field GF(2^n).

        Returns:
            A new BitVector with the multiplicative inverse in GF(2^n), or a
            tuple of descriptive strings if no inverse exists.
        """
        num = self
        NUM = copy.deepcopy(num)
        MOD = copy.deepcopy(mod)
        x = BitVector(size=mod.length())
        x_old = BitVector(intVal=1, size=mod.length())
        y = BitVector(intVal=1, size=mod.length())
        y_old = BitVector(size=mod.length())
        while int(mod):
            quotient, remainder = num.gf_divide_by_modulus(mod, n)
            num, mod = mod, remainder
            x, x_old = x_old ^ quotient.gf_multiply(x), x
            y, y_old = y_old ^ quotient.gf_multiply(y), y
        if int(num) != 1:
            return (
                "NO MI. However, the GCD of ",
                str(NUM),
                " and ",
                str(MOD),
                " is ",
                str(num),
            )
        else:
            z = x_old ^ MOD
            quotient, remainder = z.gf_divide_by_modulus(MOD, n)
            return remainder

    def runs(self) -> list[str]:
        """Extracts contiguous runs of identical bits ('0's and '1's).

        Returns:
            A list of binary strings, each representing a contiguous run of 0s
            or 1s.
        """
        allruns: list[str] = []
        if self.size == 0:
            return allruns
        run = ""
        previous_bit = self[0]
        if previous_bit == 0:
            run = "0"
        else:
            run = "1"
        for bit in list(self)[1:]:
            if bit == 0 and previous_bit == 0:
                run += "0"
            elif bit == 1 and previous_bit == 0:
                allruns.append(run)
                run = "1"
            elif bit == 0 and previous_bit == 1:
                allruns.append(run)
                run = "0"
            else:
                run += "1"
            previous_bit = bit
        allruns.append(run)
        return allruns

    def test_for_primality(self) -> float:
        """Tests the integer value for primality using Miller-Rabin probabilistic test.

        Returns:
            A float probability close to 1.0 for prime numbers, or 0.0 for
            composites.
        """
        p = int(self)
        if p == 1:
            return 0
        probes = [2, 3, 5, 7, 11, 13, 17]
        for a in probes:
            if a == p:
                return 1
        if any([p % a == 0 for a in probes]):
            return 0
        k, q = 0, p - 1
        while not q & 1:
            q >>= 1
            k += 1
        for a in probes:
            a_raised_to_q = pow(a, q, p)
            if a_raised_to_q == 1 or a_raised_to_q == p - 1:
                continue
            a_raised_to_jq = a_raised_to_q
            primeflag = 0
            for j in range(k - 1):
                a_raised_to_jq = pow(a_raised_to_jq, 2, p)
                if a_raised_to_jq == p - 1:
                    primeflag = 1
                    break
            if not primeflag:
                return 0
        probability_of_prime = 1 - 1.0 / (4 ** len(probes))
        return probability_of_prime

    def gen_random_bits(self, width: int) -> BitVector:
        """Generates a random odd integer bit vector of specified bit width.

        Ensures the number spans the full width by setting the two most
        significant bits and the least significant bit to 1.

        Args:
            width: The desired integer bit width of the random vector.

        Returns:
            A new BitVector instance containing the generated random bits.
        """
        candidate = random.getrandbits(width)
        candidate |= 1
        candidate |= 1 << width - 1
        candidate |= 2 << width - 3
        return BitVector(intVal=candidate)

    def min_canonical(self) -> BitVector:
        """Finds the minimum canonical circular rotation of the bit vector.

        Evaluates all circular shifts and selects the rotation with the minimum
        integer value (maximum leading zeros).

        Returns:
            A new BitVector instance representing the minimum canonical rotation.
        """
        intvals_for_circular_shifts = [int(self << 1) for _ in range(len(self))]
        return BitVector(intVal=min(intvals_for_circular_shifts), size=len(self))


class BitVectorIterator:
    items: list[int]
    index: int

    def __init__(self, bitvec: BitVector) -> None:
        """Initializes the iterator with a copy of the target vector's bits.

        Args:
            bitvec: The BitVector instance to iterate over.
        """
        self.items = []
        for i in range(bitvec.size):
            self.items.append(bitvec._getbit(i))
        self.index = -1

    def __iter__(self) -> Self:
        """Returns the iterator object itself.

        Returns:
            This BitVectorIterator instance (self).
        """
        return self

    def next(self) -> int:
        """Retrieves the next bit in the iteration sequence.

        Returns:
            The integer bit value (0 or 1) at the next position.

        Raises:
            StopIteration: When there are no remaining bits to iterate over.
        """
        self.index += 1
        if self.index < len(self.items):
            return self.items[self.index]
        else:
            raise StopIteration

    __next__ = next
