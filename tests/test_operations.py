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

    def test_circular_rot_left(self):
        # Small vector (size <= 16)
        bv = BitVector.BitVector(bitstring="1000")
        bv.circular_rot_left()
        self.assertEqual(str(bv), "0001")

        # Large vector (size > 16)
        bv_long = BitVector.BitVector(bitstring="10000000000000000001")
        bv_long.circular_rot_left()
        self.assertEqual(str(bv_long), "00000000000000000011")

    def test_circular_rot_right(self):
        # Small vector (size <= 16)
        bv = BitVector.BitVector(bitstring="0001")
        bv.circular_rot_right()
        self.assertEqual(str(bv), "1000")

        # Large vector (size > 16)
        bv_long = BitVector.BitVector(bitstring="10000000000000000001")
        bv_long.circular_rot_right()
        self.assertEqual(str(bv_long), "11000000000000000000")

    def test_shift_left_by_one(self):
        # Small vector
        bv = BitVector.BitVector(bitstring="1011")
        bv.shift_left_by_one()
        self.assertEqual(str(bv), "0110")

        # Large vector (size > 16)
        bv_long = BitVector.BitVector(bitstring="1" + "0" * 18 + "1")
        bv_long.shift_left_by_one()
        self.assertEqual(str(bv_long), "0" * 18 + "10")

    def test_shift_right_by_one(self):
        # Small vector
        bv = BitVector.BitVector(bitstring="1101")
        bv.shift_right_by_one()
        self.assertEqual(str(bv), "0110")

        # Large vector (size > 16)
        bv_long = BitVector.BitVector(bitstring="1" + "0" * 18 + "1")
        bv_long.shift_right_by_one()
        self.assertEqual(str(bv_long), "01" + "0" * 18)

    def test_shift_left(self):
        bv = BitVector.BitVector(bitstring="101101")
        res = bv.shift_left(2)
        self.assertEqual(str(bv), "110100")
        self.assertIs(res, bv)

        bv.shift_left(0)
        self.assertEqual(str(bv), "110100")

    def test_shift_right(self):
        bv = BitVector.BitVector(bitstring="101101")
        res = bv.shift_right(2)
        self.assertEqual(str(bv), "001011")
        self.assertIs(res, bv)

        bv.shift_right(0)
        self.assertEqual(str(bv), "001011")

    def test_pad_from_left(self):
        bv = BitVector.BitVector(bitstring="101")
        bv.pad_from_left(2)
        self.assertEqual(str(bv), "00101")
        self.assertEqual(bv.size, 5)

        bv.pad_from_left(0)
        self.assertEqual(str(bv), "00101")

    def test_pad_from_right(self):
        bv = BitVector.BitVector(bitstring="101")
        bv.pad_from_right(2)
        self.assertEqual(str(bv), "10100")
        self.assertEqual(bv.size, 5)

        bv.pad_from_right(0)
        self.assertEqual(str(bv), "10100")

    def test_reset(self):
        bv = BitVector.BitVector(bitstring="101")
        with self.assertRaises(ValueError) as cm:
            bv.reset(2)
        self.assertEqual("Incorrect reset argument", str(cm.exception))

        res = bv.reset(1)
        self.assertEqual(str(bv), "111")
        self.assertIs(res, bv)

        bv.reset(0)
        self.assertEqual(str(bv), "000")

    def test_count_bits(self):
        bv = BitVector.BitVector(bitstring="100111")
        self.assertEqual(bv.count_bits(), 4)

        bv_empty = BitVector.BitVector(size=0)
        self.assertEqual(bv_empty.count_bits(), 0)

    def test_set_value(self):
        bv = BitVector.BitVector(intVal=7, size=16)
        bv.set_value(intVal=45)
        self.assertEqual(str(bv), "101101")

        bv.set_value(bitstring="1100")
        self.assertEqual(str(bv), "1100")


if __name__ == "__main__":
    unittest.main()
