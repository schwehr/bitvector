If I just create `mmap.py` which defines `MmapBitVector(BitVector)` and overrides `__init__`, `__and__`, `__or__`, `__xor__`, `__invert__`, `__add__`, `__iadd__`, `__getitem__`, `pad_from_left`, `pad_from_right`. That way I don't modify `BitVector.py` as much. But wait, then `__getitem__` would return `MmapBitVector`.
Actually, if I just modify `BitVector.py` to use a factory method like `_create_new(self, **kwargs)` and a vector allocator `_allocate_vector(self, ints_needed)`, then subclassing is a breeze!

Let's modify `BitVector.py`:
1. Add `def _create_new(self, **kwargs): return self.__class__(**kwargs)`? No, `self.__class__(...)` is standard Python.
2. In `BitVector.py`, replace explicit `BitVector(` with `self.__class__(`.
3. In `BitVector.py`, instead of `array.array("H", [0] * two_byte_ints_needed)`, do `self.vector = self._allocate_array(two_byte_ints_needed)`. Wait, it's easier to just do `self._allocate_array(two_byte_ints_needed)` which sets `self.vector`. But in `__init__`, we can just replace `self.vector = array.array("H", ...)` with `self._allocate_array(two_byte_ints_needed)`.
4. In `__and__`, `__or__`, `__xor__`, `__invert__`:
   ```python
   res = self.__class__(size=self.size)
   res._set_vector_from_list(lpb)
   ```
   where `_set_vector_from_list` in `BitVector` is:
   ```python
   def _set_vector_from_list(self, lpb: list[int]) -> None:
       self.vector = array.array("H", lpb)
   ```
   And `MmapBitVector` can override `_set_vector_from_list`:
   ```python
   def _set_vector_from_list(self, lpb: list[int]) -> None:
       self.vector[:] = array.array("H", lpb)
   ```
5. What about `__add__`?
   `BitVector.__add__`:
   ```python
        new_bv = self.__class__(size=0)
        new_bv.size = self.size
        # right now it does new_bv.vector.frombytes(self.vector.tobytes())
        new_bv._copy_vector(self.vector)
   ```
   But wait, `__add__` calls `new_bv.vector.extend([0] * two_byte_ints_to_add)`.
   If I just rewrite `__add__` slightly to support an alloc-first model, it's much better!
   ```python
        new_bv = self.__class__(size=self.size + other.size)
        if isinstance(self.vector, array.array) and isinstance(new_bv.vector, array.array):
            new_bv.vector[:len(self.vector)] = self.vector
        elif isinstance(new_bv.vector, memoryview):
            new_bv.vector[:len(self.vector)] = self.vector
        else:
            ...
   ```
   This would avoid all the weird `extend()` logic in `__add__`. Let's check `__add__` again. `__add__` also handles lists. Wait, `new_bv.vector` could be a list if it was initialized differently, but `BitVector` always uses `array.array` internally! `BitVector` supports falling back to `list[int]` only in `__slots__` typing, but in reality it always uses `array.array("H", ...)`. Let's verify this.
