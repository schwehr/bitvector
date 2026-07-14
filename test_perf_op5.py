import mmap
import timeit
import array

setup = """
import array
import mmap
a1 = array.array('H', [0]*1000)
a2 = array.array('H', [0]*1000)

m1_mmap = mmap.mmap(-1, 2000)
m1 = memoryview(m1_mmap).cast('H')

m2_mmap = mmap.mmap(-1, 2000)
m2 = memoryview(m2_mmap).cast('H')

import operator
"""
print("array.array list(map(and_)):", timeit.timeit("list(map(operator.__and__, a1, a2))", setup=setup, number=10000))
print("memoryview list(map(and_)):", timeit.timeit("list(map(operator.__and__, m1, m2))", setup=setup, number=10000))
