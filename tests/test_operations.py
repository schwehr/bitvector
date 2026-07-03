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

    def test_count_bits_sparse(self):
        bv_empty = BitVector.BitVector(size=0)
        self.assertEqual(bv_empty.count_bits_sparse(), 0)

        bv = BitVector.BitVector(bitstring="100111" + "0" * 20)
        self.assertEqual(bv.count_bits_sparse(), 4)

    def test_jaccard_similarity(self):
        # Error: both zero vectors
        bv_zero1 = BitVector.BitVector(bitstring="000")
        bv_zero2 = BitVector.BitVector(bitstring="000")
        with self.assertRaises(AssertionError) as cm:
            bv_zero1.jaccard_similarity(bv_zero2)
        self.assertIn("Jaccard called on two zero vectors", str(cm.exception))

        # Error: unequal length
        with self.assertRaises(AssertionError) as cm:
            BitVector.BitVector(bitstring="1").jaccard_similarity(
                BitVector.BitVector(bitstring="10")
            )
        self.assertIn("must be of equal length", str(cm.exception))

        # Normal similarity
        bv1 = BitVector.BitVector(bitstring="11111111")
        bv2 = BitVector.BitVector(bitstring="00101011")
        self.assertAlmostEqual(bv1.jaccard_similarity(bv2), 0.5)

    def test_jaccard_distance(self):
        # Error: unequal length
        with self.assertRaises(AssertionError) as cm:
            BitVector.BitVector(bitstring="1").jaccard_distance(
                BitVector.BitVector(bitstring="10")
            )
        self.assertIn("vectors of unequal length", str(cm.exception))

        # Normal distance
        bv1 = BitVector.BitVector(bitstring="11111111")
        bv2 = BitVector.BitVector(bitstring="00101011")
        self.assertAlmostEqual(bv1.jaccard_distance(bv2), 0.5)

    def test_hamming_distance(self):
        # Error: unequal length
        with self.assertRaises(AssertionError) as cm:
            BitVector.BitVector(bitstring="1").hamming_distance(
                BitVector.BitVector(bitstring="10")
            )
        self.assertIn("vectors of unequal length", str(cm.exception))

        # Normal hamming distance
        bv1 = BitVector.BitVector(bitstring="11111111")
        bv2 = BitVector.BitVector(bitstring="00101011")
        self.assertEqual(bv1.hamming_distance(bv2), 4)

    def test_next_set_bit(self):
        # Error: negative index
        bv = BitVector.BitVector(bitstring="00000000000001")
        with self.assertRaises(AssertionError) as cm:
            bv.next_set_bit(-1)
        self.assertIn("from_index must be nonnegative", str(cm.exception))

        # Found bit
        self.assertEqual(bv.next_set_bit(5), 13)

        # Not found bit
        bv_zeros = BitVector.BitVector(bitstring="0" * 20)
        self.assertEqual(bv_zeros.next_set_bit(0), -1)

        # Start from non-zero block, then no more bits found
        bv_short = BitVector.BitVector(bitstring="0100000000000000")
        self.assertEqual(bv_short.next_set_bit(2), -1)

    def test_rank_of_bit_set_at_index(self):
        # Error: arg bit not set
        bv = BitVector.BitVector(bitstring="01010101011100")
        with self.assertRaises(AssertionError) as cm:
            bv.rank_of_bit_set_at_index(0)
        self.assertIn("the arg bit not set", str(cm.exception))

        # Normal rank
        self.assertEqual(bv.rank_of_bit_set_at_index(10), 6)

    def test_is_power_of_2(self):
        # Zero is false
        self.assertFalse(BitVector.BitVector(bitstring="0000").is_power_of_2())

        # True cases and alias
        self.assertTrue(BitVector.BitVector(bitstring="0010").is_power_of_2())
        self.assertTrue(BitVector.BitVector(bitstring="0010").isPowerOf2())

        # False case
        self.assertFalse(BitVector.BitVector(bitstring="0011").is_power_of_2())

    def test_is_power_of_2_sparse(self):
        self.assertTrue(BitVector.BitVector(bitstring="0010").is_power_of_2_sparse())
        self.assertTrue(BitVector.BitVector(bitstring="0010").isPowerOf2_sparse())
        self.assertFalse(BitVector.BitVector(bitstring="0011").is_power_of_2_sparse())

    def test_reverse(self):
        bv = BitVector.BitVector(bitstring="0001100000000000001")
        self.assertEqual(str(bv.reverse()), "1000000000000011000")

        bv_empty = BitVector.BitVector(size=0)
        self.assertEqual(str(bv_empty.reverse()), "")

    def test_gcd(self):
        bv1 = BitVector.BitVector(bitstring="01100110")  # 102
        bv2 = BitVector.BitVector(bitstring="011010")  # 26
        self.assertEqual(int(bv1.gcd(bv2)), 2)
        self.assertEqual(int(bv2.gcd(bv1)), 2)

    def test_multiplicative_inverse(self):
        bv_mod = BitVector.BitVector(intVal=32)
        bv_has_mi = BitVector.BitVector(intVal=17)
        res = bv_has_mi.multiplicative_inverse(bv_mod)
        self.assertIsNotNone(res)
        self.assertEqual(int(res), 17)

        bv_no_mi = BitVector.BitVector(intVal=2)
        res_none = bv_no_mi.multiplicative_inverse(bv_mod)
        self.assertIsNone(res_none)

    def test_gf_multiply(self):
        a = BitVector.BitVector(bitstring="0110001")
        b = BitVector.BitVector(bitstring="0110")
        c = a.gf_multiply(b)
        self.assertEqual(str(c), "00010100110")

        # Zero multiply
        b_zero = BitVector.BitVector(bitstring="0000")
        c_zero = a.gf_multiply(b_zero)
        self.assertEqual(int(c_zero), 0)

    def test_gf_divide_by_modulus(self):
        mod = BitVector.BitVector(bitstring="100011011")  # AES modulus
        n = 8
        a = BitVector.BitVector(bitstring="11100010110001")

        # Error: modulus too long
        mod_long = BitVector.BitVector(bitstring="1" * 15)
        with self.assertRaises(ValueError) as cm:
            a.gf_divide_by_modulus(mod_long, n)
        self.assertIn("Modulus bit pattern too long", str(cm.exception))

        # Normal division and alias
        quotient, remainder = a.gf_divide_by_modulus(mod, n)
        self.assertEqual(str(quotient), "00000000111010")
        self.assertEqual(str(remainder), "10001111")

        q_alias, r_alias = a.gf_divide(mod, n)
        self.assertEqual(str(q_alias), str(quotient))
        self.assertEqual(str(r_alias), str(remainder))

        # Test division where remainder becomes 0 (remainder.next_set_bit(0) == -1)
        a_equal = mod.deep_copy()
        q_eq, r_eq = a_equal.gf_divide_by_modulus(mod, n)
        self.assertEqual(int(r_eq), 0)

        # Test division where loop runs until i == num.length() without breaking earlier
        q_zero, r_zero = BitVector.BitVector(bitstring="0").gf_divide_by_modulus(
            BitVector.BitVector(bitstring="1"), 1
        )
        self.assertEqual(int(r_zero), 0)

    def test_gf_multiply_modular(self):
        mod = BitVector.BitVector(bitstring="100011011")  # AES modulus
        n = 8
        a = BitVector.BitVector(bitstring="0110001")
        b = BitVector.BitVector(bitstring="0110")
        c = a.gf_multiply_modular(b, mod, n)
        self.assertEqual(str(c), "10100110")

    def test_gf_MI(self):
        mod = BitVector.BitVector(bitstring="100011011")
        n = 8
        a = BitVector.BitVector(bitstring="00110011")
        mi = a.gf_MI(mod, n)
        self.assertEqual(str(mi), "01101100")

        # Test case where no multiplicative inverse exists
        mod_no_mi = BitVector.BitVector(bitstring="1010")
        a_no_mi = BitVector.BitVector(bitstring="0010")
        res_no_mi = a_no_mi.gf_MI(mod_no_mi, 3)
        self.assertIsInstance(res_no_mi, tuple)
        self.assertEqual(res_no_mi[0], "NO MI. However, the GCD of ")

    def test_runs(self):
        bv_empty = BitVector.BitVector(size=0)
        self.assertEqual(bv_empty.runs(), [])

        bv1 = BitVector.BitVector(bitlist=(1, 1, 1, 0, 0, 1))
        self.assertEqual(bv1.runs(), ["111", "00", "1"])

        bv2 = BitVector.BitVector(bitstring="001100")
        self.assertEqual(bv2.runs(), ["00", "11", "00"])

        bv3 = BitVector.BitVector(bitstring="0101")
        self.assertEqual(bv3.runs(), ["0", "1", "0", "1"])

    def test_test_for_primality(self):
        # p == 1
        self.assertEqual(BitVector.BitVector(intVal=1, size=8).test_for_primality(), 0)

        # p in probes [2, 3, 5, 7, 11, 13, 17]
        self.assertEqual(BitVector.BitVector(intVal=2, size=8).test_for_primality(), 1)
        self.assertEqual(BitVector.BitVector(intVal=17, size=8).test_for_primality(), 1)

        # p divisible by a probe (e.g. 25 = 5 * 5)
        self.assertEqual(BitVector.BitVector(intVal=25, size=8).test_for_primality(), 0)

        # Miller-Rabin test on primes > 17 (e.g. 19, 41)
        prob_19 = BitVector.BitVector(intVal=19, size=16).test_for_primality()
        self.assertGreater(prob_19, 0.99)
        prob_41 = BitVector.BitVector(intVal=41, size=16).test_for_primality()
        self.assertGreater(prob_41, 0.99)

        # Miller-Rabin test on composite not divisible by probes (e.g. 361 = 19 * 19)
        self.assertEqual(
            BitVector.BitVector(intVal=361, size=16).test_for_primality(), 0
        )

    def test_gen_random_bits(self):
        bv = BitVector.BitVector(size=0).gen_random_bits(32)
        self.assertEqual(bv.size, 32)
        self.assertEqual(int(bv) & 1, 1)

        bv_alias = BitVector.BitVector(size=0).gen_rand_bits_for_prime(16)
        self.assertEqual(bv_alias.size, 16)
        self.assertEqual(int(bv_alias) & 1, 1)

    def test_min_canonical(self):
        bv = BitVector.BitVector(bitstring="1101")
        self.assertEqual(str(bv.min_canonical()), "0111")


if __name__ == "__main__":
    unittest.main()
