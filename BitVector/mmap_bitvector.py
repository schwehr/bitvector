import math
import mmap
import tempfile
from typing import Any, Iterator, Self, cast


class MmapBitVector:
    def __init__(
        self,
        *,
        size: int | None = None,
        intVal: int | None = None,
        bitstring: str | None = None,
    ):
        self.size = size if size is not None else 0
        if bitstring is not None:
            self.size = len(bitstring)
        elif intVal is not None and self.size == 0:
            self.size = max(1, intVal.bit_length())

        self.byte_size = math.ceil(self.size / 8)

        self._file = tempfile.TemporaryFile()
        self._file.write(b"\x00" * max(1, self.byte_size))
        self._file.flush()

        self._mmap = mmap.mmap(self._file.fileno(), 0)

        if intVal is not None:
            val_bytes = intVal.to_bytes(self.byte_size, byteorder="big")
            self._mmap[: len(val_bytes)] = val_bytes
        elif bitstring is not None:
            intVal = int(bitstring, 2)
            val_bytes = intVal.to_bytes(self.byte_size, byteorder="big")
            self._mmap[: len(val_bytes)] = val_bytes

    def __del__(self):
        if hasattr(self, "_mmap") and self._mmap:
            self._mmap.close()
        if hasattr(self, "_file") and self._file:
            self._file.close()

    def _clone_empty(self, size: int) -> "MmapBitVector":
        return MmapBitVector(size=size)

    def int_val(self) -> int:
        return int.from_bytes(self._mmap[: self.byte_size], byteorder="big")

    def __int__(self) -> int:
        return self.int_val()

    def __len__(self) -> int:
        return self.size

    def __str__(self) -> str:
        if self.size == 0:
            return ""
        return bin(self.int_val())[2:].zfill(self.size)

    def __xor__(self, other: Self) -> "MmapBitVector":
        max_size = max(self.size, other.size)
        res = self._clone_empty(max_size)
        max_bytes = res.byte_size

        # Align bytes to the right (least significant bytes at end)
        s_offset = max_bytes - self.byte_size
        o_offset = max_bytes - other.size // 8 - (1 if other.size % 8 else 0)

        for i in range(max_bytes):
            s_byte = self._mmap[i - s_offset] if i >= s_offset else 0
            o_byte = other._mmap[i - o_offset] if i >= o_offset else 0
            res._mmap[i] = s_byte ^ o_byte
        return cast(Self, res)

    def __and__(self, other: Self) -> "MmapBitVector":
        max_size = max(self.size, other.size)
        res = self._clone_empty(max_size)
        max_bytes = res.byte_size

        s_offset = max_bytes - self.byte_size
        o_offset = max_bytes - math.ceil(other.size / 8)

        for i in range(max_bytes):
            s_byte = self._mmap[i - s_offset] if i >= s_offset else 0
            o_byte = other._mmap[i - o_offset] if i >= o_offset else 0
            res._mmap[i] = s_byte & o_byte
        return cast(Self, res)

    def __or__(self, other: Self) -> "MmapBitVector":
        max_size = max(self.size, other.size)
        res = self._clone_empty(max_size)
        max_bytes = res.byte_size

        s_offset = max_bytes - self.byte_size
        o_offset = max_bytes - math.ceil(other.size / 8)

        for i in range(max_bytes):
            s_byte = self._mmap[i - s_offset] if i >= s_offset else 0
            o_byte = other._mmap[i - o_offset] if i >= o_offset else 0
            res._mmap[i] = s_byte | o_byte
        return cast(Self, res)

    def __invert__(self) -> "MmapBitVector":
        res = self._clone_empty(self.size)
        for i in range(self.byte_size):
            res._mmap[i] = ~self._mmap[i] & 0xFF

        # Clean up padding bits in the most significant byte
        excess = (self.byte_size * 8) - self.size
        if excess > 0 and self.byte_size > 0:
            mask = (1 << (8 - excess)) - 1
            res._mmap[0] &= mask

        return cast(Self, res)

    def __add__(self, other: Self) -> "MmapBitVector":
        res_int = (self.int_val() << other.size) | other.int_val()
        return MmapBitVector(size=self.size + other.size, intVal=res_int)

    def __iadd__(self, other: Self) -> "MmapBitVector":
        res_int = (self.int_val() << other.size) | other.int_val()
        self.size += other.size
        self.byte_size = math.ceil(self.size / 8)

        # Workaround for macOS lacking mremap (resize support)
        try:
            self._mmap.resize(max(1, self.byte_size))
        except SystemError:
            self._mmap.close()
            self._file.truncate(max(1, self.byte_size))
            self._mmap = mmap.mmap(self._file.fileno(), 0)

        val_bytes = res_int.to_bytes(self.byte_size, byteorder="big")
        self._mmap[: len(val_bytes)] = val_bytes
        return self

    def __lshift__(self, n: int) -> "MmapBitVector":
        res_int = (self.int_val() << n) & ((1 << self.size) - 1)
        return MmapBitVector(size=self.size, intVal=res_int)

    def __rshift__(self, n: int) -> "MmapBitVector":
        res_int = self.int_val() >> n
        return MmapBitVector(size=self.size, intVal=res_int)

    def __getitem__(self, pos: int | slice | Any) -> Any:
        if isinstance(pos, slice):
            start, stop, step = pos.indices(self.size)
            if step != 1:
                raise ValueError("Slice steps other than 1 are not supported")
            if start >= stop:
                return MmapBitVector(size=0, intVal=0)
            length = stop - start
            val = self.int_val()
            shift = self.size - stop
            mask = (1 << length) - 1
            res_int = (val >> shift) & mask
            return MmapBitVector(size=length, intVal=res_int)
        else:
            if not isinstance(pos, int):
                raise TypeError("Index must be an integer")
            if pos < 0:
                pos += self.size
            if pos < 0 or pos >= self.size:
                raise IndexError("Index out of range")

            # Direct byte indexing
            bit_index = self.size - pos - 1
            byte_idx = self.byte_size - 1 - (bit_index // 8)
            bit_in_byte = bit_index % 8

            return (self._mmap[byte_idx] >> bit_in_byte) & 1

    def __setitem__(self, pos: int | slice | Any, item: int | Self | Any) -> Any:
        if isinstance(pos, slice):
            start, stop, step = pos.indices(self.size)
            if step != 1:
                raise ValueError("Slice steps other than 1 are not supported")
            length = stop - start
            if isinstance(item, int):
                item_val = item
            else:
                item_val = item.int_val()

            val = self.int_val()
            shift = self.size - stop
            mask = ((1 << length) - 1) << shift

            val = (val & ~mask) | ((item_val << shift) & mask)
            val_bytes = val.to_bytes(self.byte_size, byteorder="big")
            self._mmap[: len(val_bytes)] = val_bytes
        else:
            if not isinstance(pos, int):
                raise TypeError("Index must be an integer")
            if pos < 0:
                pos += self.size
            if pos < 0 or pos >= self.size:
                raise IndexError("Index out of range")

            bit_index = self.size - pos - 1
            byte_idx = self.byte_size - 1 - (bit_index // 8)
            bit_in_byte = bit_index % 8

            byte_val = self._mmap[byte_idx]
            if item:
                byte_val |= 1 << bit_in_byte
            else:
                byte_val &= ~(1 << bit_in_byte)
            self._mmap[byte_idx] = byte_val

    def __iter__(self) -> Iterator[int]:
        # Fast iter using byte index
        for pos in range(self.size):
            bit_index = self.size - pos - 1
            byte_idx = self.byte_size - 1 - (bit_index // 8)
            bit_in_byte = bit_index % 8
            yield (self._mmap[byte_idx] >> bit_in_byte) & 1

    def __eq__(self, other: object) -> bool:
        if not hasattr(other, "size"):
            return NotImplemented
        if self.size != getattr(other, "size", -1):
            return False

        if hasattr(other, "_mmap"):
            other_mmap: Any = getattr(other, "_mmap")
            for i in range(self.byte_size):
                if self._mmap[i] != other_mmap[i]:
                    return False
            return True
        elif hasattr(other, "int_val") and callable(getattr(other, "int_val")):
            other_int_val: Any = getattr(other, "int_val")
            return self.int_val() == other_int_val()
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: object) -> bool:
        if not hasattr(other, "int_val") or not callable(getattr(other, "int_val")):
            return NotImplemented
        other_int_val: Any = getattr(other, "int_val")
        return self.int_val() < other_int_val()

    def __le__(self, other: object) -> bool:
        if not hasattr(other, "int_val") or not callable(getattr(other, "int_val")):
            return NotImplemented
        other_int_val: Any = getattr(other, "int_val")
        return self.int_val() <= other_int_val()

    def __gt__(self, other: object) -> bool:
        if not hasattr(other, "int_val") or not callable(getattr(other, "int_val")):
            return NotImplemented
        other_int_val: Any = getattr(other, "int_val")
        return self.int_val() > other_int_val()

    def __ge__(self, other: object) -> bool:
        if not hasattr(other, "int_val") or not callable(getattr(other, "int_val")):
            return NotImplemented
        other_int_val: Any = getattr(other, "int_val")
        return self.int_val() >= other_int_val()

    def __contains__(self, otherBitVec: Self) -> bool:
        if otherBitVec.size == 0:
            return True
        if self.size < otherBitVec.size:
            return False

        other_val = otherBitVec.int_val()
        mask = (1 << otherBitVec.size) - 1
        val = self.int_val()

        for i in range(self.size - otherBitVec.size + 1):
            if (val >> i) & mask == other_val:
                return True
        return False

    def count_bits(self) -> int:
        count = 0
        for i in range(self.byte_size):
            count += self._mmap[i].bit_count()
        return count

    def count_bits_sparse(self) -> int:
        return self.count_bits()

    def next_set_bit(self, from_index: int = 0) -> int:
        for pos in range(from_index, self.size):
            bit_index = self.size - pos - 1
            byte_idx = self.byte_size - 1 - (bit_index // 8)
            bit_in_byte = bit_index % 8
            if (self._mmap[byte_idx] >> bit_in_byte) & 1:
                return pos
        return -1

    def is_power_of_2(self) -> bool:
        val = self.int_val()
        return val != 0 and (val & (val - 1)) == 0

    def is_power_of_2_sparse(self) -> bool:
        return self.is_power_of_2()
