import unittest

import BitVector


class TestBitVectorOperations(unittest.TestCase):
    def test_divide_into_two(self):
        # Error: odd number of bits
        bv_odd = BitVector.BitVector(bitstring="101")
        with self.assertRaises(ValueError) as cm:
            bv_odd.divide_into_two()
        self.assertEqual("must have even num bits", str(cm.exception))

        # Normal division
        bv = BitVector.BitVector(bitstring="11001011")
        left, right = bv.divide_into_two()
        self.assertEqual(str(left), "1100")
        self.assertEqual(str(right), "1011")

        # Empty vector division (0 is even)
        bv_empty = BitVector.BitVector(size=0)
        left_empty, right_empty = bv_empty.divide_into_two()
        self.assertEqual(str(left_empty), "")
        self.assertEqual(str(right_empty), "")

    def test_permute(self):
        # Error: bad permutation index
        bv = BitVector.BitVector(bitstring="1010")
        with self.assertRaises(ValueError) as cm:
            bv.permute([0, 1, 2, 4])
        self.assertEqual("Bad permutation index", str(cm.exception))

        # Normal permutation
        bv2 = BitVector.BitVector(bitstring="1011")
        permuted = bv2.permute([3, 2, 1, 0])
        self.assertEqual(str(permuted), "1101")

        # Permutation to different size
        perm_extended = bv2.permute([0, 1, 0, 1, 2, 3])
        self.assertEqual(str(perm_extended), "101011")

    def test_unpermute(self):
        bv = BitVector.BitVector(bitstring="1010")

        # Error: bad permutation index
        with self.assertRaises(ValueError) as cm:
            bv.unpermute([0, 1, 2, 4])
        self.assertEqual("Bad permutation index", str(cm.exception))

        # Error: bad size for permute list
        with self.assertRaises(ValueError) as cm:
            bv.unpermute([0, 1, 2])
        self.assertEqual("Bad size for permute list", str(cm.exception))

        # Normal unpermute
        bv_orig = BitVector.BitVector(bitstring="11001010")
        p_list = [7, 6, 5, 4, 3, 2, 1, 0]
        permuted = bv_orig.permute(p_list)
        unpermuted = permuted.unpermute(p_list)
        self.assertEqual(str(unpermuted), str(bv_orig))


if __name__ == "__main__":
    unittest.main()
