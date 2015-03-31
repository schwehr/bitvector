import unittest

import BitVector


class ComparisonTestCases(unittest.TestCase):

  def testComparisons(self):
    """Testing comparison operators."""
    bv1 = BitVector.BitVector(bitstring='00110011')
    bv2 = BitVector.BitVector(bitlist=[0, 0, 1, 1, 0, 0, 1, 1])
    bv3 = BitVector.BitVector(intVal=5678)

    comparison_tests = [
        ((bv1, bv2, '=='), True),
        ((bv1, bv2, '!='), False),
        ((bv1, bv2, '<'), False),
        ((bv1, bv2, '<='), True),
        ((bv1, bv3, '=='), False),
        ((bv3, bv1, '>'), True),
        ((bv3, bv1, '>='), True),
    ]
    for args, expected in comparison_tests:
      op = args[2]
      if op == '==':
        actual = args[0] == args[1]
      elif op == '!=':
        actual = args[0] != args[1]
      elif op == '<':
        actual = args[0] < args[1]
      elif op == '<=':
        actual = args[0] <= args[1]
      elif op == '==':
        actual = args[0] == args[1]
      elif op == '>':
        actual = args[0] > args[1]
      elif op == '>=':
        actual = args[0] >= args[1]
      self.assertEqual(expected, actual)


if __name__ == '__main__':
  unittest.main()
