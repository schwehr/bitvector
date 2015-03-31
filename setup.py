#!/usr/bin/env python

### setup.py

from distutils.core import setup

setup(name='BitVector',
      version='3.3.2',
      author='Avinash Kak',
      author_email='kak@purdue.edu',
      maintainer='Avinash Kak',
      maintainer_email='kak@purdue.edu',
      url='https://engineering.purdue.edu/kak/dist/BitVector-3.3.2.html',
      download_url='https://engineering.purdue.edu/kak/dist/BitVector-3.3.2.tar.gz',
      description='A pure-Python memory-efficient packed representation for bit arrays',
      long_description='''
This class presents a pure-Python memory-efficient packed 
representation for bit arrays.

**Version 3.3.2** has a bug fix for the case when you
construct a bit vector from a text string that includes
character escapes.

**Version 3.3.1** is a minor upgrade to make the syntax of
the API method declarations more uniform.  Previously, while
most of the method names used underscores to connect
multiple words, some used camelcasing.  Now all use
underscores.  For backward compatibility, the old calls will
continue to work.

**Version 3.3** includes one more constructor mode: You can
now construct a bit vector from the bytes data type.  This
version also includes a couple of bug fixes.

The class is provided with the following operators/methods:

-      __getitem__
-      __setitem__
-      __len__
-      __iter__
-      __contains__
-      __getslice__
-      __str__
-      __int__
-      __add__
-      __eq__, __ne__, __lt__, __le__, __gt__, __ge__
-      __or__
-      __and__
-      __xor__
-      __invert__
-      __lshift__
-      __rshift__
-      __add__
-      count_bits 
-      count_bits_sparse      (faster for sparse bit vectors)     
-      deep_copy
-      divide_into_two
-      gcd
-      gen_rand_bits_for_prime
-      get_hex_string_from_bitvector
-      get_text_from_bitvector
-      gf_divide              (for divisions in GF(2^n))
-      gf_MI                  (for multiplicative inverse in GF(2^n))
-      gf_multiply            (for multiplications in GF(2))
-      gf_multiply_modular    (for multiplications in GF(2^n))
-      hamming_distance
-      int_val                (for returning the integer value) 
-      is_power_of_2
-      is_power_of_2_sparse   (faster for sparse bit vectors)
-      jaccard_distance
-      jaccard_similarity
-      length                 
-      multiplicative_inverse
-      next_set_bit
-      pad_from_left
-      pad_from_right
-      permute
-      rank_of_bit_set_at_index
-      read_bits_from_file
-      reset
-      reverse
-      runs
-      shift_left             (for non-circular left shift)
-      shift_right            (for non-circular right shift)
-      slice assignment
-      set_value
-      test_for_primality
-      unpermute
-      write_to_file
-      write_bits_to_fileobject

          ''',
      license='Python Software Foundation License',
      keywords='bit array, bit vector, bit string, logical operations on bit fields',
      platforms='All platforms',
      classifiers=['Topic :: Utilities', 'Programming Language :: Python :: 2.7', 'Programming Language :: Python :: 3.2'],
      packages=['']
)
