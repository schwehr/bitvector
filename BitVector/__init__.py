#!/usr/bin/env python
# Copyright: (C) 2014 Avinash Kak. Python Software Foundation.

"""Memory-efficient packed representation of bit arrays."""

import array
import binascii
import functools
import operator
import random
import sys

__version__ = '3.3.2'

_hexdict = {
    '0' : '0000', '1' : '0001', '2' : '0010', '3' : '0011',
    '4' : '0100', '5' : '0101', '6' : '0110', '7' : '0111',
    '8' : '1000', '9' : '1001', 'a' : '1010', 'b' : '1011',
    'c' : '1100', 'd' : '1101', 'e' : '1110', 'f' : '1111' }


def _readblock(blocksize, bitvector):
    global _hexdict
    bitstring = ''
    i = 0
    while i < blocksize / 8:
        i += 1
        byte = bitvector.FILEIN.read(1)
        if byte == b'':
            if len(bitstring) < blocksize:
                bitvector.more_to_read = False
            return bitstring
        if sys.version_info[0] == 3:
            hexvalue = '%02x' % byte[0]
        else:
            hexvalue = hex(ord(byte))
            hexvalue = hexvalue[2:]
            if len(hexvalue) == 1:
                hexvalue = '0' + hexvalue
        bitstring += _hexdict[hexvalue[0]]
        bitstring += _hexdict[hexvalue[1]]
    file_pos = bitvector.FILEIN.tell()
    # Peek at the next byte; moves file position only if a
    # byte is read.
    next_byte = bitvector.FILEIN.read(1)
    if next_byte:
        # Pretend we never read the byte.
        bitvector.FILEIN.seek(file_pos)
    else:
        bitvector.more_to_read = False
    return bitstring


