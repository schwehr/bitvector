import numpy as np

from BitVector.BitVectorNumPy import BitVectorNumPy


def test_numpy_init():
    bv = BitVectorNumPy(size=128)
    assert bv.size == 128
    assert len(bv.vector) == 2
    assert getattr(bv.vector, "dtype", None) == np.uint64
    bv[0] = 1
    assert bv[0] == 1
    assert bv[1] == 0


def test_numpy_operations():
    bv1 = BitVectorNumPy(bitstring="1010")
    bv2 = BitVectorNumPy(bitstring="0101")

    assert str(bv1 ^ bv2) == "1111"
    assert str(bv1 & bv2) == "0000"
    assert str(bv1 | bv2) == "1111"
    assert str(~bv1) == "0101"

    bv3 = bv1 + bv2
    assert str(bv3) == "10100101"

    bv1 += bv2
    assert str(bv1) == "10100101"


def test_numpy_count_bits():
    bv1 = BitVectorNumPy(bitstring="1011")
    assert bv1.count_bits() == 3
    assert bv1.count_bits_sparse() == 3


def test_numpy_shift():
    bv1 = BitVectorNumPy(bitstring="1011")
    bv1.shift_left_by_one()
    assert str(bv1) == "0110"

    bv2 = BitVectorNumPy(bitstring="1011")
    bv2.shift_right_by_one()
    assert str(bv2) == "0101"
