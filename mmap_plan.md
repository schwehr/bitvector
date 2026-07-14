# Plan

1.  **Refactor `BitVector` initializations in `BitVector.py`:**
    - I need to replace all explicit `BitVector(...)` calls inside `BitVector.py` with `self.__class__(...)` so that subclasses will return instances of the subclass for operations like `__and__`, `__or__`, `__xor__`, slicing, etc. Wait, I also need to make sure I do this for any internal methods that create a new instance.
    - Let's change the return types as well, if needed, though they already return `Self` or `BitVector`. I will replace `BitVector(...)` with `self.__class__(...)`.
2.  **Make array allocation generic:**
    - Right now, `self.vector = array.array("H", [0] * two_byte_ints_needed)` is hardcoded in several places.
    - I will introduce a helper method `_resize_vector(self, two_byte_ints_needed: int) -> None:` in `BitVector` which does `self.vector = array.array("H", [0] * two_byte_ints_needed)`. Wait, it's easier to just do `self._allocate_vector(two_byte_ints_needed)` which creates and returns the vector. No, `self._resize_vector(two_byte_ints_needed)` is better.
    - I will replace the instances of `self.vector = array.array("H", ...)` with `self._resize_vector(two_byte_ints_needed)` inside `__init__`, `pad_from_left`, `pad_from_right`. Wait, `__and__`, `__or__`, `__xor__` just assign directly: `res.vector = array.array("H", lpb)`. I can create a method `_set_vector_from_list(self, lpb: list[int]) -> None` in `BitVector`.
    - Let's look closer at `__and__`, etc.
      ```python
      res = self.__class__(size=size)
      res.vector = array.array("H", lpb)
      ```
      This will break if `res.vector` needs to be an mmap memoryview. If it's a memoryview, `res.vector = array.array("H", lpb)` replaces the memoryview! Instead, it should be:
      ```python
      res = self.__class__(size=size)
      for i, v in enumerate(lpb): res.vector[i] = v
      ```
      Or better, introduce a helper method `_set_vector_from_list(self, lpb)`:
      ```python
      def _set_vector_from_list(self, lpb):
          if isinstance(self.vector, array.array):
              self.vector = array.array("H", lpb)
          else:
              for i, v in enumerate(lpb):
                  self.vector[i] = v
      ```
      Wait, `memoryview` can't just be reassigned. However, `memoryview` supports slice assignment? `self.vector[:] = array.array('H', lpb)` works for `memoryview`! Let's test that.
3.  **Create `mmap.py` (or similar name like `MmapBitVector.py`):**
    - The task says "Implement an mmap version of BitVectorProtocol. How does it's performance compare to the BitVector.BitVector implementation?".
    - We will create `MmapBitVector` in `BitVector.py` itself or in `MmapBitVector.py`. `BitVector/mmap_bitvector.py` would be appropriate, or just `BitVector/MmapBitVector.py`. I'll put it in `BitVector/MmapBitVector.py` and export it in `__init__.py`.
    - `MmapBitVector` will inherit from `BitVector`.
    - `MmapBitVector` will override `_allocate_vector(self, two_byte_ints_needed)` and `__del__` if needed to close the mmap, though it doesn't strictly need to if the garbage collector takes care of it. Actually, `mmap` is tricky, we can just use `memoryview(mmap.mmap(-1, size)).cast('H')` as `self.vector` and `self._mmap = mmap.mmap(...)` as an attribute.

Let me test slice assignment to memoryview and figure out exactly where the hardcoded allocations are.
