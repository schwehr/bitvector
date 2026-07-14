import operator

import pytest

from BitVector import BitVector, MmapBitVector


def test_mmap_initialization():
    mbv = MmapBitVector(size=100)
    assert len(mbv) == 100
    assert mbv.count_bits() == 0

    mbv[10] = 1
    assert mbv[10] == 1
    assert mbv.count_bits() == 1


def test_mmap_bitwise_ops():
    m1 = MmapBitVector(size=100)
    m2 = MmapBitVector(size=100)
    m1[50] = 1
    m2[50] = 1
    m2[60] = 1

    # AND
    m3 = m1 & m2
    assert isinstance(m3, MmapBitVector)
    assert m3.count_bits() == 1
    assert m3[50] == 1

    # OR
    m4 = m1 | m2
    assert isinstance(m4, MmapBitVector)
    assert m4.count_bits() == 2
    assert m4[60] == 1


def test_mmap_extend_pad():
    m1 = MmapBitVector(size=100)
    m1[99] = 1

    m2 = MmapBitVector(size=50)
    m2[0] = 1

    m3 = m1 + m2
    assert isinstance(m3, MmapBitVector)
    assert len(m3) == 150
    assert m3[99] == 1
    assert m3[100] == 1


@pytest.fixture(params=[2**i for i in range(15, 23)])
def bv_size(request):
    return request.param


def test_bench_init_bitvector(benchmark, bv_size):
    benchmark(BitVector, size=bv_size)


def test_bench_init_mmap(benchmark, bv_size):
    benchmark(MmapBitVector, size=bv_size)


def test_bench_and_bitvector(benchmark, bv_size):
    bv1 = BitVector(size=bv_size)
    bv2 = BitVector(size=bv_size)
    benchmark(operator.and_, bv1, bv2)


def test_bench_and_mmap(benchmark, bv_size):
    m1 = MmapBitVector(size=bv_size)
    m2 = MmapBitVector(size=bv_size)
    benchmark(operator.and_, m1, m2)


def test_bench_invert_bitvector(benchmark, bv_size):
    bv1 = BitVector(size=bv_size)
    benchmark(operator.invert, bv1)


def test_bench_invert_mmap(benchmark, bv_size):
    m1 = MmapBitVector(size=bv_size)
    benchmark(operator.invert, m1)
