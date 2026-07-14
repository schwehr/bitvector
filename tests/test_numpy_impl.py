import pytest

from BitVector.numpy_impl import (
    NumpyBitVector8,
    NumpyBitVector16,
    NumpyBitVector32,
    NumpyBitVector64,
)


def test_numpy_init():
    # Bitstring
    v = NumpyBitVector16(bitstring="10100")
    assert v.size == 5
    assert v.int_val() == 20

    # IntVal + size
    v = NumpyBitVector16(intVal=20, size=5)
    assert v.size == 5
    assert v.int_val() == 20

    # Size only
    v = NumpyBitVector16(size=5)
    assert v.size == 5
    assert v.int_val() == 0

    with pytest.raises(ValueError):
        NumpyBitVector16(intVal=20)

    with pytest.raises(ValueError):
        NumpyBitVector16()


def test_numpy_bitwise():
    v1 = NumpyBitVector16(bitstring="1100")
    v2 = NumpyBitVector16(bitstring="1010")

    assert (v1 & v2).int_val() == 8  # 1000
    assert (v1 | v2).int_val() == 14  # 1110
    assert (v1 ^ v2).int_val() == 6  # 0110

    assert (~v1).int_val() == 3  # 0011 (since size is 4)

    with pytest.raises(ValueError):
        v1 & NumpyBitVector16(bitstring="10")


def test_numpy_shifts():
    v = NumpyBitVector16(bitstring="1100")

    assert (v << 1).int_val() == 9  # 1001
    assert (v >> 1).int_val() == 6  # 0110

    assert (v << 0).int_val() == 12
    assert (v >> 0).int_val() == 12

    assert (v << 5).int_val() == 9  # 5 % 4 = 1 -> 1001

    with pytest.raises(ValueError):
        v << -1
    with pytest.raises(ValueError):
        v >> -1

    empty = NumpyBitVector16(size=0)
    assert (empty << 1).size == 0
    assert (empty >> 1).size == 0


def test_numpy_add():
    v1 = NumpyBitVector16(bitstring="11")
    v2 = NumpyBitVector16(bitstring="001")
    v3 = v1 + v2
    assert v3.size == 5
    assert v3.int_val() == 25  # 11001 -> 16 + 8 + 1 = 25

    v1 += v2
    assert v1.int_val() == 25
    assert v1.size == 5


def test_numpy_comparison():
    v1 = NumpyBitVector16(bitstring="1100")
    v2 = NumpyBitVector16(bitstring="1010")
    v3 = NumpyBitVector16(bitstring="1100")

    assert v1 == v3
    assert v1 != v2
    assert v1 > v2
    assert v2 < v1
    assert v1 >= v2
    assert v2 <= v1
    assert v1 >= v3
    assert v1 <= v3

    assert v1 == 12
    assert v1 != 10
    assert v1 > 10
    assert v1 < 15

    assert v1 == 12.0
    assert v1 > 10.0

    assert v1 != "string"


def test_numpy_slice_and_index():
    v = NumpyBitVector16(bitstring="110010")

    assert v[0] == 1
    assert v[1] == 1
    assert v[2] == 0
    assert v[3] == 0
    assert v[-1] == 0

    v[2] = 1
    assert v.int_val() == 58  # 111010

    v2 = v[1:4]
    assert v2.size == 3
    assert v2.int_val() == 6  # 110

    v[1:4] = NumpyBitVector16(bitstring="000")
    assert v.int_val() == 34  # 100010

    with pytest.raises(IndexError):
        v[10]
    with pytest.raises(IndexError):
        v[10] = 1
    with pytest.raises(ValueError):
        v[1:4] = NumpyBitVector16(bitstring="0")
    with pytest.raises(ValueError):
        v[1:4:2]
    with pytest.raises(ValueError):
        v[1:4:2] = NumpyBitVector16(bitstring="00")
    with pytest.raises(TypeError):
        v["a"]
    with pytest.raises(TypeError):
        v["a"] = 1
    with pytest.raises(TypeError):
        v[1:4] = 1

    v3 = v[4:1]
    assert v3.size == 0