class BitVector(object):

    def __init__(self, *args, **kwargs):
        if args:
            raise ValueError(
                'BitVector constructor can only be called with '
                'keyword arguments for the following keywords: '
                'filename, fp, size, intVal, bitlist, bitstring, '
                'hexstring, textstring, and rawbytes)')
        allowed_keys = ('bitlist', 'bitstring', 'filename', 'fp', 'intVal',
                        'size', 'textstring', 'hexstring', 'rawbytes')
        keywords_used = kwargs.keys()
        for keyword in keywords_used:
            if keyword not in allowed_keys:
                raise ValueError('Wrong keyword used --- check spelling')
        filename = fp = intVal = size = bitlist = None
        bitstring = textstring = hexstring = rawbytes = None
        if 'filename' in kwargs   : filename=kwargs.pop('filename')
        if 'fp' in kwargs         : fp = kwargs.pop('fp')
        if 'size' in kwargs       : size = kwargs.pop('size')
        if 'intVal' in kwargs     : intVal = kwargs.pop('intVal')
        if 'bitlist' in kwargs    : bitlist = kwargs.pop('bitlist')
        if 'bitstring' in kwargs  : bitstring = kwargs.pop('bitstring')
        if 'hexstring' in kwargs  : hexstring = kwargs.pop('hexstring')
        if 'textstring' in kwargs : textstring = kwargs.pop('textstring')
        if 'rawbytes' in kwargs   : rawbytes = kwargs.pop('rawbytes')
        self.filename = None
        self.size = 0
        self.FILEIN = None
        self.FILEOUT = None
        if filename:
            if (fp or size or intVal or bitlist or bitstring or hexstring
                or textstring or rawbytes):
                raise ValueError('When filename is specified, you cannot give '
                                 'values to any other constructor args')
            self.filename = filename
            self.FILEIN = open(filename, 'rb')
            self.more_to_read = True
            return
        elif fp:
            if (filename or size or intVal or bitlist or bitstring or hexstring
                or textstring or rawbytes):
                raise ValueError('When fileobject is specified, you cannot '
                                 'give values to any other constructor args')
            bits = self.read_bits_from_fileobject(fp)
            bitlist =  list(map(int, bits))
            self.size = len(bitlist)
        elif intVal or intVal == 0:
            if (filename or fp or bitlist or bitstring or hexstring
                or textstring or rawbytes):
                raise ValueError('When intVal is specified, you can only give '
                                 'a value to the \'size\' constructor arg')
            if intVal == 0:
                bitlist = [0]
                if size is None:
                    self.size = 1
                elif size == 0:
                    raise ValueError('The value specified for size must be at '
                                     'least as large as for the smallest bit '
                                     'vector possible for intVal')
                else:
                    if size < len(bitlist):
                        raise ValueError(
                            'The value specified for size must be at least as '
                            'large as for the smallest bit vector possible for '
                            'intVal')
                    n = size - len(bitlist)
                    bitlist = [0]*n + bitlist
                    self.size = len(bitlist)
            else:
                hexVal = hex(intVal).lower().rstrip('l')
                hexVal = hexVal[2:]
                if len(hexVal) == 1:
                    hexVal = '0' + hexVal
                bitlist = ''.join(map(lambda x: _hexdict[x],hexVal))
                bitlist = list(map(int, bitlist))
                i = 0
                while i < len(bitlist):
                    if bitlist[i] == 1: break
                    i += 1
                del bitlist[0:i]
                if size is None:
                    self.size = len(bitlist)
                elif size == 0:
                    if size < len(bitlist):
                        raise ValueError(
                            'The value specified for size must be at least as '
                            'large as for the smallest bit vector possible '
                            'for intVal')
                else:
                    if size < len(bitlist):
                        raise ValueError(
                            'The value specified for size must be at least as '
                            'large as for the smallest bit vector possible '
                            'for intVal')
                    n = size - len(bitlist)
                    bitlist = [0]*n + bitlist
                    self.size = len(bitlist)
        elif size is not None and size >= 0:
            if (filename or fp or intVal or bitlist or bitstring or hexstring
                or textstring or rawbytes):
                raise ValueError(
                    'When size is specified (without an intVal), you cannot '
                    'give values to any other constructor args')
            self.size = size
            two_byte_ints_needed = (size + 15) // 16
            self.vector = array.array('H', [0]*two_byte_ints_needed)
            return
        elif bitstring or bitstring == '':
            if (filename or fp or size or intVal or bitlist or hexstring
                or textstring or rawbytes):
                raise ValueError(
                    'When a bitstring is specified, you cannot give '
                    'values to any other constructor args')
            bitlist =  list(map(int, list(bitstring)))
            self.size = len(bitlist)
        elif bitlist:
            if (filename or fp or size or intVal or bitstring or hexstring
                or textstring or rawbytes):
                raise ValueError(
                    'When bits are specified, you cannot give values '
                    'to any other constructor args')
            self.size = len(bitlist)
        elif textstring or textstring == '':
            if (filename or fp or size or intVal or bitlist or bitstring
                or hexstring or rawbytes):
                raise ValueError(
                    'When bits are specified through textstring, you '
                    'cannot give values to any other constructor args')
            hexlist = ''.join(map(lambda x: x[2:], map(lambda x: hex(x) if len(hex(x)[2:])==2
                                 else hex(x)[:2] + '0' + hex(x)[2:], map(ord, list(textstring)))))
            bitlist = list(map(int,list(''.join(map(lambda x: _hexdict[x], list(hexlist))))))
            self.size = len(bitlist)
        elif hexstring or hexstring == '':
            if filename or fp or size or intVal or bitlist or bitstring or textstring or rawbytes:
                raise ValueError('When bits are specified through hexstring, you '
                                 'cannot give values to any other constructor args')
            bitlist = list(map(int,list(''.join(map(lambda x: _hexdict[x], list(hexstring))))))
            self.size = len(bitlist)
        elif rawbytes:
            if (filename or fp or size or intVal or bitlist or bitstring
                or textstring or hexstring):
                raise ValueError(
                    'When bits are specified through rawbytes, you '
                    'cannot give values to any other constructor args')
            hexlist = binascii.hexlify(rawbytes)
            if sys.version_info[0] == 3:
                bitlist = list(
                    map(int,
                        list(''.join(map(lambda x: _hexdict[x],
                                         list(map(chr,list(hexlist))))))))
            else:
                bitlist = list(
                    map(int,
                        list(''.join(map(lambda x: _hexdict[x],
                                         list(hexlist))))))
            self.size = len(bitlist)
        else:
            raise ValueError('wrong arg(s) for constructor')
        two_byte_ints_needed = (len(bitlist) + 15) // 16
        self.vector = array.array('H', [0]*two_byte_ints_needed)
        list(map(self._setbit, range(len(bitlist)), bitlist))

    def _setbit(self, posn, val):
        'Set the bit at the designated position to the value shown'
        if val not in (0, 1):
            raise ValueError('incorrect value for a bit')
        if isinstance(posn, tuple):
            posn = posn[0]
        if  posn >= self.size or posn < -self.size:
            raise ValueError('index range error')
        if posn < 0: posn = self.size + posn
        block_index = posn // 16
        shift = posn & 15
        cv = self.vector[block_index]
        if (cv >> shift) & 1 != val:
            self.vector[block_index] = cv ^ (1 << shift)

    def _getbit(self, pos):
        'Get the bit from the designated position'
        if not isinstance(pos, slice):
            if  pos >= self.size or pos < -self.size:
                raise ValueError('index range error')
            if pos < 0: pos = self.size + pos
            return (self.vector[pos//16] >> (pos & 15)) & 1
        else:
            bitstring = ''
            if pos.start is None:
                start = 0
            else:
                start = pos.start
            if pos.stop is None:
                stop = self.size
            else:
                stop = pos.stop
            for i in range(start, stop):
                bitstring += str(self[i])
            return BitVector(bitstring = bitstring)

    def __xor__(self, other):
        if self.size < other.size:
            bv1 = self._resize_pad_from_left(other.size - self.size)
            bv2 = other
        elif self.size > other.size:
            bv1 = self
            bv2 = other._resize_pad_from_left(self.size - other.size)
        else:
            bv1 = self
            bv2 = other
        res = BitVector(size = bv1.size)
        lpb = map(operator.__xor__, bv1.vector, bv2.vector)
        res.vector = array.array('H', lpb)
        return res

    def __and__(self, other):
        if self.size < other.size:
            bv1 = self._resize_pad_from_left(other.size - self.size)
            bv2 = other
        elif self.size > other.size:
            bv1 = self
            bv2 = other._resize_pad_from_left(self.size - other.size)
        else:
            bv1 = self
            bv2 = other
        res = BitVector(size = bv1.size)
        lpb = map(operator.__and__, bv1.vector, bv2.vector)
        res.vector = array.array('H', lpb)
        return res

    def __or__(self, other):
        if self.size < other.size:
            bv1 = self._resize_pad_from_left(other.size - self.size)
            bv2 = other
        elif self.size > other.size:
            bv1 = self
            bv2 = other._resize_pad_from_left(self.size - other.size)
        else:
            bv1 = self
            bv2 = other
        res = BitVector(size = bv1.size)
        lpb = map(operator.__or__, bv1.vector, bv2.vector)
        res.vector = array.array('H', lpb)
        return res

    def __invert__(self):
        res = BitVector(size = self.size)
        lpb = list(map(operator.__inv__, self.vector))
        res.vector = array.array('H')
        for i in range(len(lpb)):
            res.vector.append(lpb[i] & 0x0000FFFF)
        return res

    def __add__(self, other):
        i = 0
        outlist = []
        while i < self.size:
            outlist.append(self[i])
            i += 1
        i = 0
        while i < other.size:
            outlist.append(other[i])
            i += 1
        return BitVector(bitlist = outlist)

    def _getsize(self):
        return self.size

    def read_bits_from_file(self, blocksize):
        if not self.filename:
            raise SyntaxError('You need to first construct a BitVector '
                'object with a filename as argument')
        if blocksize % 8 != 0:
            raise ValueError('block size must be a multiple of 8')
        bitstr = _readblock(blocksize, self)
        if len(bitstr) == 0:
            return BitVector(size = 0)
        else:
            return BitVector(bitstring = bitstr)

    def read_bits_from_fileobject(self, fp):
        bitlist = []
        while 1:
            bit = fp.read()
            if bit == '': return bitlist
            bitlist += bit

    def write_bits_to_fileobject(self, fp):
        for bit_index in range(self.size):
            if sys.version_info[0] == 3:
                if self[bit_index] == 0:
                    fp.write('0')
                else:
                    fp.write('1')
            else:
                if self[bit_index] == 0:
                    fp.write(u'0')
                else:
                    fp.write(u'1')

    def divide_into_two(self):
        if self.size % 2 != 0:
            raise ValueError('must have even num bits')
        i = 0
        outlist1 = []
        while i < self.size / 2:
            outlist1.append(self[i])
            i += 1
        outlist2 = []
        while i < self.size:
            outlist2.append(self[i])
            i += 1
        return [BitVector(bitlist = outlist1),
                BitVector(bitlist = outlist2)]

    def permute(self, permute_list):
        if max(permute_list) > self.size -1:
            raise ValueError('Bad permutation index')
        outlist = []
        i = 0
        while i < len(permute_list):
            outlist.append(self[permute_list[i]])
            i += 1
        return BitVector(bitlist = outlist)

    def unpermute(self, permute_list):
        if max(permute_list) > self.size -1:
            raise ValueError('Bad permutation index')
        if self.size != len(permute_list):
            raise ValueError('Bad size for permute list')
        out_bv = BitVector(size = self.size)
        i = 0
        while i < len(permute_list):
            out_bv[permute_list[i]] = self[i]
            i += 1
        return out_bv

    def write_to_file(self, file_out):
        if not self.FILEOUT:
            self.FILEOUT = file_out
        if self.size % 8:
            raise ValueError(
                'Only a bit vector whose length is a multiple of 8 can '
                'be written to a file.  Use the padding functions to satisfy '
                'this constraint.')
        for byte in range(int(self.size / 8)):
            value = 0
            for bit in range(8):
                value += (self._getbit(byte * 8 + (7 - bit)) << bit)
            if sys.version_info[0] == 3:
                file_out.write(bytes(chr(value), 'utf-8'))
            else:
                file_out.write(chr(value))

    def close_file_object(self):
        if not self.FILEIN:
            raise SyntaxError('No associated open file')
        self.FILEIN.close()

    def int_val(self):
        intVal = 0
        for i in range(self.size):
            intVal += self[i] * (2 ** (self.size - i - 1))
        return intVal

    intValue = int_val

    def get_text_from_bitvector(self):
        if self.size % 8:
            raise ValueError('The bitvector for get_text_from_bitvector() '
                             'must be an integral multiple of 8 bits')
        return ''.join(
            map(chr, map(int,[self[i:i+8] for i in range(0, self.size, 8)])))

    def get_hex_string_from_bitvector(self):
        if self.size % 4:
            raise ValueError(
                'The bitvector for get_hex_string_from_bitvector() '
                'must be an integral multiple of 4 bits')
        return ''.join(map(lambda x: x.replace('0x',''),
                       map(hex,
                           map(int,
                               [self[i:i+4] for i in range(0, self.size, 4)]))))

    def __lshift__(self, n):
        if self.size == 0:
            raise ValueError('Circular shift of an empty vector '
                             'makes no sense')
        if n < 0:
            return self >> abs(n)
        for i in range(n):
            self.circular_rotate_left_by_one()
        return self

    def __rshift__(self, n):
        if self.size == 0:
            raise ValueError('Circular shift of an empty vector '
                             'makes no sense')
        if n < 0:
            return self << abs(n)
        for i in range(n):
            self.circular_rotate_right_by_one()
        return self

    def circular_rotate_left_by_one(self):
        size = len(self.vector)
        bitstring_leftmost_bit = self.vector[0] & 1
        left_most_bits = list(map(operator.__and__, self.vector, [1]*size))
        left_most_bits.append(left_most_bits[0])
        del(left_most_bits[0])
        self.vector = list(map(operator.__rshift__, self.vector, [1]*size))
        self.vector = list(
            map(operator.__or__, self.vector,
                list(map(operator.__lshift__, left_most_bits, [15]*size))))

        self._setbit(self.size -1, bitstring_leftmost_bit)

    def circular_rotate_right_by_one(self):
        size = len(self.vector)
        bitstring_rightmost_bit = self[self.size - 1]
        right_most_bits = list(map(operator.__and__,
                               self.vector, [0x8000] * size))
        self.vector = list(map(operator.__and__, self.vector, [~0x8000]*size))
        right_most_bits.insert(0, bitstring_rightmost_bit)
        right_most_bits.pop()
        self.vector = list(map(operator.__lshift__, self.vector, [1]*size))
        self.vector = list(
            map(operator.__or__, self.vector,
                list(map(operator.__rshift__, right_most_bits, [15]*size))))

        self._setbit(0, bitstring_rightmost_bit)

    def circular_rot_left(self):
        max_index = (self.size -1) // 16
        left_most_bit = self.vector[0] & 1
        self.vector[0] = self.vector[0] >> 1
        for i in range(1, max_index + 1):
            left_bit = self.vector[i] & 1
            self.vector[i] = self.vector[i] >> 1
            self.vector[i-1] |= left_bit << 15
        self._setbit(self.size -1, left_most_bit)

    def circular_rot_right(self):
        max_index = (self.size -1) // 16
        right_most_bit = self[self.size - 1]
        self.vector[max_index] &= ~0x8000
        self.vector[max_index] = self.vector[max_index] << 1
        for i in range(max_index-1, -1, -1):
            right_bit = self.vector[i] & 0x8000
            self.vector[i] &= ~0x8000
            self.vector[i] = self.vector[i] << 1
            self.vector[i+1] |= right_bit >> 15
        self._setbit(0, right_most_bit)

    def shift_left_by_one(self):
        size = len(self.vector)
        left_most_bits = list(map(operator.__and__, self.vector, [1]*size))
        left_most_bits.append(left_most_bits[0])
        del(left_most_bits[0])
        self.vector = list(map(operator.__rshift__, self.vector, [1]*size))
        self.vector = list(
            map(operator.__or__, self.vector,
            list(map(operator.__lshift__, left_most_bits, [15]*size))))
        self._setbit(self.size -1, 0)

    def shift_right_by_one(self):
        size = len(self.vector)
        right_most_bits = list(
            map(operator.__and__, self.vector, [0x8000]*size))
        self.vector = list(map(operator.__and__, self.vector, [~0x8000]*size))
        right_most_bits.insert(0, 0)
        right_most_bits.pop()
        self.vector = list(map(operator.__lshift__, self.vector, [1]*size))
        self.vector = list(
            map(operator.__or__, self.vector,
                list(map(operator.__rshift__,right_most_bits, [15]*size))))
        self._setbit(0, 0)

    def shift_left(self, n):
        for i in range(n):
            self.shift_left_by_one()
        return self

    def shift_right(self, n):
        for i in range(n):
            self.shift_right_by_one()
        return self

    # Allow array like subscripting for getting and setting:
    __getitem__ = _getbit

    def __setitem__(self, pos, item):
        if isinstance(pos, slice):
            if not isinstance(item, BitVector):
                raise TypeError('For slice assignment, '
                    'the right hand side must be a BitVector')
            if not pos.start and not pos.stop:
                return item.deep_copy()
            elif not pos.start:
                if pos.stop != len(item):
                    raise ValueError(
                        'incompatible lengths for slice assignment')
                for i in range(pos.stop):
                    self[i] = item[i]
                return
            elif not pos.stop:
                if ((len(self) - pos.start) != len(item)):
                    raise ValueError(
                        'incompatible lengths for slice assignment')
                for i in range(len(item)-1):
                    self[pos.start + i] = item[i]
                return
            else:
                if ((pos.stop - pos.start) != len(item)):
                    raise ValueError(
                        'incompatible lengths for slice assignment')
                for i in range(pos.start, pos.stop):
                    self[i] = item[i - pos.start]
                return
        # For index assignment use _setbit()
        self._setbit(pos, item)

    def __getslice__(self, i, j):
        'Fetch slices with [i:j], [:], etc.'
        if self.size == 0:
            return BitVector(bitstring = '')
        if i == j:
            return BitVector(bitstring = '')
        slicebits = []
        if j > self.size: j = self.size
        for x in range(i,j):
            slicebits.append(self[x])
        return BitVector(bitlist = slicebits)

    __len__ = _getsize
    __int__ = int_val

    def __iter__(self):
        return BitVectorIterator(self)

    def __str__(self):
        if self.size == 0:
            return ''
        return ''.join(map(str, self))

    def __eq__(self, other):
        if self.size != other.size:
            return False
        i = 0
        while i < self.size:
            if self[i] != other[i]: return False
            i += 1
        return True

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return self.intValue() < other.intValue()

    def __le__(self, other):
        return self.intValue() <= other.intValue()

    def __gt__(self, other):
        return self.intValue() > other.intValue()

    def __ge__(self, other):
        return self.intValue() >= other.intValue()

    def deep_copy(self):
        copy = str(self)
        return BitVector(bitstring = copy)

    def _resize_pad_from_left(self, n):
        new_str = '0'*n + str(self)
        return BitVector(bitstring = new_str)

    def _resize_pad_from_right(self, n):
        new_str = str(self) + '0' * n
        return BitVector(bitstring = new_str)

    def pad_from_left(self, n):
        new_str = '0' * n + str(self)
        bitlist = list(map(int, list(new_str)))
        self.size = len(bitlist)
        two_byte_ints_needed = (len(bitlist) + 15) // 16
        self.vector = array.array('H', [0]*two_byte_ints_needed)
        list(map(self._setbit, enumerate(bitlist), bitlist))

    def pad_from_right(self, n):
        new_str = str(self) + '0'*n
        bitlist =  list(map(int, list(new_str)))
        self.size = len(bitlist)
        two_byte_ints_needed = (len(bitlist) + 15) // 16
        self.vector = array.array('H', [0]*two_byte_ints_needed)
        list(map(self._setbit, enumerate(bitlist), bitlist))

    def __contains__(self, otherBitVec):
        if self.size == 0:
              raise ValueError('First arg bitvec has no bits')
        elif self.size < otherBitVec.size:
              raise ValueError('First arg bitvec too short')
        max_index = self.size - otherBitVec.size + 1
        for i in range(max_index):
              if self[i:i+otherBitVec.size] == otherBitVec:
                    return True
        return False

    def reset(self, val):
        if val not in (0,1):
            raise ValueError('Incorrect reset argument')
        bitlist = [val for i in range(self.size)]
        list(map(self._setbit, enumerate(bitlist), bitlist))
        return self

    def count_bits(self):
        return functools.reduce(lambda x, y: int(x)+int(y), self)

    def set_value(self, *args, **kwargs):
        self.__init__(*args, **kwargs)

    def count_bits_sparse(self):
        num = 0
        for intval in self.vector:
            if intval == 0: continue
            c = 0; iv = intval
            while iv > 0:
                iv = iv & (iv -1)
                c = c + 1
            num = num + c
        return num

    def jaccard_similarity(self, other):
        assert self.intValue() > 0 or other.intValue() > 0, (
            'Jaccard called on two zero vectors --- NOT ALLOWED')
        assert self.size == other.size, 'vectors of unequal length'
        intersect = self & other
        union = self | other
        return (intersect.count_bits_sparse()
                / float(union.count_bits_sparse()))

    def jaccard_distance(self, other):
        assert self.size == other.size, 'vectors of unequal length'
        return 1 - self.jaccard_similarity(other)

    def hamming_distance(self, other):
        assert self.size == other.size, 'vectors of unequal length'
        diff = self ^ other
        return diff.count_bits_sparse()

    def next_set_bit(self, from_index=0):
        assert from_index >= 0, 'from_index must be nonnegative'
        i = from_index
        v = self.vector
        l = len(v)
        o = i >> 4
        s = i & 0x0F
        i = o << 4
        while o < l:
            h = v[o]
            if h:
                i += s
                m = 1 << s
                while m != (1 << 0x10):
                    if h & m: return i
                    m <<= 1
                    i += 1
            else:
                i += 0x10
            s = 0
            o += 1
        return -1

    def rank_of_bit_set_at_index(self, position):
        assert self[position] == 1, 'the arg bit not set'
        bv = self[0:position+1]
        return bv.count_bits()

    def is_power_of_2(self):
        if self.intValue() == 0: return False
        bv = self & BitVector(intVal = self.intValue() - 1)
        if bv.intValue() == 0: return True
        return False

    isPowerOf2 = is_power_of_2

    def is_power_of_2_sparse(self):
        if self.count_bits_sparse() == 1: return True
        return False

    isPowerOf2_sparse = is_power_of_2_sparse

    def reverse(self):
        reverseList = []
        i = 1
        while i < self.size + 1:
            reverseList.append(self[-i])
            i += 1
        return BitVector(bitlist = reverseList)

    def gcd(self, other):
        a = self.intValue()
        b = other.intValue()
        if a < b: a,b = b,a
        while b != 0:
            a, b = b, a % b
        return BitVector(intVal = a)

    def multiplicative_inverse(self, modulus):
        MOD = mod = modulus.intValue(); num = self.intValue()
        x, x_old = 0, 1
        y, y_old = 1, 0
        while mod:
            quotient = num // mod
            num, mod = mod, num % mod
            x, x_old = x_old - x * quotient, x
            y, y_old = y_old - y * quotient, y
        if num != 1:
            return None
        else:
            MI = (x_old + MOD) % MOD
            return BitVector(intVal = MI)

    def length(self):
        return self.size

    def gf_multiply(self, b):
        a = self.deep_copy()
        b_copy = b.deep_copy()
        a_highest_power = a.length() - a.next_set_bit(0) - 1
        b_highest_power = b.length() - b_copy.next_set_bit(0) - 1
        result = BitVector(size = a.length()+b_copy.length())
        a.pad_from_left(result.length() - a.length())
        b_copy.pad_from_left(result.length() - b_copy.length())
        for i,bit in enumerate(b_copy):
            if bit == 1:
                power = b_copy.length() - i - 1
                a_copy = a.deep_copy()
                a_copy.shift_left(power)
                result ^=  a_copy
        return result


    def gf_divide(self, mod, n):
        num = self
        if mod.length() > n+1:
            raise ValueError('Modulus bit pattern too long')
        quotient = BitVector(intVal = 0, size = num.length())
        remainder = num.deep_copy()
        i = 0
        while 1:
            i = i+1
            if i == num.length(): break
            mod_highest_power = mod.length()-mod.next_set_bit(0)-1
            if remainder.next_set_bit(0) == -1:
                remainder_highest_power = 0
            else:
                remainder_highest_power = (
                    remainder.length() - remainder.next_set_bit(0) - 1)
            if remainder_highest_power < mod_highest_power:
                break
            if int(remainder) == 0:
                break
            exponent_shift = remainder_highest_power - mod_highest_power
            quotient[quotient.length()-exponent_shift-1] = 1
            quotient_mod_product = mod.deep_copy();
            quotient_mod_product.pad_from_left(remainder.length()
                                               - mod.length())
            quotient_mod_product.shift_left(exponent_shift)
            remainder = remainder ^ quotient_mod_product
        if remainder.length() > n:
            remainder = remainder[remainder.length()-n:]
        return quotient, remainder

    def gf_multiply_modular(self, b, mod, n):
        a = self
        a_copy = a.deep_copy()
        b_copy = b.deep_copy()
        product = a_copy.gf_multiply(b_copy)
        quotient, remainder = product.gf_divide(mod, n)
        return remainder

    def gf_MI(self, mod, n):
        num = self
        NUM = num.deep_copy(); MOD = mod.deep_copy()
        x = BitVector(size=mod.length())
        x_old = BitVector(intVal=1, size=mod.length())
        y = BitVector(intVal=1, size=mod.length())
        y_old = BitVector(size=mod.length())
        while int(mod):
            quotient, remainder = num.gf_divide(mod, n)
            num, mod = mod, remainder
            x, x_old = x_old ^ quotient.gf_multiply(x), x
            y, y_old = y_old ^ quotient.gf_multiply(y), y
        if int(num) != 1:
            return ('NO MI. However, the GCD of ', str(NUM), ' and ',
                                 str(MOD), ' is ', str(num))
        else:
            z = x_old ^ MOD
            quotient, remainder = z.gf_divide(MOD, n)
            return remainder

    def runs(self):
        if self.size == 0:
            raise ValueError('An empty vector has no runs')
        allruns = []
        run = ''
        previous_bit = self[0]
        if previous_bit == 0:
            run = '0'
        else:
            run = '1'
        for bit in list(self)[1:]:
            if bit == 0 and previous_bit == 0:
                run += '0'
            elif bit == 1 and previous_bit == 0:
                allruns.append(run)
                run = '1'
            elif bit == 0 and previous_bit == 1:
                allruns.append(run)
                run = '0'
            else:
                run += '1'
            previous_bit = bit
        allruns.append(run)
        return allruns

    def test_for_primality(self):
        p = int(self)
        probes = [2, 3, 5, 7, 11, 13, 17]
        if p in probes:
            return 1
        if any([p % a == 0 for a in probes]):
            return 0
        k, q = 0, p-1
        while not q&1:
            q >>= 1
            k += 1
        for a in probes:
            a_raised_to_q = pow(a, q, p)
            if a_raised_to_q == 1 or a_raised_to_q == p-1:
                continue
            a_raised_to_jq = a_raised_to_q
            primeflag = 0
            for j in range(k-1):
                a_raised_to_jq = pow(a_raised_to_jq, 2, p)
                if a_raised_to_jq == p-1:
                    primeflag = 1
                    break
            if not primeflag:
                return 0
        probability_of_prime = 1 - 1.0/(4 ** len(probes))
        return probability_of_prime

    def gen_rand_bits_for_prime(self, width):
        candidate = random.getrandbits(width)
        candidate |= 1
        candidate |= (1 << width-1)
        candidate |= (2 << width-3)
        return BitVector(intVal = candidate)


class BitVectorIterator:

    def __init__(self, bitvec):
        self.items = []
        for i in range(bitvec.size):
            self.items.append(bitvec._getbit(i))
        self.index = -1

    def __iter__(self):
        return self

    def next(self):
        self.index += 1
        if self.index < len(self.items):
            return self.items[self.index]
        else:
            raise StopIteration

    __next__ = next
