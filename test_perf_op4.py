import mmap
import timeit
setup = """
from BitVector import BitVector
b1 = BitVector(size=10000)
b1[100] = 1

b2 = BitVector(size=10000)
b2[100] = 1
"""
print("BitVector and:", timeit.timeit("b1 & b2", setup=setup, number=10000))
setup2 = """
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

m1 = MmapBitVector(size=10000)
m1[100] = 1

m2 = MmapBitVector(size=10000)
m2[100] = 1
"""
print("MmapBitVector and:", timeit.timeit("m1 & m2", setup=setup2, number=10000))
