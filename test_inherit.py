from BitVector import BitVector

class MmapBitVector(BitVector):
    pass

b = MmapBitVector(size=100)
print(b.vector)