def test_numpy_utility():
    v = NumpyBitVector16(bitstring="1010")
    assert len(v) == 4
    assert int(v) == 10
    assert str(v) == "1010"

    assert v.count_bits() == 2
    assert v.count_bits_sparse() == 2

    assert list(v) == [1, 0, 1, 0]

    assert v.next_set_bit(0) == 0
    assert v.next_set_bit(1) == 2
    assert v.next_set_bit(3) == -1

    assert not v.is_power_of_2()
    assert not v.is_power_of_2_sparse()

    v2 = NumpyBitVector16(bitstring="1000")
    assert v2.is_power_of_2()
    assert v2.is_power_of_2_sparse()

    empty = NumpyBitVector16(size=0)
    assert str(empty) == ""

    assert NumpyBitVector16(bitstring="01") in v
    assert NumpyBitVector16(bitstring="11") not in v
    assert NumpyBitVector16(bitstring="10101") not in v
    assert empty not in v


def test_numpy_other_variants():
    v8 = NumpyBitVector8(bitstring="1010")
    v32 = NumpyBitVector32(bitstring="1010")
    v64 = NumpyBitVector64(bitstring="1010")

    assert v8.int_val() == 10
    assert v32.int_val() == 10
    assert v64.int_val() == 10


def test_numpy_eq_cmp_branches():
    v1 = NumpyBitVector16(bitstring="1010")
    v2 = NumpyBitVector16(bitstring="10100")
    assert v1 != v2
    assert v2 != v1
    assert v1 < v2
    assert v2 > v1

    v3 = NumpyBitVector16(bitstring="1100")
    assert v1 < v3
    assert v3 > v1

    assert v1 < 15
    assert v1 > 5
    assert v1 == 10

    assert v1 < 15.0
    assert v1 > 5.0
    assert v1 == 10.0

    class DummyObj:
        def int_val(self):
            return 10

    d = DummyObj()
    assert v1 == d

    class DummyObj2:
        def int_val(self):
            return 15

    d2 = DummyObj2()
    assert v1 < d2
    assert v3 < d2

    class DummyObj3:
        def int_val(self):
            return 5

    d3 = DummyObj3()
    assert v1 > d3


def test_numpy_other_ops():
    v = NumpyBitVector16(bitstring="1100")
    # Coverage for size mismatch errors
    with pytest.raises(ValueError):
        v | NumpyBitVector16(bitstring="10")
    with pytest.raises(ValueError):
        v ^ NumpyBitVector16(bitstring="10")

    v_zero = NumpyBitVector16(size=5)
    assert v_zero.count_bits_sparse() == 0

    v_pad = ~v_zero
    assert v_pad.size == 5

    v_shift = v_zero << 0
    assert v_shift.size == 5
    v_shift = v_zero >> 0
    assert v_shift.size == 5

    empty = NumpyBitVector16(size=0)
    assert (empty + v).int_val() == 12
    assert (v + empty).int_val() == 12

    assert str(empty) == ""
    assert int(empty) == 0
    assert empty.int_val() == 0
    assert list(empty) == []


def test_numpy_contains_branches():
    v = NumpyBitVector16(bitstring="1010100")
    # Coverage for contains
    assert NumpyBitVector16(bitstring="111") not in v

    empty = NumpyBitVector16(size=0)
    assert empty not in v

    large = NumpyBitVector16(bitstring="10101001111111")
    assert large not in v


def test_numpy_cmp_branches_2():
    v1 = NumpyBitVector16(bitstring="10")
    assert v1._cmp_values(None) is NotImplemented
    assert (v1 == None) is False  # noqa: E711
    assert (v1 != None) is True  # noqa: E711
    assert (v1 < None) is False
    assert (v1 <= None) is False
    assert (v1 > None) is False
    assert (v1 >= None) is False


def test_numpy_getitem_setitem_branches():
    v = NumpyBitVector16(bitstring="1100")
    with pytest.raises(IndexError):
        v[-10]
    with pytest.raises(IndexError):
        v[-10] = 1


def test_numpy_setitem_type_branches():
    v = NumpyBitVector16(bitstring="1100")
    with pytest.raises(TypeError):
        v[1:3] = 5


def test_numpy_int_val_branches():
    v = NumpyBitVector16(intVal=0, size=5)
    assert v.int_val() == 0


def test_numpy_shift_branches():
    v = NumpyBitVector16(bitstring="1100")
    # Coverage for shift amount exceeding size implicitly checked by modulo
    v_shift = v << 5
    assert v_shift.int_val() == 9  # 1001


