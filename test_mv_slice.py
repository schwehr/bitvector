import mmap
import array
m = mmap.mmap(-1, 20)
v = memoryview(m).cast('H')
lpb = [1, 2, 3, 4, 5]
# test slice assignment
try:
    v[:len(lpb)] = array.array('H', lpb)
    print("Slice assignment works!")
    print(v[0], v[1], v[2])
except Exception as e:
    print("Slice assignment failed:", e)

# Also test len(v) vs len(lpb)
v[:] = array.array('H', [0]*10)
print(list(v))
