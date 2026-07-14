Wait, `__add__` has this:
```python
        if isinstance(self.vector, array.array) and isinstance(
            new_bv.vector, array.array
        ):
            new_bv.vector.frombytes(self.vector.tobytes())
        elif isinstance(self.vector, list):
            new_bv.vector = self.vector.copy()
```
If we use `_copy_vector` or `_allocate_vector`, we must make sure `__add__` correctly handles appending.
In `__add__`:
```python
        new_bv = self.__class__(size=0)
        new_bv.size = self.size
        # To copy:
        new_bv._allocate_vector((self.size + 15) // 16)
        if hasattr(self.vector, "tobytes") and hasattr(new_bv.vector, "frombytes"):
            # Wait, memoryview has tobytes but NOT frombytes.
            pass
```

Wait, the current code for `__add__`:
```python
        new_bv = BitVector(size=0)
        new_bv.size = self.size
        if isinstance(self.vector, array.array) and isinstance(
            new_bv.vector, array.array
        ):
            new_bv.vector.frombytes(self.vector.tobytes())
        elif isinstance(self.vector, list):
            new_bv.vector = self.vector.copy()
```
If `new_bv.vector` is a memoryview, how do we append to it?
Well, memoryview cannot grow! You can't `.extend()` a memoryview.
So `__add__` and `__iadd__` on MmapBitVector is problematic because the mmap has a fixed size.
Wait, `mmap.mmap(-1, ...)` can actually be resized! `mmap.resize(new_size)`. However, `mmap.resize()` on anonymous mappings (`-1`) only works on Linux? No, anonymous mmap resize is typically not supported or dangerous.
Actually, if `__add__` returns a NEW `MmapBitVector`, we can just instantiate it with the NEW size!
```python
        new_size = self.size + other.size
        new_bv = self.__class__(size=new_size)
        # copy bits from self and other
        new_bv[:self.size] = self
        new_bv[self.size:] = other
```
Wait, `__add__` currently tries to append `array.array` which grows it dynamically. `__iadd__` also grows it.
Let's look at `__add__`:
```python
        new_bv = BitVector(size=0)
        new_bv.size = self.size
        if isinstance(self.vector, array.array) and isinstance(
            new_bv.vector, array.array
        ):
            new_bv.vector.frombytes(self.vector.tobytes())
        # ...
        two_byte_ints_to_add = (self.size + other.size + 15) // 16 - len(self.vector)
        new_bv.vector.extend([0] * two_byte_ints_to_add)
```
If we use `MmapBitVector`, it has a fixed size based on `self.size`. If we `extend`, it fails!
