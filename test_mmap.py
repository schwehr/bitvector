import mmap
from BitVector import BitVector

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

b = MmapBitVector(size=100)
b[10] = 1
print(b[10])
print(type(b.vector))
