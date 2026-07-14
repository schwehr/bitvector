import pytest

from BitVector import BitVector
from BitVector.numpy_impl import (
    NumpyBitVector8,
    NumpyBitVector16,
    NumpyBitVector32,
    NumpyBitVector64,
)


@pytest.fixture
def test_string():
    return "01010111" * 128


@pytest.fixture
def class_types():
    return [
        BitVector,
        NumpyBitVector8,
        NumpyBitVector16,
        NumpyBitVector32,
        NumpyBitVector64,
    ]


@pytest.mark.parametrize(
    "bv_class",
    [BitVector, NumpyBitVector8, NumpyBitVector16, NumpyBitVector32, NumpyBitVector64],
)
def test_bench_init(benchmark, bv_class, test_string):
    def init_test():
        return bv_class(bitstring=test_string)

    benchmark(init_test)


@pytest.mark.parametrize(
    "bv_class",
    [BitVector, NumpyBitVector8, NumpyBitVector16, NumpyBitVector32, NumpyBitVector64],
)
def test_bench_and(benchmark, bv_class, test_string):
    v1 = bv_class(bitstring=test_string)
    v2 = bv_class(bitstring="10101000" * 128)

    def and_test():
        return v1 & v2

    benchmark(and_test)


@pytest.mark.parametrize(
    "bv_class",
    [BitVector, NumpyBitVector8, NumpyBitVector16, NumpyBitVector32, NumpyBitVector64],
)
def test_bench_or(benchmark, bv_class, test_string):
    v1 = bv_class(bitstring=test_string)
    v2 = bv_class(bitstring="10101000" * 128)

    def or_test():
        return v1 | v2

    benchmark(or_test)


@pytest.mark.parametrize(
    "bv_class",
    [BitVector, NumpyBitVector8, NumpyBitVector16, NumpyBitVector32, NumpyBitVector64],
)
def test_bench_count_bits(benchmark, bv_class, test_string):
    v = bv_class(bitstring=test_string)

    def count_bits_test():
        return v.count_bits()

    benchmark(count_bits_test)


@pytest.mark.parametrize(
    "bv_class",
    [BitVector, NumpyBitVector8, NumpyBitVector16, NumpyBitVector32, NumpyBitVector64],
)
def test_bench_add(benchmark, bv_class, test_string):
    v1 = bv_class(bitstring=test_string)
    v2 = bv_class(bitstring=test_string)

    def add_test():
        return v1 + v2

    benchmark(add_test)
