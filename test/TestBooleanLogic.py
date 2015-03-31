import unittest

import BitVector


bv1 = BitVector.BitVector(bitstring='00110011')
bv2 = BitVector.BitVector(bitlist=[1, 1, 1, 1, 0, 0, 1, 1])
bv3 = BitVector.BitVector(bitstring='00000000111111110000000')
bv4 = BitVector.BitVector(bitstring='')
bv5 = BitVector.BitVector(size=0)


class BooleanLogicTestCase(unittest.TestCase):

  def testAndWithSomeOnes(self):
    """And with overlapping ones in a bitlist."""
    self.assertEqual(bv1 & bv2, bv1)

  def testAndWithBitStringZeros(self):
    """And with a bitstring with zeros in the matching location."""
    self.assertEqual(int(bv1 & bv3), 0)

  def testAndEmptyString(self):
    """And with an empty bitstring."""
    self.assertEqual(int(bv1 & bv4), 0)

  def testAndWithSize0(self):
    """And with a size 0."""
    self.assertEqual(int(bv1 & bv5), 0)

  def testOrWithSomeOnes(self):
    """Or with overlapping ones in a bitlist."""
    expected = BitVector.BitVector(bitstring='11110011')
    self.assertEqual(bv1 | bv2, expected)

  def testOrWithBitStringZeros(self):
    """Or with a bitstring with zeros in the matching location."""
    expected = BitVector.BitVector(bitstring='00000000111111110110011')
    self.assertEqual(int(bv1 | bv3), int(expected))

  def testOrEmptyString(self):
    """Or with an empty bitstring."""
    self.assertEqual(int(bv1 | bv4), int(bv1))

  def testOrWithSize0(self):
    """Or with a size 0."""
    self.assertEqual(int(bv1 | bv5), int(bv1))

  def testBitWiseInversion(self):
    expected = BitVector.BitVector(bitstring='11001100')
    self.assertEqual(~bv1, expected)

  @unittest.skip('Some of these do not look like they are correct.')
  def testLogicOp(self):
    """Testing Boolean operators."""
    logic_tests = [
        ((bv1, bv2, '&'), '00110011'),
        ((bv1, bv3, '&'), ''),
        ((bv1, bv4, '&'), ''),
        ((bv1, bv5, '&'), ''),
        ((bv1, bv2, '|'), '11110011'),
        ((bv1, bv3, '|'), ''),
        ((bv1, bv4, '|'), ''),
        ((bv1, bv5, '|'), ''),
        ((bv1, '', '~'), '11001100'),
    ]

    for args, expected_str in logic_tests:
      op = args[2]
      if op == '&':
        actual = args[0] & args[1]
      elif op == '|':
        actual = args[0] | args[1]
      elif op == '~':
        actual = ~args[0]
      expected = BitVector.BitVector(bitstring=expected_str)
      self.assertEqual(int(actual), int(expected),
                       '%s != %s (%s)' % (actual, expected, expected_str))


if __name__ == '__main__':
  unittest.main()
