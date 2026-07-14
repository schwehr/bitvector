import array
from typing import Any
import operator
import mmap

class BitVector:
    def __init__(self, size=0):
        self.size = size
        two_byte_ints_needed = (size + 15) // 16
        self.vector = array.array("H", [0] * two_byte_ints_needed)

    def circular_rot_left(self) -> None:
        size = len(self.vector)
        if size == 0:
            return
        left_most_bits = list(map(operator.__and__, self.vector, [1] * size))
        left_most_bits.append(left_most_bits[0])
        del left_most_bits[0]
        self._set_vector(list(map(operator.__rshift__, self.vector, [1] * size)))
        self._set_vector(list(
            map(
                operator.__or__,
                self.vector,
                list(map(operator.__lshift__, left_most_bits, [15] * size)),
            )
        ))

    def _set_vector(self, new_vec):
        if isinstance(self.vector, array.array):
            self.vector = array.array("H", new_vec)
        elif isinstance(self.vector, memoryview):
            self.vector[:] = array.array("H", new_vec)
        else:
            self.vector = new_vec

class MmapBitVector(BitVector):
    def __init__(self, size=0):
        self.size = size
        two_byte_ints_needed = (size + 15) // 16
        if two_byte_ints_needed > 0:
            self._mmap = mmap.mmap(-1, two_byte_ints_needed * 2)
            self.vector = memoryview(self._mmap).cast('H')
        else:
            self._mmap = None
            self.vector = []

m = MmapBitVector(100)
m.vector[0] = 5
m.circular_rot_left()
print(m.vector[0])
