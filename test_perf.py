import timeit
import array

setup = """
from BitVector import BitVector
import mmap

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

b1 = BitVector(size=1000000)
b2 = MmapBitVector(size=1000000)
"""

print("BitVector init:", timeit.timeit("BitVector(size=1000000)", setup=setup, number=100))
print("MmapBitVector init:", timeit.timeit("MmapBitVector(size=1000000)", setup=setup, number=100))

print("BitVector set:", timeit.timeit("b1[500000] = 1", setup=setup, number=10000))
print("MmapBitVector set:", timeit.timeit("b2[500000] = 1", setup=setup, number=10000))

print("BitVector get:", timeit.timeit("x = b1[500000]", setup=setup, number=10000))
print("MmapBitVector get:", timeit.timeit("x = b2[500000]", setup=setup, number=10000))
