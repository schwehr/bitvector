import unittest

import BitVector
from BitVector.BitVector import BitVectorIterator


class TestBitVectorGetSet(unittest.TestCase):
    def test_setbit(self):
        bv = BitVector.BitVector(bitstring="00000")

        # Error: invalid value
        with self.assertRaises(ValueError) as cm:
            bv._setbit(0, 2)
        self.assertEqual("incorrect value for a bit", str(cm.exception))

        # Error: index range error (positive and negative)
        with self.assertRaises(ValueError) as cm:
            bv._setbit(5, 1)
        self.assertEqual("index range error", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            bv._setbit(-6, 1)
        self.assertEqual("index range error", str(cm.exception))

        # Tuple index support
        bv._setbit((0,), 1)
        self.assertEqual(str(bv), "10000")

        # Negative index support
        bv._setbit(-1, 1)
        self.assertEqual(str(bv), "10001")

        # Set to same value (branch where (cv >> shift) & 1 == val)
        bv._setbit(0, 1)
        self.assertEqual(str(bv), "10001")

    def test_getbit_int(self):
        bv = BitVector.BitVector(bitstring="10110")

        # Error: index range error
        with self.assertRaises(ValueError) as cm:
            bv._getbit(5)
        self.assertEqual("index range error", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            bv._getbit(-6)
        self.assertEqual("index range error", str(cm.exception))

        # Positive and negative integer index access
        self.assertEqual(bv._getbit(0), 1)
        self.assertEqual(bv._getbit(1), 0)
        self.assertEqual(bv._getbit(-1), 0)
        self.assertEqual(bv._getbit(-2), 1)

    def test_getbit_slice_none(self):
        bv = BitVector.BitVector(bitstring="10110")

        # [:] both None
        self.assertEqual(str(bv[:]), "10110")

        # [:j] i is None
        self.assertEqual(str(bv[:3]), "101")
        with self.assertRaises(ValueError) as cm:
            bv[:10]
        self.assertEqual("illegal slice index values", str(cm.exception))

        self.assertEqual(str(bv[:-2]), "101")
        with self.assertRaises(ValueError) as cm:
            bv[:-10]
        self.assertEqual("illegal slice index values", str(cm.exception))

        # [i:] j is None
        self.assertEqual(str(bv[2:]), "110")
        with self.assertRaises(ValueError) as cm:
            bv[10:]
        self.assertEqual("illegal slice index values", str(cm.exception))

        self.assertEqual(str(bv[-3:]), "110")
        with self.assertRaises(ValueError) as cm:
            bv[-10:]
        self.assertEqual("illegal slice index values", str(cm.exception))

    def test_getbit_slice_errors(self):
        bv = BitVector.BitVector(bitstring="10110")

        # i >= 0, j >= 0, i > j
        with self.assertRaises(ValueError) as cm:
            bv[3:1]
        self.assertEqual("illegal slice index values", str(cm.exception))

        # i < 0, j >= 0, (len - abs(i)) > j
        with self.assertRaises(ValueError) as cm:
            bv[-1:2]
        self.assertEqual("illegal slice index values", str(cm.exception))

        # i >= 0, j < 0, len - abs(j) < i
        with self.assertRaises(ValueError) as cm:
            bv[4:-3]
        self.assertEqual("illegal slice index values", str(cm.exception))

    def test_getbit_slice_valid(self):
        bv = BitVector.BitVector(bitstring="10110")

        # i >= 0, j < 0 valid
        self.assertEqual(str(bv[1:-1]), "011")

        # Empty vector slice
        bv_empty = BitVector.BitVector(size=0)
        self.assertEqual(str(bv_empty[0:0]), "")

        # i == j
        self.assertEqual(str(bv[2:2]), "")

        # Standard range and negative range
        self.assertEqual(str(bv[1:4]), "011")
        self.assertEqual(str(bv[-4:-1]), "011")

    def test_bitvector_iterator(self):
        bv = BitVector.BitVector(bitstring="101")
        it = iter(bv)
        self.assertIsInstance(it, BitVectorIterator)
        self.assertIs(iter(it), it)
        self.assertEqual(list(it), [1, 0, 1])


if __name__ == "__main__":
    unittest.main()
