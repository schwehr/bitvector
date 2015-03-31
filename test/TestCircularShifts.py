import unittest

import BitVector


class CircularShiftTest(unittest.TestCase):

  def testCircularShifts(self):
    """Testing circular shifts."""
    bv = BitVector.BitVector(bitstring='00110011')

    circular_shift_tests = [
        ((3, '>>'), '01100110'),
        ((3, '<<'), '10011001'),
    ]

    for args, expected in circular_shift_tests:
      op = args[1]
      if op == '>>':
        actual = BitVector.BitVector(bitstring=str(bv))
        actual >> args[0]
      elif op == '<<':
        actual = BitVector.BitVector(bitstring=str(bv))
        actual << args[0]
      self.assertEqual(actual, BitVector.BitVector(bitstring=expected))


if __name__ == '__main__':
  unittest.main()
