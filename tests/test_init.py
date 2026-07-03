import io
import os
import tempfile
import unittest

import BitVector


class ZeroHex:
    """Helper class to test intVal == 0 False branch (while loop exit without break and size == 0 branch)."""

    def __eq__(self, other):
        return False

    def __index__(self):
        return 0


class TestBitVectorInit(unittest.TestCase):
    def test_positional_args_error(self):
        with self.assertRaises(ValueError) as cm:
            BitVector.BitVector(123)
        self.assertIn("BitVector constructor can only be called", str(cm.exception))

    def test_invalid_keyword_error(self):
        with self.assertRaises(ValueError) as cm:
            BitVector.BitVector(invalid_param=123)
        self.assertEqual("Wrong keyword used --- check spelling", str(cm.exception))

    def test_filename_constructor(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"A")
            tmp_path = tmp.name

        try:
            with self.assertRaises(ValueError) as cm:
                BitVector.BitVector(filename=tmp_path, size=8)
            self.assertIn("When filename is specified", str(cm.exception))

            bv = BitVector.BitVector(filename=tmp_path)
            self.assertEqual(bv.filename, tmp_path)
            self.assertTrue(bv.more_to_read)
            bv.close_file_object()
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_fp_constructor(self):
        fp = io.StringIO("1011000101110")
        with self.assertRaises(ValueError) as cm:
            BitVector.BitVector(fp=fp, size=13)
        self.assertIn("When fileobject is specified", str(cm.exception))

        fp = io.StringIO("1011000101110")
        bv = BitVector.BitVector(fp=fp)
        self.assertEqual(str(bv), "1011000101110")

    def test_intVal_constructor_zero(self):
        bv = BitVector.BitVector(intVal=0)
        self.assertEqual(bv.size, 1)
        self.assertEqual(str(bv), "0")

        with self.assertRaises(ValueError) as cm:
            BitVector.BitVector(intVal=0, size=0)
        self.assertIn(
            "The value specified for size must be at least", str(cm.exception)
        )

        with self.assertRaises(ValueError) as cm:
            BitVector.BitVector(intVal=0, size=-1)
        self.assertIn(
            "The value specified for size must be at least", str(cm.exception)
        )

        bv = BitVector.BitVector(intVal=0, size=5)
        self.assertEqual(bv.size, 5)
        self.assertEqual(str(bv), "00000")

    def test_intVal_constructor_nonzero(self):
        with self.assertRaises(ValueError) as cm:
            BitVector.BitVector(intVal=5, bitstring="101")
        self.assertIn("When intVal is specified", str(cm.exception))

        bv = BitVector.BitVector(intVal=5)
        self.assertEqual(str(bv), "101")
        self.assertEqual(bv.size, 3)

        bv = BitVector.BitVector(intVal=32)
        self.assertEqual(str(bv), "100000")
        self.assertEqual(bv.size, 6)

        with self.assertRaises(ValueError) as cm:
            BitVector.BitVector(intVal=5, size=0)
        self.assertIn(
            "The value specified for size must be at least", str(cm.exception)
        )

        with self.assertRaises(ValueError) as cm:
            BitVector.BitVector(intVal=255, size=2)
        self.assertIn(
            "The value specified for size must be at least", str(cm.exception)
        )

        bv = BitVector.BitVector(intVal=5, size=10)
        self.assertEqual(bv.size, 10)
        self.assertEqual(str(bv), "0000000101")

    def test_intVal_zero_hex_loop_and_size_zero_false(self):
        bv = BitVector.BitVector(intVal=ZeroHex(), size=0)
        self.assertEqual(bv.size, 0)
        self.assertEqual(str(bv), "")

        bv2 = BitVector.BitVector(intVal=ZeroHex(), size=5)
        self.assertEqual(bv2.size, 5)
        self.assertEqual(str(bv2), "00000")

    def test_size_constructor(self):
        with self.assertRaises(ValueError) as cm:
            BitVector.BitVector(size=10, bitlist=[1, 0])
        self.assertIn("When size is specified (without an intVal)", str(cm.exception))

        bv = BitVector.BitVector(size=10)
        self.assertEqual(bv.size, 10)
        self.assertEqual(str(bv), "0000000000")

        bv_zero = BitVector.BitVector(size=0)
        self.assertEqual(bv_zero.size, 0)
        self.assertEqual(str(bv_zero), "")

        with self.assertRaises(ValueError) as cm:
            BitVector.BitVector(size=-5)
        self.assertEqual("wrong arg(s) for constructor", str(cm.exception))

    def test_bitstring_constructor(self):
        with self.assertRaises(ValueError) as cm:
            BitVector.BitVector(bitstring="1010", rawbytes=b"xy")
        self.assertIn("When a bitstring is specified", str(cm.exception))

        bv = BitVector.BitVector(bitstring="00110011")
        self.assertEqual(str(bv), "00110011")

        bv_empty = BitVector.BitVector(bitstring="")
        self.assertEqual(str(bv_empty), "")

    def test_bitlist_constructor(self):
        with self.assertRaises(ValueError) as cm:
            BitVector.BitVector(bitlist=[1, 0], hexstring="a")
        self.assertIn("When bits are specified", str(cm.exception))

        bv = BitVector.BitVector(bitlist=[1, 1, 0, 1])
        self.assertEqual(str(bv), "1101")

        bv_empty = BitVector.BitVector(bitlist=[])
        self.assertEqual(str(bv_empty), "")

    def test_textstring_constructor(self):
        with self.assertRaises(ValueError) as cm:
            BitVector.BitVector(textstring="hello", rawbytes=b"a")
        self.assertIn("When bits are specified through textstring", str(cm.exception))

        bv = BitVector.BitVector(textstring="A\x05")
        self.assertEqual(bv.size, 16)
        self.assertEqual(str(bv), "0100000100000101")

        bv_empty = BitVector.BitVector(textstring="")
        self.assertEqual(str(bv_empty), "")

    def test_hexstring_constructor(self):
        with self.assertRaises(ValueError) as cm:
            BitVector.BitVector(hexstring="0f", rawbytes=b"xy")
        self.assertIn("When bits are specified through hexstring", str(cm.exception))

        bv = BitVector.BitVector(hexstring="0FaE")
        self.assertEqual(str(bv), "0000111110101110")

        bv_empty = BitVector.BitVector(hexstring="")
        self.assertEqual(str(bv_empty), "")

    def test_rawbytes_constructor(self):
        with self.assertRaises(ValueError) as cm:
            BitVector.BitVector(rawbytes=b"xy", size=-5)
        self.assertIn("When bits are specified through rawbytes", str(cm.exception))

        bv = BitVector.BitVector(rawbytes=b"\x00\xff")
        self.assertEqual(str(bv), "0000000011111111")

    def test_no_args_or_unmatched_constructor(self):
        with self.assertRaises(ValueError) as cm:
            BitVector.BitVector()
        self.assertEqual("wrong arg(s) for constructor", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            BitVector.BitVector(rawbytes=b"")
        self.assertEqual("wrong arg(s) for constructor", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
