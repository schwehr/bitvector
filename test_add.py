from BitVector import BitVector

def new_add(self, other):
    new_bv = self.__class__(size=self.size + other.size)
    new_bv.vector[:len(self.vector)] = self.vector

    # same loop as in BitVector.__add__
    i = self.size
    for bit in other:
        if bit:
            new_bv.vector[i // 16] |= 1 << (i & 15)
        i += 1
    return new_bv

b1 = BitVector(bitstring="1010")
b2 = BitVector(bitstring="0111")
b3 = b1 + b2
print("original add:", b3)

b4 = new_add(b1, b2)
print("new add:", b4)
