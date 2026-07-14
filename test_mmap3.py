import mmap
import os

m = mmap.mmap(-1, 200) # Anonymous mmap!
m.close()
