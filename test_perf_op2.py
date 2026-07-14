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

b1 = BitVector(size=100000)
b1[100] = 1
b2 = BitVector(size=100000)
b2[200] = 1

m1 = MmapBitVector(size=100000)
m1[100] = 1
m2 = MmapBitVector(size=100000)
m2[200] = 1

import operator
"""

print("BitVector and:", timeit.timeit("operator.and_(b1, b2)", setup=setup, number=1000))
print("MmapBitVector and:", timeit.timeit("operator.and_(m1, m2)", setup=setup, number=1000))
