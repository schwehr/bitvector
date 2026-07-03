import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import BitVector


class TestBitVectorStream(unittest.TestCase):
    def test_read_bits_from_file(self):
        # Error: no filename
        bv_no_file = BitVector.BitVector(size=8)
        with self.assertRaises(SyntaxError) as cm:
            bv_no_file.read_bits_from_file(8)
        self.assertIn("You need to first construct a BitVector", str(cm.exception))

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"AB")
            tmp_path = tmp.name

        try:
            bv = BitVector.BitVector(filename=tmp_path)

            # Error: blocksize not multiple of 8
            with self.assertRaises(ValueError) as cm:
                bv.read_bits_from_file(10)
            self.assertEqual("block size must be a multiple of 8", str(cm.exception))

            # Read first block (8 bits: 'A' = 0x41 = 01000001)
            bv1 = bv.read_bits_from_file(8)
            self.assertEqual(str(bv1), "01000001")
            self.assertTrue(bv.more_to_read)

            # Read second block (8 bits: 'B' = 0x42 = 01000010), file ends exactly here
            bv2 = bv.read_bits_from_file(8)
            self.assertEqual(str(bv2), "01000010")
            self.assertFalse(bv.more_to_read)

            # Read at EOF (returns size 0)
            bv3 = bv.read_bits_from_file(8)
            self.assertEqual(bv3.size, 0)
            self.assertEqual(str(bv3), "")
            bv.close_file_object()
        finally:
            Path(tmp_path).unlink(missing_ok=True)

        # Test partial block read (EOF mid-block)
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"A")
            tmp_path2 = tmp.name

        try:
            bv_part = BitVector.BitVector(filename=tmp_path2)
            bv_read = bv_part.read_bits_from_file(16)
            self.assertEqual(str(bv_read), "01000001")
            self.assertFalse(bv_part.more_to_read)
            bv_part.close_file_object()
        finally:
            Path(tmp_path2).unlink(missing_ok=True)

        # Test Python 2 branch in _readblock
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"\x05\xff")
            tmp_path3 = tmp.name

        try:
            with patch.object(sys, "version_info", (2, 7, 18)):
                bv_py2 = BitVector.BitVector(filename=tmp_path3)
                bv_py2_1 = bv_py2.read_bits_from_file(8)
                self.assertEqual(str(bv_py2_1), "00000101")
                bv_py2_2 = bv_py2.read_bits_from_file(8)
                self.assertEqual(str(bv_py2_2), "11111111")
                bv_py2.close_file_object()
        finally:
            Path(tmp_path3).unlink(missing_ok=True)

    def test_read_bits_from_fileobject(self):
        fp = io.StringIO("11010011")
        bv = BitVector.BitVector(size=0)
        bitlist = bv.read_bits_from_fileobject(fp)
        self.assertEqual(bitlist, ["1", "1", "0", "1", "0", "0", "1", "1"])

    def test_write_bits_to_stream_object(self):
        bv = BitVector.BitVector(bitstring="101100101")
        fp = io.StringIO()
        bv.write_bits_to_stream_object(fp)
        self.assertEqual(fp.getvalue(), "101100101")

    def test_write_to_file(self):
        # Error: length not multiple of 8
        bv_short = BitVector.BitVector(bitstring="10101")
        with self.assertRaises(ValueError) as cm:
            bv_short.write_to_file(io.BytesIO())
        self.assertIn(
            "Only a bit vector whose length is a multiple of 8", str(cm.exception)
        )

        # Normal write (Python 3 branch)
        bv = BitVector.BitVector(bitstring="0100000101000010")  # 'AB'
        out_stream = io.BytesIO()
        bv.write_to_file(out_stream)
        self.assertEqual(out_stream.getvalue(), b"AB")

        # Calling again to test self.FILEOUT already set
        bv.write_to_file(out_stream)
        self.assertEqual(out_stream.getvalue(), b"ABAB")

        # Test Python 2 branch in write_to_file
        bv_py2 = BitVector.BitVector(bitstring="01000001")  # 'A'
        out_str_stream = io.StringIO()
        with patch.object(sys, "version_info", (2, 7, 18)):
            bv_py2.write_to_file(out_str_stream)
        self.assertEqual(out_str_stream.getvalue(), "A")

    def test_close_file_object(self):
        # Error: no associated open file
        bv_no_file = BitVector.BitVector(size=8)
        with self.assertRaises(SyntaxError) as cm:
            bv_no_file.close_file_object()
        self.assertEqual("No associated open file", str(cm.exception))

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test")
            tmp_path = tmp.name

        try:
            bv = BitVector.BitVector(filename=tmp_path)
            self.assertFalse(bv.FILEIN.closed)
            bv.close_file_object()
            self.assertTrue(bv.FILEIN.closed)
        finally:
            Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
