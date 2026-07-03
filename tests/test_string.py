import unittest

import BitVector


class TestBitVectorString(unittest.TestCase):
    def test_get_bitvector_in_ascii(self):
        # Error: length not multiple of 8
        bv_short = BitVector.BitVector(bitstring="10101")
        with self.assertRaises(ValueError) as cm:
            bv_short.get_bitvector_in_ascii()
        self.assertIn("must be an integral multiple of 8 bits", str(cm.exception))

        # Normal ASCII conversion
        bv = BitVector.BitVector(textstring="hello")
        self.assertEqual(bv.get_bitvector_in_ascii(), "hello")

        # Empty vector (0 is multiple of 8)
        bv_empty = BitVector.BitVector(size=0)
        self.assertEqual(bv_empty.get_bitvector_in_ascii(), "")

    def test_get_bitvector_in_hex(self):
        # Error: length not multiple of 4
        bv_short = BitVector.BitVector(bitstring="101")
        with self.assertRaises(ValueError) as cm:
            bv_short.get_bitvector_in_hex()
        self.assertIn("must be an integral multiple of 4 bits", str(cm.exception))

        # Normal hex conversion
        bv = BitVector.BitVector(hexstring="68656c6c6f")
        self.assertEqual(bv.get_bitvector_in_hex(), "68656c6c6f")

        # Empty vector (0 is multiple of 4)
        bv_empty = BitVector.BitVector(size=0)
        self.assertEqual(bv_empty.get_bitvector_in_hex(), "")


if __name__ == "__main__":
    unittest.main()
