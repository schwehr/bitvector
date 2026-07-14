import timeit
import operator

setup = """
from BitVector import BitVector
import mmap
import array

class MmapBitVector(BitVector):
    __slots__ = ("_mmap",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        two_byte_ints_needed = (self.size + 15) // 16
        if two_byte_ints_needed > 0:
            self._mmap = mmap.mmap(-1, two_byte_ints_needed * 2)
            self.vector = memoryview(self._mmap).cast('H')
        else:
            self._mmap = None
            self.vector = []

b1 = BitVector(size=10000)
b1[100] = 1

m1 = MmapBitVector(size=10000)
m1[100] = 1
"""

print("BitVector count_bits:", timeit.timeit("b1.count_bits()", setup=setup, number=1000))
print("MmapBitVector count_bits:", timeit.timeit("m1.count_bits()", setup=setup, number=1000))
