from BitVector import BitVector

class MmapBitVector(BitVector):
    __slots__ = ("_mmap",)
    pass

# check if subclass works with the filename arg
with open('test_b.dat', 'wb') as f:
    f.write(b'\xFF\xFF')
b = MmapBitVector(filename='test_b.dat')
res = b.read_bits_from_file(8)
print("read", res)
