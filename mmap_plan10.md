Let's review `BitVector.__add__`:
```python
        new_bv = BitVector(size=0)
        new_bv.size = self.size
        if isinstance(self.vector, array.array) and isinstance(
            new_bv.vector, array.array
        ):
            new_bv.vector.frombytes(self.vector.tobytes())
        elif isinstance(self.vector, list):
            new_bv.vector = self.vector.copy()
        else:
            raise ValueError("vector must be an array or list")
        two_byte_ints_to_add = (self.size + other.size + 15) // 16 - len(self.vector)
        new_bv.vector.extend([0] * two_byte_ints_to_add)

        # shifting logic:
        # (shifting logic uses new_bv.size to know where to start)
```

If I change this to:
```python
        new_bv = self.__class__(size=0)
        new_bv.size = self.size
        new_bv._set_vector(self.vector)
        two_byte_ints_to_add = (self.size + other.size + 15) // 16 - len(self.vector)
        new_bv._extend_vector(two_byte_ints_to_add)
```
This is fully compatible, as long as `_set_vector` creates a copy and `_extend_vector` works!
For `MmapBitVector`:
```python
class MmapBitVector(BitVector):
    def _set_vector(self, new_vec):
        if self._mmap:
            self._mmap.close()
        # allocate a new mmap for the size of new_vec
        ints_needed = len(new_vec)
        if ints_needed > 0:
            self._mmap = mmap.mmap(-1, ints_needed * 2)
            self.vector = memoryview(self._mmap).cast('H')
            self.vector[:] = new_vec
        else:
            self._mmap = None
            self.vector = []

    def _extend_vector(self, ints_to_add: int):
        if ints_to_add > 0:
            old_ints = len(self.vector)
            new_ints = old_ints + ints_to_add
            new_mmap = mmap.mmap(-1, new_ints * 2)
            new_vec = memoryview(new_mmap).cast('H')
            if old_ints > 0:
                new_vec[:old_ints] = self.vector
                self._mmap.close()
            self._mmap = new_mmap
            self.vector = new_vec
```
This is extremely elegant and handles everything! `__add__` will just call `_set_vector` (which reallocates if needed) and then `_extend_vector` (which reallocates again). Not perfectly efficient (2 reallocations), but correct!
Wait, `BitVector`'s current `__add__` uses `self.vector.extend([0] * ...)` which works fine for `array.array`.
So if I implement `_set_vector` and `_extend_vector` on `BitVector` as default implementations, and override them in `MmapBitVector`, it's flawless.
