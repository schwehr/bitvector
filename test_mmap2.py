import mmap
import os
import array

m = mmap.mmap(-1, 200) # Anonymous mmap!
v = memoryview(m).cast('H')
v[0] = 0x1234
print(hex(v[0]))
v[1] = 0x5678
print(hex(v[1]))
m.close()
