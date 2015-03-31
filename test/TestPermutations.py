import unittest

import BitVector


class PermutationTestCase(unittest.TestCase):

  def testPermutations(self):
    bv1 = BitVector.BitVector(bitlist=[1, 0, 0, 1, 1, 0, 1])
    bv2 = BitVector.BitVector(bitlist=[1, 0, 1, 0, 0, 1, 1])

    permutation_tests = [
        ((bv1, 'permute', '6201543'), '1010011'),
        ((bv2, 'unpermute', '6201543'), '1001101'),
    ]
    for args, expected in permutation_tests:
      if args[1] == 'permute':
        actual = args[0].permute([int(x) for x in args[2]])
      elif args[1] == 'unpermute':
        actual = args[0].unpermute([int(x) for x in args[2]])
      self.assertEqual(actual, BitVector.BitVector(bitstring=expected))


if __name__ == '__main__':
  unittest.main()
