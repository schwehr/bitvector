import io
import sys
import unittest

import BitVector


class ConstructorTest(unittest.TestCase):

  def testConstructors(self):
    """Testing constructors."""
    constructor_tests = [
        (('size', '0'), ''),
        (('size', '1'), '0'),
        (('bitlist', '(1,1,0,1)'), '1101'),
        (('bitlist', '[1,0,0,1]'), '1001'),
        (('intVal', '5678'), '1011000101110'),
        (('bitstring', '00110011'), '00110011'),
        (('streamobject', '111100001111'), '111100001111'),
    ]
    for args, expected in constructor_tests:
      mode = args[0]
      if mode == 'size':
        # pylint: disable=eval-used
        bitvec = BitVector.BitVector(size=eval(args[1]))
      elif mode == 'bitlist':
        # pylint: disable=eval-used
        bitvec = BitVector.BitVector(bitlist=eval(args[1]))
      elif mode == 'intVal':
        bitvec = BitVector.BitVector(intVal=int(args[1]))
      elif mode == 'bitstring':
        bitvec = BitVector.BitVector(bitstring=args[1])
      elif mode == 'streamobject':
        fp_read = None
        if sys.version_info[0] == 3:
          fp_read = io.StringIO(args[1])
        else:
          fp_read = io.StringIO(unicode(args[1]))
        bitvec = BitVector.BitVector(fp=fp_read)
      elif mode == 'filename':
        bvec = BitVector.BitVector(filename=args[1])
        bitvec = bvec.read_bits_from_file(64)
      else:
        self.assertFalse(True)
      actual = str(bitvec)
      self.assertEqual(actual, expected)


if __name__ == '__main__':
  unittest.main()
