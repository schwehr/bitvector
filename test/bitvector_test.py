#!/usr/bin/env python

"""Tests for BitVector.py."""
import base64
import binascii  # pylint: disable=unused-import
import io
import os
import shutil
import sys
import tempfile
import unittest

from BitVector import BitVector


class BitvectorTest(unittest.TestCase):

    def testBasics(self):
        # Construct an EMPTY bit vector.
        bv1 = BitVector(size=0)
        self.assertEqual(str(bv1), '')
        self.assertEqual(len(bv1), 0)

        # Construct a bit vector of size 2.
        bv2 = BitVector(size=2)
        self.assertEqual(str(bv2), '00')
        self.assertEqual(len(bv2), 2)

        # Joining two bit vectors.
        self.assertEqual(str(bv1 + bv2), '00')

    def testFromTuple(self):
        self.assertEqual(str(BitVector(bitlist=(1, 0, 0, 1))), '1001')

    def testFromList(self):
        self.assertEqual(str(BitVector(bitlist=[1, 1, 0, 1])), '1101')

    def testFromInt(self):
        self.assertEqual(str(BitVector(intVal=5678)), '1011000101110')

        self.assertEqual(str(BitVector(intVal=0)), '0')
        self.assertEqual(str(BitVector(intVal=2)), '10')
        self.assertEqual(str(BitVector(intVal=3)), '11')
        self.assertEqual(str(BitVector(intVal=123456)), '11110001001000000')
        self.assertEqual(BitVector(intVal=123456).int_val(), 123456)
        self.assertEqual(int(BitVector(intVal=123456)), 123456)

    def testFromVeryLargeInt(self):
        # pylint:disable=line-too-long
        x = 12345678901234567890123456789012345678901234567890123456789012345678901234567890
        self.assertEqual(int(BitVector(intVal=x)), x)

    def testFromFileLikeObject(self):
        x = '111100001111'
        if sys.version_info[0] == 2:
            x = unicode(x)
        fp_read = io.StringIO(x)
        self.assertEqual(str(BitVector(fp=fp_read)), '111100001111')

    def testFromBitString(self):
        self.assertEqual(str(BitVector(bitstring='00110011')), '00110011')

    def testEmptyBitString(self):
        self.assertEqual(str(BitVector(bitstring='')), '')
        self.assertEqual(BitVector(bitstring='').int_val(), 0)

    def testFromTextString(self):
        self.assertEqual(
            BitVector(textstring='hello').get_text_from_bitvector(), 'hello')

        self.assertEqual(
            BitVector(textstring='hello\njello').get_text_from_bitvector(),
            'hello\njello')

    def testFromHexString(self):
        self.assertEqual(
            BitVector(hexstring='68656c6c6f').get_hex_string_from_bitvector(),
            '68656c6c6f')

    def testRawByteMode(self):
        # Useful for reading public and private keys.
        pubkey = (
            'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA5amriY96HQS8Y/nKc8zu3zOylvpOn'
            '3vzMmWwrtyDy+aBvns4UC1RXoaD9rDKqNNMCBAQwWDsYwCAFsrBzbxRQONHePX8lR'
            'WgM87MseWGlu6WPzWGiJMclTAO9CTknplG9wlNzLQBj3dP1M895iLF6jvJ7GR+V3C'
            'RU6UUbMmRvgPcsfv6ec9RRPm/B8ftUuQICL0jt4tKdPG45PBJUylHs71FuE9FJNp0'
            '1hrj1EMFObNTcsy9zuis0YPyzArTYSOUsGglleExAQYi7iLh17pAa+y6fZrGLsptg'
            'qryuftN9Q4NqPuTiFjlqRowCDU7sSxKDgU7bzhshyVx3+pzXO4D2Q== kak@pixie')

        if sys.version_info[0] == 2:
            keydata = base64.b64decode(pubkey.split()[1])
        else:
            keydata = base64.b64decode(bytes(pubkey.split()[1], 'utf-8'))
        data = (
            '\x00\x00\x00\x07ssh-rsa\x00\x00\x00\x01#\x00\x00\x01\x01\x00\xe5'
            '\xa9\xab\x89\x8fz\x1d\x04\xbcc\xf9\xcas\xcc\xee\xdf3\xb2\x96\xfaN'
            '\x9f{\xf32e\xb0\xae\xdc\x83\xcb\xe6\x81\xbe{8P-Q^\x86\x83\xf6\xb0'
            '\xca\xa8\xd3L\x08\x10\x10\xc1`\xecc\x00\x80\x16\xca\xc1\xcd\xbcQ@'
            '\xe3Gx\xf5\xfc\x95\x15\xa03\xce\xcc\xb1\xe5\x86\x96\xee\x96?5\x86'
            '\x88\x93\x1c\x950\x0e\xf4$\xe4\x9e\x99F\xf7\tM\xcc\xb4\x01\x8fwO'
            '\xd4\xcf=\xe6"\xc5\xea;\xc9\xecd~Wp\x91S\xa5\x14l\xc9\x91\xbe\x03'
            '\xdc\xb1\xfb\xfay\xcfQD\xf9\xbf\x07\xc7\xedR\xe4\x08\x08\xbd#\xb7'
            '\x8bJt\xf1\xb8\xe4\xf0IS)G\xb3\xbdE\xb8OE$\xdat\xd6\x1a\xe3\xd4C'
            '\x059\xb3Sr\xcc\xbd\xce\xe8\xac\xd1\x83\xf2\xcc\n\xd3a#\x94\xb0h%'
            '\x95\xe11\x01\x06"\xee"\xe1\xd7\xba@k\xec\xba}\x9a\xc6.\xcam\x82'
            '\xaa\xf2\xb9\xfbM\xf5\x0e\r\xa8\xfb\x93\x88X\xe5\xa9\x1a0\x085;'
            '\xb1,J\x0e\x05;o8l\x87%q\xdf\xeas\\\xee\x03\xd9')
        self.assertEqual(BitVector(rawbytes=keydata).get_text_from_bitvector(),
                         data)

    def testArrayLikeIndexing(self):
        bv = BitVector(bitstring='110001')
        self.assertEqual(
            [bv[0], bv[1], bv[2], bv[3], bv[4], bv[5]],
            [1, 1, 0, 0, 0, 1])
        self.assertEqual(
            [bv[-1], bv[-2], bv[-3], bv[-4], bv[-5], bv[-6]],
            [1, 0, 0, 0, 1, 1])

    def testSettingWithAccessors(self):
        bv = BitVector(bitstring='1111')

        bv[0] = 0
        bv[1] = 0
        bv[2] = 0
        bv[3] = 0
        self.assertEqual(str(bv), '0000')

        bv[-1] = 1
        bv[-2] = 1
        bv[-4] = 1
        self.assertEqual(str(bv), '1011')

    def testEquality(self):
        bv1 = BitVector(bitstring='00110011')
        bv2 = BitVector(bitlist=[0, 0, 1, 1, 0, 0, 1, 1])
        self.assertTrue(bv1 == bv2)
        self.assertFalse(bv1 != bv2)
        self.assertFalse(bv1 < bv2)
        self.assertTrue(bv1 <= bv2)

        bv3 = BitVector(intVal=5678)
        self.assertEqual(bv3.int_val(), 5678)
        self.assertEqual(str(bv3), '1011000101110')
        self.assertFalse(bv1 == bv3)
        self.assertTrue(bv3 > bv1)
        self.assertTrue(bv3 >= bv1)

    def testWriteToFileLike(self):
        fp_write = io.StringIO()
        BitVector(bitstring='1011').write_bits_to_fileobject(fp_write)
        self.assertEqual(fp_write.getvalue(), '1011')

    def testBitwiseLogicalOperations(self):
        bv1 = BitVector(bitstring='00110011')
        bv2 = BitVector(bitlist=[0, 0, 1, 1, 0, 0, 1, 1])
        self.assertEqual(str(bv1 | bv2), '00110011')
        self.assertEqual(str(bv1 & bv2), '00110011')
        bv3 = bv1 + bv2
        self.assertEqual(str(bv3), '0011001100110011')
        bv4 = BitVector(size=3)
        self.assertEqual(str(bv4), '000')
        bv5 = bv3 + bv4
        self.assertEqual(str(bv5), '0011001100110011000')
        bv6 = ~bv5
        self.assertEqual(str(bv6), '1100110011001100111')
        self.assertEqual(str(bv5 & bv6), '0000000000000000000')
        self.assertEqual(str(bv5 | bv6), '1111111111111111111')

    def testLogicalOperationsOnDifferentSizes(self):
        bv1 = BitVector(intVal=6)
        bv2 = BitVector(intVal=13)
        self.assertEqual(str(bv1 ^ bv2), '1011')
        self.assertEqual(str(bv1 & bv2), '0100')
        self.assertEqual(str(bv1 | bv2), '1111')

        bv3 = BitVector(intVal=1)
        self.assertEqual(str(bv3 ^ bv2), '1100')
        self.assertEqual(str(bv3 & bv2), '0001')
        self.assertEqual(str(bv3 | bv2), '1101')

    def testSetbitAndLen(self):
        bv1 = BitVector(bitstring='1111111111111111111')
        bv1[7] = 0
        self.assertEqual(str(bv1), '1111111011111111111')
        self.assertEqual(len(bv1), 19)

        bv2 = BitVector(bitstring='0011001100110011000')
        bv3 = BitVector(bitstring='1100110011001100111')
        self.assertEqual(str((bv2 & bv3) ^ bv1), '1111111011111111111')

    # TODO(schwehr): Find this file both when the test is run directly
    #   and when run with python setup.py test.
    @unittest.skipIf(not os.path.isfile('testinput1.txt'),
                     'Unable to find testinput1.txt')
    def testReadFromFile(self):
        bv = BitVector(filename='testinput1.txt')
        self.assertEqual(str(bv), '')
        bv1 = bv.read_bits_from_file(64)
        self.assertEqual(
            str(bv1),
            '0100000100100000011010000111010101101110011001110111001001111001')
        bv2 = bv.read_bits_from_file(64)
        self.assertEqual(
            str(bv2),
            '0010000001100010011100100110111101110111011011100010000001100110')

        bv3 = bv1 ^ (bv2)
        self.assertEqual(
            str(bv3),
            '0110000101000010000110100001101000011001000010010101001000011111')

    def testDivideIntoTwo(self):
        bv = BitVector(
            bitstring=('01100001010000100001101000011010000110010000100101010'
                       '01000011111'))
        bv1, bv2 = bv.divide_into_two()
        self.assertEqual(str(bv1), '01100001010000100001101000011010')
        self.assertEqual(str(bv2), '00011001000010010101001000011111')

    def testPermute(self):
        bv = BitVector(bitstring='1001101')
        self.assertEqual(str(bv.permute([6, 2, 0, 1])), '1010')

    def testWriteToFile(self):
        bitstring = '00001010'
        tmp_dir = tempfile.mkdtemp()
        self.assertIsNotNone(tmp_dir, None)
        try:
            filepath = os.path.join(tmp_dir, 'test.txt')
            with open(filepath, 'wb') as out:
                BitVector(bitstring=bitstring).write_to_file(out)
            bv2 = BitVector(filename=filepath)
            bv3 = bv2.read_bits_from_file(32)
            self.assertEqual(str(bv3), bitstring)
        finally:
            if tmp_dir:
                shutil.rmtree(tmp_dir)

    # TODO(schwehr): Find this file both when the test is run directly
    #   and when run with python setup.py test.
    @unittest.skipIf(not os.path.isfile('testinput1.txt'),
                     'Unable to find testinput4.txt')
    def testReadEntireFile(self):
        filename = 'testinput4.txt'
        expected = (
            '0100000100100000011010000111010101101110011001110111001001111001',
            '0010000001100010011100100110111101110111011011100010000001100110',
            '0110111101111000001000000110101001110101011011010111000001100101',
            '0110010000100000011011110111011001100101011100100010000001100001',
            '0010000001101100011000010111101001111001001000000111011101101001',
            '0110110001100100001000000110010001101111011001110010111000001010',
            '0000101001100001011000010110000101100001011000010110000101100001',
            '0110000101100001011000010110000101100001000010100000101001101010',
            '0110101001101010011010100110101001101010011010100110101001101010',
            '0110101001101010011010100110101001101010011010100110101001101010',
            '0000101000001010011000110111001001111001011100000111010001101111',
            '0010000001110100011001010110101100001010')
        bv = BitVector(filename=filename)
        read_num = 0
        while bv.more_to_read:
            self.assertEqual(str(bv.read_bits_from_file(64)),
                             expected[read_num])
            read_num += 1

        # Closing file object and start extracting the beginning again.
        bv.close_file_object()
        bv = BitVector(filename=filename)
        self.assertEqual(str(bv.read_bits_from_file(64)), expected[0])

    def testPermutationAndUnpermutation64Bit(self):
        bits = '0100000100100000011010000111010101101110011001110111001001111001'
        bv = BitVector(bitstring=bits)

        # Permutation array was generated by the Fisher-Yates shuffle algorithm.
        bv2 = bv.permute([
            22, 47, 33, 36, 18, 6, 32, 29, 54, 62, 4,
            9, 42, 39, 45, 59, 8, 50, 35, 20, 25, 49,
            15, 61, 55, 60, 0, 14, 38, 40, 23, 17, 41,
            10, 57, 12, 30, 3, 52, 11, 26, 43, 21, 13,
            58, 37, 48, 28, 1, 63, 2, 31, 53, 56, 44, 24,
            51, 19, 7, 5, 34, 27, 16, 46])
        self.assertEqual(
            str(bv2),
            '0111100110001011010111000100100111100000100011001101000010101101')

        bv3 = bv2.unpermute([
            22, 47, 33, 36, 18, 6, 32, 29, 54, 62, 4,
            9, 42, 39, 45, 59, 8, 50, 35, 20, 25, 49,
            15, 61, 55, 60, 0, 14, 38, 40, 23, 17, 41,
            10, 57, 12, 30, 3, 52, 11, 26, 43, 21, 13,
            58, 37, 48, 28, 1, 63, 2, 31, 53, 56, 44, 24,
            51, 19, 7, 5, 34, 27, 16, 46])
        self.assertEqual(str(bv3), bits)

    def testCircularShifts(self):
        bits = ('010000010010000001101000011101010110111001100111011100100111'
                '1001')
        bv = BitVector(bitstring=bits)
        self.assertEqual(
            str(bv << 7),
            '1001000000110100001110101011011100110011101110010011110010100000')

        self.assertEqual(
            str(bv >> 7),
            '0100000100100000011010000111010101101110011001110111001001111001')

        self.assertEqual(len(bv), 64)

    def testSlicingAndIterating(self):
        bits = ('010000010010000001101000011101010110111001100111011100100111'
                '1001')
        bv = BitVector(bitstring=bits)
        bv2 = bv[5:22]
        self.assertEqual(str(bv2), '00100100000011010')
        self.assertEqual(
            [bit for bit in bv2],
            [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0])

    def testPadding(self):
        bv = BitVector(bitstring='101010')
        bv.pad_from_left(4)
        self.assertEqual(str(bv), '0000101010')

        bv.pad_from_right(4)
        self.assertEqual(str(bv), '00001010100000')

    def testIn(self):
        bits = '0011001100'
        bv1 = BitVector(bitstring=bits)
        self.assertIn(BitVector(bitstring=bits), bv1)
        self.assertIn(BitVector(bitstring='110011'), bv1)
        self.assertNotIn(BitVector(bitstring='111'), bv1)

    def testInitialSize(self):
        self.assertEqual(str(BitVector(intVal=45, size=16)), '0000000000101101')
        self.assertEqual(str(BitVector(intVal=0, size=8)), '00000000')
        self.assertEqual(str(BitVector(intVal=1, size=8)), '00000001')

    def testSliceAssign(self):
        bv1 = BitVector(size=25)
        bv2 = BitVector(bitstring='1010001')
        bv1[6:9] = bv2[0:3]
        self.assertEqual(str(bv1), '0000001010000000000000000')
        bv1[:5] = bv1[5:10]
        self.assertEqual(str(bv1), '0101001010000000000000000')
        bv1[20:] = bv1[5:10]
        self.assertEqual(str(bv1), '0101001010000000000001010')
        bv1[:] = bv1[:]
        self.assertEqual(str(bv1), '0101001010000000000001010')
        bv3 = bv1[:]
        self.assertEqual(str(bv3), '0101001010000000000001010')

    def testReset(self):
        bv = BitVector(bitstring='0101001010000000000001010')
        bv.reset(1)
        self.assertEqual(str(bv), '1111111111111111111111111')
        self.assertEqual(str(bv[3:9].reset(0)), '000000')
        self.assertEqual(str(bv[:].reset(0)), '0000000000000000000000000')

    def testCountBits(self):
        self.assertEqual(BitVector(intVal=45, size=16).count_bits(), 4)
        self.assertEqual(BitVector(bitstring='100111').count_bits(), 4)
        self.assertEqual(BitVector(bitstring='00111000').count_bits(), 3)
        self.assertEqual(BitVector(bitstring='001').count_bits(), 1)
        self.assertEqual(BitVector(bitstring='00000000000000').count_bits(), 0)

    def testSetValue(self):
        bv = BitVector(intVal=7, size=16)
        bv.set_value(intVal=45)
        self.assertEqual(str(bv), '101101')

    def testCountBitsSparse(self):
        bv = BitVector(size=2000000)
        bv[345234] = 1
        bv[233] = 1
        bv[243] = 1
        bv[18] = 1
        bv[785] = 1
        self.assertEqual(bv.count_bits_sparse(), 5)

    def testJaccardSimiliarityDistanceAndHammingDistance(self):
        bv1 = BitVector(bitstring='11111111')
        bv2 = BitVector(bitstring='00101011')
        self.assertEqual(bv1.jaccard_similarity(bv2), 0.5)
        self.assertEqual(bv1.jaccard_distance(bv2), 0.5)
        self.assertEqual(bv1.hamming_distance(bv2), 4)

    def testNextSetBit(self):
        self.assertEqual(
            BitVector(bitstring='00000000000001').next_set_bit(5), 13)
        self.assertEqual(
            BitVector(bitstring='000000000000001').next_set_bit(5), 14)
        self.assertEqual(BitVector(
            bitstring='0000000000000001').next_set_bit(5), 15)
        self.assertEqual(
            BitVector(bitstring='00000000000000001').next_set_bit(5), 16)

    def testRankOfBitSetAtIndex(self):
        self.assertEqual(
            BitVector(
                bitstring='01010101011100').rank_of_bit_set_at_index(10), 6)

    def testIsPowerOf2(self):
        # 826
        self.assertFalse(BitVector(bitstring='10000000001110').is_power_of_2())
        self.assertTrue(BitVector(intVal=2**20).is_power_of_2())

        self.assertFalse(BitVector(intVal=826).is_power_of_2_sparse())
        self.assertTrue(BitVector(intVal=2**20).is_power_of_2_sparse())

    def testReverse(self):
        bits = '0001100000000000001'
        self.assertEqual(str(BitVector(bitstring=bits).reverse()), bits[::-1])

    def testGreatestCommonDivisor(self):
        self.assertEqual(
            int(BitVector(intVal=102).gcd(BitVector(intVal=26))), 2)
        self.assertEqual(
                int(BitVector(intVal=7*13).gcd(BitVector(intVal=11*13))), 13)

    def testMultiplicativeInverse(self):
        bv_modulus = BitVector(intVal=32)
        bv = BitVector(intVal=17)
        self.assertEqual(int(bv.multiplicative_inverse(bv_modulus)), 17)

    def testMultiplicationInGf2(self):
        bv = BitVector(bitstring='0110001')
        self.assertEqual(
            str(bv.gf_multiply(BitVector(bitstring='0110'))), '00010100110')

    def testDivitionInGf2(self):
        mod = BitVector(bitstring='100011011')  # AES modulus.
        quotient, remainder = (
            BitVector(bitstring='11100010110001').gf_divide(mod, 8))
        self.assertEqual(str(quotient), '00000000111010')
        self.assertEqual(str(remainder), '10001111')

    def testModularMultiplicationInGf2(self):
        mod = BitVector(bitstring='100011011')  # AES modulus.
        b = BitVector(bitstring='0110')
        c = BitVector(bitstring='0110001').gf_multiply_modular(b, mod, 8)
        self.assertEqual(str(c), '10100110')

    def testMultiplicativeInvInGf2WithModPolynomial(self):
        # Modulus polynomial = x^3 + x + 1
        mod = BitVector(bitstring='100011011')  # AES modulus.
        self.assertEqual(
            str(BitVector(bitstring='00110011').gf_MI(mod, 8)), '01101100')

    def testMoreModular(self):
        # In the following, the first row shows the binary code words, the
        # second the multiplicative inverses and the third the product of
        # a binary word with its multiplicative inverse.

        mod = BitVector(bitstring='1011')
        n = 3
        bitarrays = [BitVector(intVal=x, size=n) for x in range(1, 2**3)]

        # Bit arrays in GF(2^3).
        self.assertEqual(
            [str(x) for x in bitarrays],
            ['001', '010', '011', '100', '101', '110', '111'])

        # Multiplicati_inverses.
        mi_list = [x.gf_MI(mod, n) for x in bitarrays]
        self.assertEqual(
            [str(mi) for mi in mi_list],
            ['001', '101', '110', '111', '010', '011', '100'])

        products = [str(bitarrays[i].gf_multiply_modular(mi_list[i], mod, n))
                    for i in range(len(bitarrays))]
        self.assertEqual(
            products,
            ['001', '001', '001', '001', '001', '001', '001'])

    @unittest.skip('slow')
    def testAesMultiplicativeInverses(self):
        # In GF(2^8) with modulus polynomial x^8 + x^4 + x^3 + x + 1
        # This takes a few seconds.
        mod = BitVector(bitstring='100011011')
        n = 8
        bitarrays = [BitVector(intVal=x, size=n) for x in range(1, 2**8)]
        mi_list = [x.gf_MI(mod, n) for x in bitarrays]
        self.assertEqual(
            [str(mi) for mi in mi_list],
            ['00000001', '10001101', '11110110', '11001011', '01010010',
             '01111011', '11010001', '11101000', '01001111', '00101001',
             '11000000', '10110000', '11100001', '11100101', '11000111',
             '01110100', '10110100', '10101010', '01001011', '10011001',
             '00101011', '01100000', '01011111', '01011000', '00111111',
             '11111101', '11001100', '11111111', '01000000', '11101110',
             '10110010', '00111010', '01101110', '01011010', '11110001',
             '01010101', '01001101', '10101000', '11001001', '11000001',
             '00001010', '10011000', '00010101', '00110000', '01000100',
             '10100010', '11000010', '00101100', '01000101', '10010010',
             '01101100', '11110011', '00111001', '01100110', '01000010',
             '11110010', '00110101', '00100000', '01101111', '01110111',
             '10111011', '01011001', '00011001', '00011101', '11111110',
             '00110111', '01100111', '00101101', '00110001', '11110101',
             '01101001', '10100111', '01100100', '10101011', '00010011',
             '01010100', '00100101', '11101001', '00001001', '11101101',
             '01011100', '00000101', '11001010', '01001100', '00100100',
             '10000111', '10111111', '00011000', '00111110', '00100010',
             '11110000', '01010001', '11101100', '01100001', '00010111',
             '00010110', '01011110', '10101111', '11010011', '01001001',
             '10100110', '00110110', '01000011', '11110100', '01000111',
             '10010001', '11011111', '00110011', '10010011', '00100001',
             '00111011', '01111001', '10110111', '10010111', '10000101',
             '00010000', '10110101', '10111010', '00111100', '10110110',
             '01110000', '11010000', '00000110', '10100001', '11111010',
             '10000001', '10000010', '10000011', '01111110', '01111111',
             '10000000', '10010110', '01110011', '10111110', '01010110',
             '10011011', '10011110', '10010101', '11011001', '11110111',
             '00000010', '10111001', '10100100', '11011110', '01101010',
             '00110010', '01101101', '11011000', '10001010', '10000100',
             '01110010', '00101010', '00010100', '10011111', '10001000',
             '11111001', '11011100', '10001001', '10011010', '11111011',
             '01111100', '00101110', '11000011', '10001111', '10111000',
             '01100101', '01001000', '00100110', '11001000', '00010010',
             '01001010', '11001110', '11100111', '11010010', '01100010',
             '00001100', '11100000', '00011111', '11101111', '00010001',
             '01110101', '01111000', '01110001', '10100101', '10001110',
             '01110110', '00111101', '10111101', '10111100', '10000110',
             '01010111', '00001011', '00101000', '00101111', '10100011',
             '11011010', '11010100', '11100100', '00001111', '10101001',
             '00100111', '01010011', '00000100', '00011011', '11111100',
             '10101100', '11100110', '01111010', '00000111', '10101110',
             '01100011', '11000101', '11011011', '11100010', '11101010',
             '10010100', '10001011', '11000100', '11010101', '10011101',
             '11111000', '10010000', '01101011', '10110001', '00001101',
             '11010110', '11101011', '11000110', '00001110', '11001111',
             '10101101', '00001000', '01001110', '11010111', '11100011',
             '01011101', '01010000', '00011110', '10110011', '01011011',
             '00100011', '00111000', '00110100', '01101000', '01000110',
             '00000011', '10001100', '11011101', '10011100', '01111101',
             '10100000', '11001101', '00011010', '01000001', '00011100'])

        products = [str(bitarrays[i].gf_multiply_modular(mi_list[i], mod, n))
                    for i in range(len(bitarrays))]
        self.assertEqual(products, ['00000001']*255)

    def testRuns(self):
        self.assertEqual(
            [str(val) for val in BitVector(bitstring='1001').runs()],
            ['1', '00', '1'])
        self.assertEqual(
            [str(val) for val in BitVector(bitstring='10').runs()],
            ['1', '0'])
        self.assertEqual(
            [str(val) for val in BitVector(bitstring='01').runs()],
            ['0', '1'])
        self.assertEqual(
            [str(val) for val in BitVector(bitstring='0001').runs()],
            ['000', '1'])
        self.assertEqual(
            [str(val) for val in BitVector(bitstring='0110').runs()],
            ['0', '11', '0'])

    def testChainedCircularShifts(self):
        bv = BitVector(bitstring='111001')
        self.assertEqual(str(bv >> 1), '111100')
        self.assertEqual(str(bv >> 1 >> 1), '001111')

        bv1 = BitVector(bitstring='111001')
        self.assertEqual(str(bv1 << 1), '110011')
        self.assertEqual(str(bv1 << 1 << 1), '001111')

    def testChainedNonCircularShifts(self):
        bv = BitVector(bitstring='111001')
        self.assertEqual(str(bv.shift_right(1)), '011100')
        self.assertEqual(str(bv.shift_right(1).shift_right(1)), '000111')

        bv1 = BitVector(bitstring='111001')
        self.assertEqual(str(bv1.shift_left(1)), '110010')
        self.assertEqual(str(bv1.shift_left(1).shift_left(1)), '001000')

    def testPrimality(self):
        primes = [179, 233, 283, 353, 419, 467, 547, 607, 661, 739, 811, 877,
                  947, 1019, 1087, 1153, 1229, 1297, 1381, 1453, 1523, 1597,
                  1663, 1741, 1823, 1901, 7001, 7109, 7211, 7307, 7417, 7507,
                  7573, 7649, 7727, 7841]
        for prime in primes:
            self.assertAlmostEqual(
                BitVector(intVal=prime).test_for_primality(), 1.0, delta=4)

    def testGenRand32BitsForPrime(self):
        for unused_count in range(100):
            bv = BitVector(intVal=0).gen_rand_bits_for_prime(32)
            self.assertEqual(len(bv), 32)
            self.assertLess(int(bv), 2**32)


if __name__ == '__main__':
    unittest.main()
