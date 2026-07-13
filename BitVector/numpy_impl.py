from typing import Any, Iterator, Self

import numpy as np


class NumpyBitVectorBase:
    __slots__ = ("size", "vector", "dtype", "bits_per_word")
    vector: Any

    # To be overridden by subclasses
    _dtype: Any = np.uint16
    _bits_per_word = 16

    def __init__(
        self,
        *,
        size: int | None = None,
        intVal: int | None = None,
        bitstring: str | None = None,
    ) -> None:
        self.dtype = self._dtype
        self.bits_per_word = self._bits_per_word

        if bitstring is not None:
            self.size = len(bitstring)
            words = (self.size + self.bits_per_word - 1) // self.bits_per_word
            self.vector = np.zeros(words, dtype=self.dtype)
            for i, c in enumerate(bitstring):
                if c == "1":
                    self.vector[i // self.bits_per_word] |= self.dtype(1) << self.dtype(
                        i % self.bits_per_word
                    )
        elif intVal is not None and size is not None:
            self.size = size
            words = (self.size + self.bits_per_word - 1) // self.bits_per_word
            self.vector = np.zeros(words, dtype=self.dtype)
            val = intVal
            for i in range(self.size - 1, -1, -1):
                if val & 1:
                    self.vector[i // self.bits_per_word] |= self.dtype(1) << self.dtype(
                        i % self.bits_per_word
                    )
                val >>= 1
        elif size is not None:
            self.size = size
            words = (self.size + self.bits_per_word - 1) // self.bits_per_word
            self.vector = np.zeros(words, dtype=self.dtype)
        else:
            raise ValueError("Invalid arguments")

    def _clone(self) -> Self:
        new_bv = self.__class__(size=self.size)
        new_bv.vector = np.copy(self.vector)
        return new_bv

    def __and__(self, other: Self) -> Self:
        if self.size != other.size:
            raise ValueError("BitVectors must be of equal length for bitwise AND")
        new_bv = self._clone()
        new_bv.vector = self.vector & other.vector
        return new_bv

    def __or__(self, other: Self) -> Self:
        if self.size != other.size:
            raise ValueError("BitVectors must be of equal length for bitwise OR")
        new_bv = self._clone()
        new_bv.vector = self.vector | other.vector
        return new_bv

    def __xor__(self, other: Self) -> Self:
        if self.size != other.size:
            raise ValueError("BitVectors must be of equal length for bitwise XOR")
        new_bv = self._clone()
        new_bv.vector = self.vector ^ other.vector
        return new_bv

    def __invert__(self) -> Self:
        new_bv = self._clone()
        new_bv.vector = ~self.vector
        # Clean up padding bits
        rem = self.size % self.bits_per_word
        if rem != 0:
            mask = (self.dtype(1) << self.dtype(rem)) - self.dtype(1)
            new_bv.vector[-1] &= mask
        return new_bv

    def __add__(self, other: Self) -> Self:
        # Concatenation
        new_size = self.size + other.size
        new_bv = self.__class__(size=new_size)

        # Copy first part
        new_bv.vector[: len(self.vector)] = self.vector

        # Shift and copy second part
        shift_amount = self.size % self.bits_per_word
        word_offset = self.size // self.bits_per_word

        if shift_amount == 0:
            new_bv.vector[word_offset : word_offset + len(other.vector)] = other.vector
        else:
            # We need to shift the bits of 'other' by 'shift_amount' and add them
            for i in range(len(other.vector)):
                val = other.vector[i]
                new_bv.vector[word_offset + i] |= val << self.dtype(shift_amount)
                if word_offset + i + 1 < len(new_bv.vector):
                    new_bv.vector[word_offset + i + 1] |= val >> self.dtype(
                        self.bits_per_word - shift_amount
                    )
        return new_bv

    def __iadd__(self, other: Self) -> Self:
        return self.__add__(other)

    def __lshift__(self, n: int) -> Self:
        if n < 0:
            raise ValueError("shift count must be non-negative")
        n = n % self.size if self.size > 0 else 0
        if n == 0 or self.size == 0:
            return self._clone()

        new_bv = self.__class__(size=self.size)
        for i in range(self.size):
            if self._getbit((i + n) % self.size):
                new_bv._setbit(i, 1)
        return new_bv

    def __rshift__(self, n: int) -> Self:
        if n < 0:
            raise ValueError("shift count must be non-negative")
        n = n % self.size if self.size > 0 else 0
        if n == 0 or self.size == 0:
            return self._clone()

        new_bv = self.__class__(size=self.size)
        for i in range(self.size):
            if self._getbit((i - n) % self.size):
                new_bv._setbit(i, 1)
        return new_bv

    def _getbit(self, pos: int) -> int:
        return int(
            (
                self.vector[pos // self.bits_per_word]
                >> self.dtype(pos % self.bits_per_word)
            )
            & 1
        )

    def _setbit(self, pos: int, val: int) -> None:
        if val:
            self.vector[pos // self.bits_per_word] |= self.dtype(1) << self.dtype(
                pos % self.bits_per_word
            )
        else:
            self.vector[pos // self.bits_per_word] &= ~(
                self.dtype(1) << self.dtype(pos % self.bits_per_word)
            )

    def __len__(self) -> int:
        return self.size

    def __int__(self) -> int:
        return self.int_val()

    def __iter__(self) -> Iterator[int]:
        for i in range(self.size):
            yield self._getbit(i)

    def __str__(self) -> str:
        if self.size == 0:
            return ""
        return "".join(str(self._getbit(i)) for i in range(self.size))

    def int_val(self) -> int:
        val = 0
        for i in range(self.size):
            val = (val << 1) | self._getbit(i)
        return val

    def count_bits(self) -> int:
        # A simple popcount could use bin(x).count('1')
        count = 0
        for word in self.vector:
            count += bin(int(word)).count("1")
        return count

    def count_bits_sparse(self) -> int:
        count = 0
        for word in self.vector:
            w = int(word)
            while w:
                w &= w - 1
                count += 1
        return count

    def next_set_bit(self, from_index: int = 0) -> int:
        for i in range(from_index, self.size):
            if self._getbit(i):
                return i
        return -1

    def is_power_of_2(self) -> bool:
        return self.count_bits() == 1

    def is_power_of_2_sparse(self) -> bool:
        return self.count_bits_sparse() == 1

    def _cmp_values(self, other: object) -> int:
        # returns -1 if self < other, 0 if ==, 1 if >
        if isinstance(other, int):
            s_val = self.int_val()
            if s_val < other:
                return -1
            elif s_val > other:
                return 1
            else:
                return 0
        elif isinstance(other, float):
            s_val = self.int_val()
            if s_val < other:
                return -1
            elif s_val > other:
                return 1
            else:
                return 0
        elif isinstance(other, NumpyBitVectorBase):
            # compare lengths first then int val or array values
            if self.size < other.size:
                return -1
            elif self.size > other.size:
                return 1
            # equal size
            # the easiest reliable comparison is comparing their integer values,
            # or bit by bit since array chunks are little endian in bits but sequence is big endian.
            s_val = self.int_val()
            o_val = other.int_val()
            if s_val < o_val:
                return -1
            elif s_val > o_val:
                return 1
            return 0
        else:
            # fallback
            if hasattr(other, "int_val"):
                other_cast: Any = other
                other_val = other_cast.int_val()
                s_val = self.int_val()
                if s_val < other_val:
                    return -1
                elif s_val > other_val:
                    return 1
                else:
                    return 0
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        res = self._cmp_values(other)
        if res is NotImplemented:
            return False
        return res == 0

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: object) -> bool:
        res = self._cmp_values(other)
        if res is NotImplemented:
            return False
        return res == -1

    def __le__(self, other: object) -> bool:
        res = self._cmp_values(other)
        if res is NotImplemented:
            return False
        return res in (-1, 0)

    def __gt__(self, other: object) -> bool:
        res = self._cmp_values(other)
        if res is NotImplemented:
            return False
        return res == 1

    def __ge__(self, other: object) -> bool:
        res = self._cmp_values(other)
        if res is NotImplemented:
            return False
        return res in (1, 0)

    def __contains__(self, otherBitVec: Self) -> bool:
        if self.size == 0 or otherBitVec.size == 0 or otherBitVec.size > self.size:
            return False

        # very simple sliding window
        target = otherBitVec.int_val()
        target_size = otherBitVec.size

        for i in range(self.size - target_size + 1):
            val = 0
            for j in range(target_size):
                val = (val << 1) | self._getbit(i + j)
            if val == target:
                return True
        return False

    def __getitem__(self, pos: int | slice | Any) -> Any:
        if isinstance(pos, slice):
            start, stop, step = pos.indices(self.size)
            if step != 1:
                raise ValueError("Slice step must be 1")
            if stop < start:
                stop = start
            new_size = stop - start
            new_bv = self.__class__(size=new_size)
            for i in range(new_size):
                new_bv._setbit(i, self._getbit(start + i))
            return new_bv
        elif isinstance(pos, int):
            if pos < 0:
                pos += self.size
            if pos < 0 or pos >= self.size:
                raise IndexError("Index out of range")
            return self._getbit(pos)
        else:
            raise TypeError("Invalid argument type")

    def __setitem__(self, pos: int | slice | Any, item: int | Self | Any) -> Any:
        if isinstance(pos, slice):
            start, stop, step = pos.indices(self.size)
            if step != 1:
                raise ValueError("Slice step must be 1")
            if stop < start:
                stop = start
            slice_size = stop - start
            if hasattr(item, "size") and hasattr(item, "_getbit"):
                if getattr(item, "size") != slice_size:
                    raise ValueError("Size mismatch")
                for i in range(slice_size):
                    self._setbit(start + i, getattr(item, "_getbit")(i))
            else:
                raise TypeError("Item must be a bit vector")
        elif isinstance(pos, int):
            if pos < 0:
                pos += self.size
            if pos < 0 or pos >= self.size:
                raise IndexError("Index out of range")
            self._setbit(pos, int(item))
        else:
            raise TypeError("Invalid argument type")


class NumpyBitVector8(NumpyBitVectorBase):
    _dtype = np.uint8
    _bits_per_word = 8


class NumpyBitVector16(NumpyBitVectorBase):
    _dtype = np.uint16
    _bits_per_word = 16


class NumpyBitVector32(NumpyBitVectorBase):
    _dtype = np.uint32
    _bits_per_word = 32


class NumpyBitVector64(NumpyBitVectorBase):
    _dtype = np.uint64
    _bits_per_word = 64
