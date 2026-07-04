import unittest

import BitVector


class TestBitVectorDunder(unittest.TestCase):
    def test_xor(self):
        bv_short = BitVector.BitVector(bitstring="10")
        bv_long = BitVector.BitVector(bitstring="1100")
        self.assertEqual(str(bv_short ^ bv_long), "1110")
        self.assertEqual(str(bv_long ^ bv_short), "1110")

        bv1 = BitVector.BitVector(bitstring="1010")
        bv2 = BitVector.BitVector(bitstring="1100")
        self.assertEqual(str(bv1 ^ bv2), "0110")

    def test_and(self):
        bv_short = BitVector.BitVector(bitstring="11")
        bv_long = BitVector.BitVector(bitstring="0110")
        self.assertEqual(str(bv_short & bv_long), "0010")
        self.assertEqual(str(bv_long & bv_short), "0010")

        bv1 = BitVector.BitVector(bitstring="1010")
        bv2 = BitVector.BitVector(bitstring="1100")
        self.assertEqual(str(bv1 & bv2), "1000")

    def test_add(self):
        bv1 = BitVector.BitVector(bitstring="101")
        bv2 = BitVector.BitVector(bitstring="010")
        self.assertEqual(str(bv1 + bv2), "101010")

        bv_empty = BitVector.BitVector(size=0)
        self.assertEqual(str(bv_empty + bv1), "101")
        self.assertEqual(str(bv1 + bv_empty), "101")
        self.assertEqual(str(bv_empty + bv_empty), "")

        # Test __add__ when self.vector is a list (lines 500-501)
        bv_list = BitVector.BitVector(bitstring="1100")
        bv_list.vector = list(bv_list.vector)
        self.assertEqual(str(bv_list + bv2), "1100010")

        # Test __add__ when self.vector is neither array.array nor list (lines 502-504)
        bv_tuple = BitVector.BitVector(bitstring="1001")
        bv_tuple.vector = tuple(bv_tuple.vector)  # ty: ignore[invalid-assignment]
        self.assertEqual(str(bv_tuple + bv2), "1001010")

    def test_iadd(self):
        bv1 = BitVector.BitVector(bitstring="101")
        bv2 = BitVector.BitVector(bitstring="010")
        bv1 += bv2
        self.assertEqual(str(bv1), "101010")

        # Test __iadd__ with non-BitVector argument (line 519)
        with self.assertRaises(TypeError) as cm:
            bv1 += "010"  # ty: ignore[unsupported-operator]
        self.assertIn("Can only join two BitVector objects, not", str(cm.exception))

    def test_or(self):
        bv_short = BitVector.BitVector(bitstring="10")
        bv_long = BitVector.BitVector(bitstring="0100")
        self.assertEqual(str(bv_short | bv_long), "0110")
        self.assertEqual(str(bv_long | bv_short), "0110")

        bv1 = BitVector.BitVector(bitstring="1010")
        bv2 = BitVector.BitVector(bitstring="0101")
        self.assertEqual(str(bv1 | bv2), "1111")

    def test_invert(self):
        bv = BitVector.BitVector(bitstring="10100111")
        self.assertEqual(str(~bv), "01011000")

        bv_empty = BitVector.BitVector(size=0)
        self.assertEqual(str(~bv_empty), "")

    def test_lshift(self):
        bv = BitVector.BitVector(bitstring="1000")
        self.assertEqual(str(bv << 1), "0001")
        self.assertEqual(str(bv << 2), "0100")
        self.assertEqual(str(bv << 0), "0100")
        self.assertEqual(str(bv << -1), "0010")

        bv_empty = BitVector.BitVector(size=0)
        with self.assertRaises(ValueError) as cm:
            _ = bv_empty << 1
        self.assertIn("Circular shift of an empty vector", str(cm.exception))

    def test_rshift(self):
        bv = BitVector.BitVector(bitstring="1000")
        self.assertEqual(str(bv >> 1), "0100")
        self.assertEqual(str(bv >> 2), "0001")
        self.assertEqual(str(bv >> 0), "0001")
        self.assertEqual(str(bv >> -1), "0010")

        bv_empty = BitVector.BitVector(size=0)
        with self.assertRaises(ValueError) as cm:
            _ = bv_empty >> 1
        self.assertIn("Circular shift of an empty vector", str(cm.exception))

    def test_setitem(self):
        # Index assignment
        bv = BitVector.BitVector(bitstring="000")
        bv[1] = 1
        bv[-1] = 1
        self.assertEqual(str(bv), "011")
        bv[0] = 0
        self.assertEqual(str(bv), "011")

        # Slice assignment error: item not a BitVector
        with self.assertRaises(TypeError) as cm:
            bv[0:1] = [1]
        self.assertIn(
            "For slice assignment, the right hand side must be a BitVector",
            str(cm.exception),
        )

        # Slice assignment: start is None and stop is None
        bv2 = BitVector.BitVector(bitstring="1010")
        bv2[:] = BitVector.BitVector(bitstring="0101")
        self.assertEqual(str(bv2), "1010")

        # Slice assignment: start is None, stop >= 0
        bv3 = BitVector.BitVector(bitstring="0000")
        with self.assertRaises(ValueError) as cm:
            bv3[:2] = BitVector.BitVector(size=1)
        self.assertIn("incompatible lengths for slice assignment 1", str(cm.exception))
        bv3[:2] = BitVector.BitVector(bitstring="11")
        self.assertEqual(str(bv3), "1100")

        # Slice assignment: start is None, stop < 0
        bv4 = BitVector.BitVector(bitstring="0000")
        with self.assertRaises(ValueError) as cm:
            bv4[:-1] = BitVector.BitVector(size=2)
        self.assertIn("incompatible lengths for slice assignment 2", str(cm.exception))
        bv4[:-1] = BitVector.BitVector(bitstring="111")
        self.assertEqual(str(bv4), "1110")

        # Slice assignment: stop is None, start >= 0
        bv5 = BitVector.BitVector(bitstring="0000")
        with self.assertRaises(ValueError) as cm:
            bv5[2:] = BitVector.BitVector(size=1)
        self.assertIn("incompatible lengths for slice assignment 3", str(cm.exception))
        bv5[2:] = BitVector.BitVector(bitstring="11")
        self.assertEqual(str(bv5), "0011")

        # Slice assignment: stop is None, start < 0
        bv6 = BitVector.BitVector(bitstring="0000")
        with self.assertRaises(ValueError) as cm:
            bv6[-2:] = BitVector.BitVector(size=1)
        self.assertIn("incompatible lengths for slice assignment 4", str(cm.exception))
        bv6[-2:] = BitVector.BitVector(bitstring="11")
        self.assertEqual(str(bv6), "0011")

        # Slice assignment: start >= 0 and stop < 0
        bv7 = BitVector.BitVector(bitstring="000000")
        with self.assertRaises(ValueError) as cm:
            bv7[1:-1] = BitVector.BitVector(size=2)
        self.assertIn("incompatible lengths for slice assignment 5", str(cm.exception))
        bv7[1:-1] = BitVector.BitVector(bitstring="1111")
        self.assertEqual(str(bv7), "011110")

        # Slice assignment: start < 0 and stop >= 0
        bv8 = BitVector.BitVector(bitstring="0000000000")
        with self.assertRaises(ValueError) as cm:
            bv8[-8:6] = BitVector.BitVector(size=3)
        self.assertIn("incompatible lengths for slice assignment 6", str(cm.exception))
        bv8[-2:6] = BitVector.BitVector(size=2)

        # Slice assignment: start >= 0 and stop >= 0 (normal slice)
        bv9 = BitVector.BitVector(bitstring="0000")
        with self.assertRaises(ValueError) as cm:
            bv9[1:3] = BitVector.BitVector(size=1)
        self.assertIn("incompatible lengths for slice assignment 7", str(cm.exception))
        bv9[1:3] = BitVector.BitVector(bitstring="11")
        self.assertEqual(str(bv9), "0110")

    def test_str(self):
        self.assertEqual(str(BitVector.BitVector(size=0)), "")
        self.assertEqual(str(BitVector.BitVector(bitstring="10110")), "10110")

    def test_eq(self):
        bv1 = BitVector.BitVector(bitstring="1010")
        self.assertFalse(bv1 == BitVector.BitVector(bitstring="10100"))
        self.assertFalse(bv1 == BitVector.BitVector(bitstring="1011"))
        self.assertTrue(bv1 == BitVector.BitVector(bitstring="1010"))
        self.assertTrue(BitVector.BitVector(size=0) == BitVector.BitVector(size=0))

    def test_ne(self):
        bv1 = BitVector.BitVector(bitstring="1010")
        self.assertFalse(bv1 != BitVector.BitVector(bitstring="1010"))
        self.assertTrue(bv1 != BitVector.BitVector(bitstring="0101"))

    def test_lt(self):
        bv_small = BitVector.BitVector(intVal=3, size=8)
        bv_large = BitVector.BitVector(intVal=5, size=8)
        self.assertTrue(bv_small < bv_large)
        self.assertFalse(bv_large < bv_small)
        self.assertFalse(bv_small < BitVector.BitVector(intVal=3, size=8))

    def test_le(self):
        bv_small = BitVector.BitVector(intVal=3, size=8)
        bv_large = BitVector.BitVector(intVal=5, size=8)
        self.assertTrue(bv_small <= bv_large)
        self.assertTrue(bv_small <= BitVector.BitVector(intVal=3, size=8))
        self.assertFalse(bv_large <= bv_small)

    def test_gt(self):
        bv_small = BitVector.BitVector(intVal=3, size=8)
        bv_large = BitVector.BitVector(intVal=5, size=8)
        self.assertTrue(bv_large > bv_small)
        self.assertFalse(bv_small > bv_large)
        self.assertFalse(bv_small > BitVector.BitVector(intVal=3, size=8))

    def test_ge(self):
        bv_small = BitVector.BitVector(intVal=3, size=8)
        bv_large = BitVector.BitVector(intVal=5, size=8)
        self.assertTrue(bv_large >= bv_small)
        self.assertTrue(bv_small >= BitVector.BitVector(intVal=3, size=8))
        self.assertFalse(bv_small >= bv_large)

    def test_contains(self):
        bv_empty = BitVector.BitVector(size=0)
        bv = BitVector.BitVector(bitstring="110100")

        with self.assertRaises(ValueError) as cm:
            _ = BitVector.BitVector(bitstring="1") in bv_empty
        self.assertIn("First arg bitvec has no bits", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            _ = BitVector.BitVector(bitstring="1101000") in bv
        self.assertIn("First arg bitvec too short", str(cm.exception))

        self.assertTrue(BitVector.BitVector(bitstring="010") in bv)
        self.assertFalse(BitVector.BitVector(bitstring="111") in bv)


if __name__ == "__main__":
    unittest.main()