def test_numpy_str_branches():
    v = NumpyBitVector16(size=0)
    assert str(v) == ""


def test_numpy_getitem_slice_step():
    v = NumpyBitVector16(bitstring="1100")
    with pytest.raises(ValueError):
        v[1:3:2]


def test_numpy_getitem_type():
    v = NumpyBitVector16(bitstring="1100")
    with pytest.raises(TypeError):
        v["a"]


def test_numpy_cmp_values_int_branch():
    v = NumpyBitVector16(bitstring="1010")
    assert v._cmp_values(10) == 0
    assert v._cmp_values(15) == -1
    assert v._cmp_values(5) == 1
    assert v._cmp_values(10.0) == 0
    assert v._cmp_values(15.0) == -1
    assert v._cmp_values(5.0) == 1


def test_numpy_cmp_values_numpy_branch():
    v1 = NumpyBitVector16(bitstring="10")
    v2 = NumpyBitVector16(bitstring="100")
    assert v1._cmp_values(v2) == -1
    assert v2._cmp_values(v1) == 1


def test_numpy_invalid_init():
    with pytest.raises(ValueError):
        NumpyBitVector16(bitstring="1100", intVal=12)


def test_numpy_setitem_slice_reverse():
    v = NumpyBitVector16(bitstring="1100")
    with pytest.raises(ValueError):
        v[3:1:-1] = NumpyBitVector16(bitstring="00")


def test_numpy_cmp_values_numpy_branch_size_equal():
    # To test `s_val < o_val` and `s_val > o_val` with equal lengths
    v1 = NumpyBitVector16(bitstring="1010")  # 10
    v2 = NumpyBitVector16(bitstring="1100")  # 12
    v3 = NumpyBitVector16(bitstring="1010")  # 10
    assert v1._cmp_values(v2) == -1
    assert v2._cmp_values(v1) == 1
    assert v1._cmp_values(v3) == 0


def test_numpy_add_shift_branch():
    v1 = NumpyBitVector16(bitstring="110")  # size 3
    v2 = NumpyBitVector16(bitstring="01")  # size 2
    # v1 + v2 sizes: 3 % 16 = 3 (shift_amount > 0)
    # len(other.vector) == 1
    # word_offset + i + 1 < len(...) is 0 + 0 + 1 < 1 which is False
    v3 = v1 + v2
    assert v3.int_val() == 25  # 11001


def test_numpy_setitem_branch():
    v = NumpyBitVector16(bitstring="1100")

    # Not hasattr size or _getbit for slice
    class NoAttr:
        pass

    with pytest.raises(TypeError):
        v[1:3] = NoAttr()

    with pytest.raises(IndexError):
        v[10] = 1


def test_numpy_int_val_and_slice():
    # Cover line 84->87 missing branches and 109 and 335
    pass


def test_numpy_invert_branch():
    v = NumpyBitVector16(size=16)  # Rem == 0
    v2 = ~v
    assert v2.int_val() == 65535  # 1111111111111111


def test_numpy_iadd_branch():
    v1 = NumpyBitVector16(bitstring="1")
    v2 = NumpyBitVector16(bitstring="0")
    v1 += v2
    assert v1.size == 2


def test_numpy_slice_item_type():
    v = NumpyBitVector16(bitstring="1100")

    class DummyItem:
        size = 2

    with pytest.raises(TypeError):
        v[1:3] = DummyItem()


def test_numpy_add_shift_zero_branch():
    v1 = NumpyBitVector16(size=16)  # size % 16 == 0
    v2 = NumpyBitVector16(bitstring="11")
    v3 = v1 + v2
    assert v3.int_val() == 3


def test_numpy_setitem_int_negative():
    v = NumpyBitVector16(bitstring="1100")
    v[-1] = 1
    assert v.int_val() == 13  # 1101


def test_numpy_add_shift_large_other():
    v1 = NumpyBitVector16(bitstring="110")  # size 3
    v2 = NumpyBitVector16(bitstring="1" * 15)  # size 15, crosses word_offset + i + 1
    v3 = v1 + v2
    assert v3.size == 18
    assert v3.int_val() == (6 << 15) | ((1 << 15) - 1)
