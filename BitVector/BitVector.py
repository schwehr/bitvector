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
                    """When filename is specified, you cannot give values """
                    """to any other constructor args"""
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
                    """When fileobject is specified, you cannot give """
                    """values to any other constructor args"""
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
                    """When intVal is specified, you can only give a """
                    """value to the 'size' constructor arg"""
                )
            if intVal == 0:
                bitlist = [0]
                if size is None:
                    self.size = 1
                elif size == 0:
                    raise ValueError(
                        """The value specified for size must be at least """
                        """as large as for the smallest bit vector possible """
                        """for intVal"""
                    )
                else:
                    if size < len(bitlist):
                        raise ValueError(
                            """The value specified for size must be at least """
                            """as large as for the smallest bit vector """
                            """possible for intVal"""
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
                            """The value specified for size must be at least """
                            """as large as for the smallest bit vector possible """
                            """for intVal"""
                        )
                else:
                    if size < len(bitlist):
                        raise ValueError(
                            """The value specified for size must be at least """
                            """as large as for the smallest bit vector possible """
                            """for intVal"""
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
                    """When size is specified (without an intVal), you cannot """
                    """give values to any other constructor args"""
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
                    """When a bitstring is specified, you cannot give """
                    """values to any other constructor args"""
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
                    """When bits are specified, you cannot give values """
                    """to any other constructor args"""
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
                    """When bits are specified through textstring, you """
                    """cannot give values to any other constructor args"""
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
                    """When bits are specified through hexstring, you """
                    """cannot give values to any other constructor args"""
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
                    """When bits are specified through rawbytes, you """
                    """cannot give values to any other constructor args"""
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
        "Set the bit at the designated position to the value shown"
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
        "Get the bit from the designated position"
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
        """
        Take a bitwise 'XOR' of the bit vector on which the method is invoked with
        the argument bit vector.  Return the result as a new bit vector.  If the two
        bit vectors are not of the same size, pad the shorter one with zeros from the
        left.
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
        """
        Take a bitwise 'AND' of the bit vector on which the method is invoked with
        the argument bit vector.  Return the result as a new bit vector.  If the two
        bit vectors are not of the same size, pad the shorter one with zeros from the
        left.
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
        """
        Take a bitwise 'OR' of the bit vector on which the method is invoked with the
        argument bit vector.  Return the result as a new bit vector.  If the two bit
        vectors are not of the same size, pad the shorter one with zero's from the
        left.
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
        """
        Invert the bits in the bit vector on which the method is invoked
        and return the result as a new bit vector.
        """
        res = BitVector(size=self.size)
        lpb = list(map(operator.__inv__, self.vector))
        res.vector = array.array("H")
        for i in range(len(lpb)):
            res.vector.append(lpb[i] & 0x0000FFFF)
        return res

    def __add__(self, other: BitVector) -> BitVector:
        """
        Because __add__ is supplied, you can always join two bitvectors by

            bitvec3  =  bitvec1  +  bitvec2

        bitvec3 is a new bitvector object that contains all the bits of bitvec1
        followed by all the bits of bitvec2.
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
        """
        When extending an existing instance of a BitVector,  __iadd__ should be faster
        than __add__ because we do not need to create a new BitVector. The call to
        __iadd__ simply modifies the current bitvector.   __iadd__ is invoked when a
        user calls:

            bitvec1 += bitvec2
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
        "Return the number of bits in a bit vector."
        return self.size

    def read_bits_from_file(self, blocksize: int) -> BitVector:
        """
        You can construct bitvectors directly from the bits in a disk file
        through the calls shown below.  As you can see, this requires two
        steps: First you make a call as illustrated by the first statement
        below.  The purpose of this call is to create a file object that is
        associated with the variable bv.  Subsequent calls to
        read_bits_from_file(n) on this variable return a bitvector for each
        block of n bits thus read.  The read_bits_from_file() throws an
        exception if the argument n is not a multiple of 8.

            bv  =  BitVector(filename = 'somefile')
            bv1 =  bv.read_bits_from_file(64)
            bv2 =  bv.read_bits_from_file(64)
            ...
            ...
            bv.close_file_object()

        When reading a file as shown above, you can test the attribute
        more_to_read of the bitvector object in order to find out if there
        is more to read in the file.  The while loop shown below reads all
        of a file in 64-bit blocks:

            bv = BitVector( filename = 'testinput4.txt' )
            print("Here are all the bits read from the file:")
            while (bv.more_to_read):
                bv_read = bv.read_bits_from_file( 64 )
                print(bv_read)
            bv.close_file_object()

        The size of the last bitvector constructed from a file corresponds
        to how many bytes remain unread in the file at that point.  It is
        your responsibility to zero-pad the last bitvector appropriately
        if, say, you are doing block encryption of the whole file.
        """
        error_str = """You need to first construct a BitVector
        object with a filename as  argument"""
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
        """
        This function is meant to read a bit string from a file like
        object.
        """
        bitlist: list[str] = []
        while 1:
            bit = fp.read()
            if bit == "":
                return bitlist
            bitlist += bit

    def write_bits_to_stream_object(self, fp: Any) -> None:
        """
        You can write a bitvector directly to a stream object, as
        illustrated by:

            fp_write = io.StringIO()
            bitvec.write_bits_to_stream_object(fp_write)
            print(fp_write.getvalue())

        This method does not return anything.

        This function is meant to write a bitvector directly to a file like
        object.  Note that whereas 'write_to_file' method creates a memory
        footprint that corresponds exactly to the bitvector, the
        'write_bits_to_stream_object' actually writes out the 1's and 0's
        as individual items to the file object.  That makes this method
        convenient for creating a string representation of a bitvector,
        especially if you use the StringIO class, as shown in the test
        code.

        """
        for bit_index in range(self.size):
            if self[bit_index] == 0:
                fp.write("0")
            else:
                fp.write("1")

    write_bits_to_fileobject = write_bits_to_stream_object

    def divide_into_two(self) -> list[BitVector]:
        """
        A bitvector containing an even number of bits can be divided into
        two equal parts by

            [left_half, right_half] = bitvec.divide_into_two()

        where left_half and right_half hold references to the two returned
        bitvectors.  The method throws an exception when called on a
        bitvector with an odd number of bits.
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
        """
        This method returns a new bitvector object.  Permuting a bitvector means
        that you select its bits in the sequence specified by the argument
        permute_list.
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
        """
        This method returns a new bitvector object. As indicated earlier
        for the permute() method, permuting a bitvector means that you
        select its bits in the sequence specified by the argument
        permute_list. Calling unpermute() with the same argument
        permute_list restores the sequence of bits to what it was in
        the original bitvector.
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
        """
        You can write a bit vector directly to a file by calling
        write_to_file(), as illustrated by the following example that reads
        one bitvector from a file and then writes it to another file:

            bv = BitVector(filename = 'input.txt')
            bv1 = bv.read_bits_from_file(64)
            print(bv1)
            FILEOUT = open('output.bits', 'wb')
            bv1.write_to_file(FILEOUT)
            FILEOUT.close()
            bv = BitVector(filename = 'output.bits')
            bv2 = bv.read_bits_from_file(64)
            print(bv2)

        Since all file I/O is byte oriented, the method write_to_file()
        throws an exception if the size of the bitvector on which the
        method is invoked is not a multiple of 8.  This method does not
        return anything.

        IMPORTANT FOR WINDOWS USERS: When writing an internally generated
                    bit vector out to a disk file, it is important to open
                    the file in the binary mode as shown.  Otherwise, the
                    bit pattern 00001010 ('\\n') in your bitstring will be
                    written out as 0000110100001010 ('\\r\\n'), which is
                    the linebreak on Windows machines.
        """
        err_str = """Only a bit vector whose length is a multiple of 8 can
            be written to a file.  Use the padding functions to satisfy
            this constraint."""
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
        """
        When you construct bitvectors by block scanning a disk file, after
        you are done, you can call this method to close the file object
        that was created to read the file:

            bv  =  BitVector(filename = 'somefile')
            bv1 =  bv.read_bits_from_file(64)
            bv.close_file_object()

        The constructor call in the first statement creates a file object
        for reading the bits.  It is this file object that is closed when
        you call close_file_object().
        """
        if not self.FILEIN:
            raise SyntaxError("No associated open file")
        self.FILEIN.close()

    def int_val(self) -> int:
        "Return the integer value of a bitvector"
        intVal = 0
        for i in range(self.size):
            intVal += self[i] * (2 ** (self.size - i - 1))
        return intVal

    intValue = int_val

    def get_bitvector_in_ascii(self) -> str:
        """
        You can call get_bitvector_in_ascii() to directly convert a bit
        vector into a text string (this is a useful thing to do only if the
        length of the vector is an integral multiple of 8 and every byte in
        your bitvector has a print representation):

            bv = BitVector(textstring = "hello")
            print(bv)        # 0110100001100101011011000110110001101111
            mytext = bv3.get_bitvector_in_ascii()
            print mytext                           # hello

        This method is useful when you encrypt text through its bitvector
        representation.  After decryption, you can recover the text using
        the call shown here.  A call to get_bitvector_in_ascii() returns a
        string.
        """
        if self.size % 8:
            raise ValueError("""\nThe bitvector for get_bitvector_in_ascii()
                                  must be an integral multiple of 8 bits""")
        return "".join(
            map(chr, map(int, [self[i : i + 8] for i in range(0, self.size, 8)]))
        )

    def get_bitvector_in_hex(self) -> str:
        """
        You can directly convert a bit vector into a hex string (this is a
        useful thing to do only if the length of the vector is an integral
        multiple of 4):

            bv4 = BitVector(hexstring = "68656c6c6f")
            print(bv4)     # 0110100001100101011011000110110001101111
            myhexstring = bv4.get_bitvector_in_hex()
            print myhexstring                      # 68656c6c6

        This method throws an exception if the size of the bitvector is not
        a multiple of 4.  The method returns a string that is formed by
        scanning the bits from the left and replacing each sequence of 4
        bits by its corresponding hex digit.
        """
        if self.size % 4:
            raise ValueError(
                """\nThe bitvector for get_bitvector_in_hex() """
                """must be an integral multiple of 4 bits"""
            )
        return "".join(
            map(
                lambda x: x.replace("0x", ""),
                map(hex, map(int, [self[i : i + 4] for i in range(0, self.size, 4)])),
            )
        )

    def __lshift__(self, n: int) -> Self:
        """
        Left circular rotation of a BitVector through N positions can be
        carried out by

            bitvec  << N

        This operator overloading is made possible by implementing the
        __lshift__ method defined here.  Note that this operator returns
        the bitvector on which it is invoked.  This allows for a chained
        invocation of the operator

        """
        if self.size == 0:
            raise ValueError("""Circular shift of an empty vector
                                makes no sense""")
        if n < 0:
            return self >> abs(n)
        for i in range(n):
            self.circular_rotate_left_by_one()
        return self

    def __rshift__(self, n: int) -> Self:
        """
        Right circular rotation of a BitVector through N positions can be
        carried out by

            bitvec  >> N

        This operator overloading is made possible by implementing the
        __rshift__ method defined here.  Note that this operator returns
        the bitvector on which it is invoked.  This allows for a chained
        invocation of the operator.
        """
        if self.size == 0:
            raise ValueError("""Circular shift of an empty vector makes no sense""")
        if n < 0:
            return self << abs(n)
        for i in range(n):
            self.circular_rotate_right_by_one()
        return self

    def circular_rotate_left_by_one(self) -> None:
        "For a one-bit in-place left circular shift"
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
        "For a one-bit in-place right circular shift"
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
        """
        This is merely another implementation of the method
        circular_rotate_left_by_one() shown above.  This one does NOT use map
        functions.  This method carries out a one-bit left circular shift of a bit
        vector.
        """
        max_index = (self.size - 1) // 16
        left_most_bit = self.vector[0] & 1
        self.vector[0] = self.vector[0] >> 1
        for i in range(1, max_index + 1):
            left_bit = self.vector[i] & 1
            self.vector[i] = self.vector[i] >> 1
            self.vector[i - 1] |= left_bit << 15
        self._setbit(self.size - 1, left_most_bit)

    def circular_rot_right(self) -> None:
        """
        This is merely another implementation of the method
        circular_rotate_right_by_one() shown above.  This one does NOT use map
        functions.  This method does a one-bit right circular shift of a bit vector.
        """
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
        """
        For a one-bit in-place left non-circular shift.  Note that bitvector size
        does not change.  The leftmost bit that moves past the first element of the
        bitvector is discarded and rightmost bit of the returned vector is set to
        zero.
        """
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
        """
        For a one-bit in-place right non-circular shift.  Note that bitvector size
        does not change.  The rightmost bit that moves past the last element of the
        bitvector is discarded and leftmost bit of the returned vector is set to
        zero.
        """
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
        """
        Call this method if you want to shift in-place a bitvector to the left
        non-circularly.  As a bitvector is shifted non-circularly to the
        left, the exposed bit positions at the right end are filled with
        zeros. This method returns the bitvector object on which it is
        invoked.  This is to allow for chained invocations of the method.
        """
        for i in range(n):
            self.shift_left_by_one()
        return self

    def shift_right(self, n: int) -> Self:
        """
        Call this method if you want to shift in-place a bitvector to the right
        non-circularly.  As a bitvector is shifted non-circularly to the
        right, the exposed bit positions at the left end are filled with
        zeros. This method returns the bitvector object on which it is
        invoked.  This is to allow for chained invocations of the method.
        """
        for i in range(n):
            self.shift_right_by_one()
        return self

    # Allow array like subscripting for getting and setting:
    __getitem__ = _getbit

    def __setitem__(self, pos: int | slice | Any, item: int | BitVector | Any) -> Any:
        """
        This is needed for both slice assignments and for index assignments.  It
        checks the types of pos and item to see if the call is for slice assignment.
        For slice assignment, pos must be of type 'slice' and item of type BitVector.
        For index assignment, the argument types are checked in the _setbit() method.
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
        """
        To allow iterations over a bit vector by supporting the 'for bit in
        bit_vector' syntax:
        """
        return BitVectorIterator(self)

    def __str__(self) -> str:
        "To create a print representation"
        if self.size == 0:
            return ""
        return "".join(map(str, self))

    def __eq__(self, other: Any) -> bool:
        """
        Compare two bit vectors
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
        return not self == other

    def __lt__(self, other: Any) -> bool:
        return self.intValue() < other.intValue()

    def __le__(self, other: Any) -> bool:
        return self.intValue() <= other.intValue()

    def __gt__(self, other: Any) -> bool:
        return self.intValue() > other.intValue()

    def __ge__(self, other: Any) -> bool:
        return self.intValue() >= other.intValue()

    def __deepcopy__(self, memo: dict[int, Any] | None = None) -> Self:
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

    def deep_copy(self) -> BitVector:
        """
        You can make a deep copy of a bitvector by

            bitvec_copy =  bitvec.deep_copy()

        Subsequently, any alterations to either of the bitvector objects
        bitvec and bitvec_copy will not affect the other.
        """
        return copy.deepcopy(self)

    def _resize_pad_from_left(self, n: int) -> BitVector:
        """
        Resize a bit vector by padding with n 0's from the left. Return the result as
        a new bit vector.
        """
        new_str = "0" * n + str(self)
        return BitVector(bitstring=new_str)

    def pad_from_left(self, n: int) -> None:
        """
        You can pad a bitvector at its the left end with a designated number of
        zeros with this method. This method returns the bitvector object on
        which it is invoked. So you can think of this method as carrying
        out an in-place extension of a bitvector (although, under the hood,
        the extension is carried out by giving a new longer _vector
        attribute to the bitvector object).
        """
        new_str = "0" * n + str(self)
        bitlist = list(map(int, list(new_str)))
        self.size = len(bitlist)
        two_byte_ints_needed = (len(bitlist) + 15) // 16
        self.vector = array.array("H", [0] * two_byte_ints_needed)
        list(map(self._setbit, enumerate(bitlist), bitlist))

    def pad_from_right(self, n: int) -> None:
        """
        You can pad a bitvector at its right end with a designated number of
        zeros with this method. This method returns the bitvector object on
        which it is invoked. So you can think of this method as carrying
        out an in-place extension of a bitvector (although, under the hood,
        the extension is carried out by giving a new longer _vector
        attribute to the bitvector object).
        """
        new_str = str(self) + "0" * n
        bitlist = list(map(int, list(new_str)))
        self.size = len(bitlist)
        two_byte_ints_needed = (len(bitlist) + 15) // 16
        self.vector = array.array("H", [0] * two_byte_ints_needed)
        list(map(self._setbit, enumerate(bitlist), bitlist))

    def __contains__(self, otherBitVec: BitVector) -> bool:
        """
        This supports 'if x in y' and 'if x not in y' syntax for bit vectors.
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
        """
        Resets a previously created BitVector to either all zeros or all ones
        depending on the argument val.  Returns self to allow for syntax like
               bv = bv1[3:6].reset(1)
        or
               bv = bv1[:].reset(1)
        """
        if val not in (0, 1):
            raise ValueError("Incorrect reset argument")
        bitlist = [val for i in range(self.size)]
        list(map(self._setbit, enumerate(bitlist), bitlist))
        return self

    def count_bits(self) -> int:
        """
        You can count the number of bits set in a BitVector instance by

            bv = BitVector(bitstring = '100111')
            print(bv.count_bits())                 # 4

        A call to count_bits() returns an integer value that is equal to
        the number of bits set in the bitvector.
        """
        return sum(self)

    def set_value(self, *args: Any, **kwargs: Any) -> None:
        """
        You can call set_value() to change the bit pattern associated with
        a previously constructed bitvector object:

            bv = BitVector(intVal = 7, size =16)
            print(bv)                              # 0000000000000111
            bv.set_value(intVal = 45)
            print(bv)                              # 101101

        You can think of this method as carrying out an in-place resetting
        of the bit array in a bitvector. The method does not return
        anything.  The allowable modes for changing the internally stored
        bit array for a bitvector are the same as for the constructor.
        """
        BitVector.__init__(self, *args, **kwargs)

    def count_bits_sparse(self) -> int:
        """
        For folks who use bit vectors with millions of bits in them but
        with only a few bits set, your bit counting will go much, much
        faster if you call count_bits_sparse() instead of count_bits():
        However, for dense bitvectors, I expect count_bits() to work
        faster.

            # a BitVector with 2 million bits:
            bv = BitVector(size = 2000000)
            bv[345234] = 1
            bv[233]=1
            bv[243]=1
            bv[18]=1
            bv[785] =1
            print(bv.count_bits_sparse())          # 5

        A call to count_bits_sparse() returns an integer whose value is the
        number of bits set in the bitvector.  Rhiannon, who contributed
        this method, estimates that if a bit vector with over 2 millions
        bits has only five bits set, this will return the answer in 1/18 of
        the time taken by the count_bits() method. Rhianon's implementation
        is based on an algorithm generally known as the Brian Kernighan's
        way, although its antecedents predate its mention by Kernighan and
        Ritchie.
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
        """
        You can calculate the similarity between two bitvectors using the
        Jaccard similarity coefficient.

            bv1 = BitVector(bitstring = '11111111')
            bv2 = BitVector(bitstring = '00101011')
            print bv1.jaccard_similarity(bv2)               # 0.675

        The value returned is a floating point number between 0 and 1.
        """
        assert self.intValue() > 0 or other.intValue() > 0, (
            "Jaccard called on two zero vectors --- NOT ALLOWED"
        )
        assert self.size == other.size, (
            "bitvectors for comparing with Jaccard must be of equal length"
        )
        intersect = self & other
        union = self | other
        return intersect.count_bits_sparse() / float(union.count_bits_sparse())

    def jaccard_distance(self, other: BitVector) -> float:
        """
        You can calculate the distance between two bitvectors using the
        Jaccard distance coefficient.

            bv1 = BitVector(bitstring = '11111111')
            bv2 = BitVector(bitstring = '00101011')
            print(str(bv1.jaccard_distance(bv2)))           # 0.375

        The value returned is a floating point number between 0 and 1.
        """
        assert self.size == other.size, "vectors of unequal length"
        return 1 - self.jaccard_similarity(other)

    def hamming_distance(self, other: BitVector) -> int:
        """
        You can compare two bitvectors with the Hamming distance:

            bv1 = BitVector(bitstring = '11111111')
            bv2 = BitVector(bitstring = '00101011')
            print(str(bv1.hamming_distance(bv2)))           # 4

        This method returns a number that is equal to the number of bit
        positions in which the two operand bitvectors disagree.
        """
        assert self.size == other.size, "vectors of unequal length"
        diff = self ^ other
        return diff.count_bits_sparse()

    def next_set_bit(self, from_index: int = 0) -> int:
        """
        Starting from a given bit position, you can find the position index
        of the next set bit by

            bv = BitVector(bitstring = '00000000000001')
            print(bv.next_set_bit(5))                       # 13

        In this example, we are asking next_set_bit() to return the index
        of the bit that is set after the bit position that is indexed 5. If
        no next set bit is found, the method returns -1.  A call to
        next_set_bit() always returns a number.  This method was
        contributed originally by Jason Allum and updated subsequently by
        John Gleeson.
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
        """
        You can measure the "rank" of a bit that is set at a given
        position.  Rank is the number of bits that are set up to the
        position of the bit you are interested in.

            bv = BitVector(bitstring = '01010101011100')
            print(bv.rank_of_bit_set_at_index(10))          # 6

        The value 6 returned by this call to rank_of_bit_set_at_index() is
        the number of bits set up to the position indexed 10 (including
        that position). This method throws an exception if there is no bit
        set at the argument position. Otherwise, it returns the rank as a
        number.
        """
        assert self[position] == 1, "the arg bit not set"
        bv = self[0 : position + 1]
        return bv.count_bits()

    def is_power_of_2(self) -> bool:
        """
        You can test whether the integer value of a bit vector is a power of
        two.  (The sparse version of this method works much faster for very
        long bit vectors.)  However, the regular version defined here may
        work faster for dense bit vectors.

            bv = BitVector(bitstring = '10000000001110')
            print(bv.is_power_of_2())

        This predicate returns 1 for true and 0 for false.
        """
        if self.intValue() == 0:
            return False
        bv = self & BitVector(intVal=self.intValue() - 1)
        if bv.intValue() == 0:
            return True
        return False

    def is_power_of_2_sparse(self) -> bool:
        """
        You can test whether the integer value of a bit vector is a power of
        two.  This sparse version works much faster for very long bit
        vectors.  (However, the regular version defined above may work
        faster for dense bit vectors.)

            bv = BitVector(bitstring = '10000000001110')
            print(bv.is_power_of_2_sparse())

        This predicate returns 1 for true and 0 for false.
        """
        if self.count_bits_sparse() == 1:
            return True
        return False

    def reverse(self) -> BitVector:
        """
        Given a bit vector, you can construct a bit vector with all the
        bits reversed, in the sense that what was left to right before now
        becomes right to left.

            bv = BitVector(bitstring = '0001100000000000001')
            print(str(bv.reverse()))

        A call to reverse() returns a new bitvector object whose bits are
        in reverse order in relation to the bits in the bitvector on which
        the method is invoked.
        """
        reverseList = []
        i = 1
        while i < self.size + 1:
            reverseList.append(self[-i])
            i += 1
        return BitVector(bitlist=reverseList)

    def gcd(self, other: BitVector) -> BitVector:
        """
        Using Euclid's Algorithm, returns the greatest common divisor of
        the integer value of the bitvector on which the method is invoked
        and the integer value of the argument bitvector:

            bv1 = BitVector(bitstring = '01100110')     # int val: 102
            bv2 = BitVector(bitstring = '011010')       # int val: 26
            bv = bv1.gcd(bv2)
            print(int(bv))                              # 2

        The result returned by gcd() is a bitvector object.
        """
        a = self.intValue()
        b = other.intValue()
        if a < b:
            a, b = b, a
        while b != 0:
            a, b = b, a % b
        return BitVector(intVal=a)

    def multiplicative_inverse(self, modulus: BitVector) -> BitVector | None:
        """
        Using the Extended Euclid's Algorithm, this method calculates the
        multiplicative inverse using normal integer arithmetic.  [For such
        inverses in a Galois Field GF(2^n), use the method gf_MI().]

            bv_modulus = BitVector(intVal = 32)
            bv = BitVector(intVal = 17)
            bv_result = bv.multiplicative_inverse( bv_modulus )
            if bv_result is not None:
                print(str(int(bv_result)))           # 17
            else: print "No multiplicative inverse in this case"

        What this example says is that the multiplicative inverse of 17
        modulo 32 is 17.  That is because 17 times 17 modulo 32 equals 1.
        When using this method, you must test the returned value for
        None. If the returned value is None, that means that the number
        corresponding to the bitvector on which the method is invoked does
        not possess a multiplicative-inverse with respect to the modulus.
        When the multiplicative inverse exists, the result returned by
        calling multiplicative_inverse() is a bitvector object.
        """
        MOD = mod = modulus.intValue()
        num = self.intValue()
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
        return self.size

    def gf_multiply(self, b: BitVector) -> BitVector:
        """
        If you want to multiply two bit patterns in GF(2):

            a = BitVector(bitstring='0110001')
            b = BitVector(bitstring='0110')
            c = a.gf_multiply(b)
            print(c)                                   # 00010100110

        As you would expect, in general, the bitvector returned by this
        method is longer than the two operand bitvectors. A call to
        gf_multiply() returns a bitvector object.
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
        """
        To divide a bitvector by a modulus bitvector in the Galois Field
        GF(2^n):

            mod = BitVector(bitstring='100011011')     # AES modulus
            n = 8
            a = BitVector(bitstring='11100010110001')
            quotient, remainder = a.gf_divide_by_modulus(mod, n)
            print(quotient)                            # 00000000111010
            print(remainder)                           # 10001111

        What this example illustrates is dividing the bitvector a by the
        modulus bitvector mod.  For a more general division of one
        bitvector a by another bitvector b, you would multiply a by the MI
        of b, where MI stands for "multiplicative inverse" as returned by
        the call to the method gf_MI().  A call to gf_divide_by_modulus()
        returns two bitvectors, one for the quotient and the other for the
        remainder.
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
        """
        If you want to carry out modular multiplications in the Galois
        Field GF(2^n):

            modulus = BitVector(bitstring='100011011') # AES modulus
            n = 8
            a = BitVector(bitstring='0110001')
            b = BitVector(bitstring='0110')
            c = a.gf_multiply_modular(b, modulus, n)
            print(c)                                   # 10100110

        The call to gf_multiply_modular() returns the product of the two
        bitvectors a and b modulo the bitvector modulus in GF(2^8). A call
        to gf_multiply_modular() returns is a bitvector object.
        """
        a = self
        a_copy = copy.deepcopy(a)
        b_copy = copy.deepcopy(b)
        product = a_copy.gf_multiply(b_copy)
        quotient, remainder = product.gf_divide_by_modulus(mod, n)
        return remainder

    def gf_MI(self, mod: BitVector, n: int) -> BitVector | tuple[str, ...]:
        """
        To calculate the multiplicative inverse of a bit vector in the
        Galois Field GF(2^n) with respect to a modulus polynomial, call
        gf_MI() as follows:

            modulus = BitVector(bitstring = '100011011')
            n = 8
            a = BitVector(bitstring = '00110011')
            multi_inverse = a.gf_MI(modulus, n)
            print multi_inverse                        # 01101100

        A call to gf_MI() returns a bitvector object.
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
        """
        You can extract from a bitvector the runs of 1's and 0's in the
        vector as follows:

           bv = BitVector(bitlist = (1,1, 1, 0, 0, 1))
           print(str(bv.runs()))                      # ['111', '00', '1']

        The object returned by runs() is a list of strings, with each
        element of this list being a string of 1's and 0's.
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
        """
        You can test whether a randomly generated bit vector is a prime
        number using the probabilistic Miller-Rabin test

            bv = BitVector(intVal = 0)
            bv = bv.gen_random_bits(32)
            check = bv.test_for_primality()
            print(check)

        The test_for_primality() methods returns a floating point number
        close to 1 for prime numbers and 0 for composite numbers.  The
        actual value returned for a prime is the probability associated
        with the determination of its primality.
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
        """
        You can generate a bitvector with random bits with the bits
        spanning a specified width.  For example, if you wanted a random
        bit vector to fully span 32 bits, you would say

            bv = BitVector(intVal = 0)
            bv = bv.gen_random_bits(32)
            print(bv)                # 11011010001111011010011111000101

        As you would expect, gen_random_bits() returns a bitvector object.

        The bulk of the work here is done by calling random.getrandbits(
        width) which returns an integer whose binary code representation
        will NOT BE LARGER than the argument 'width'.  When random numbers
        are generated as candidates for primes, you often want to make sure
        that the random number thus created spans the full width specified
        by 'width' and that the number is odd.  This we do by setting the
        two most significant bits and the least significant bit.
        """
        candidate = random.getrandbits(width)
        candidate |= 1
        candidate |= 1 << width - 1
        candidate |= 2 << width - 3
        return BitVector(intVal=candidate)

    def min_canonical(self) -> BitVector:
        """
        This method returns the "canonical" form of a BitVector instance that is obtained by
        circularly rotating the bit pattern through all possible shifts and returning the
        pattern with the maximum number of leading zeros.  This is also the minimum int value
        version of a bit pattern.  This method is useful in the "Local Binary Pattern"
        algorithm for characterizing image textures.  If you are curious as to how, see my
        tutorial on "Measuring Texture and Color in Images."
        """
        intvals_for_circular_shifts = [int(self << 1) for _ in range(len(self))]
        return BitVector(intVal=min(intvals_for_circular_shifts), size=len(self))


class BitVectorIterator:
    items: list[int]
    index: int

    def __init__(self, bitvec: BitVector) -> None:
        self.items = []
        for i in range(bitvec.size):
            self.items.append(bitvec._getbit(i))
        self.index = -1

    def __iter__(self) -> Self:
        return self

    def next(self) -> int:
        self.index += 1
        if self.index < len(self.items):
            return self.items[self.index]
        else:
            raise StopIteration

    __next__ = next
