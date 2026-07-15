from BitVector.BitVectorNumPy import BitVectorNumPy
bv = BitVectorNumPy(size=128)
bv[0] = 1
bv[127] = 1
bv[64] = 1
print(bv.count_bits())
print(bv.count_bits_sparse())
