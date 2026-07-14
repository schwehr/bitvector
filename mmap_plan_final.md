# Plan

1. **Refactor `BitVector.py` for extensibility:**
   - Introduce vector memory management methods `_allocate_vector(self, two_byte_ints_needed: int)`, `_set_vector(self, new_vec: Any)`, `_extend_vector(self, ints_to_add: int)`, and `_copy_vector(self, source_vector: Any)` inside `BitVector`.
   - Update `__init__`, `pad_from_left`, `pad_from_right`, `__and__`, `__or__`, `__xor__`, `__invert__`, `__add__`, `__iadd__`, `circular_rot_left`, `circular_rot_right`, `reverse`, and `__deepcopy__` to use these new methods instead of hardcoding `array.array(...)` or `self.vector.extend(...)`.
   - Replace explicit `BitVector(...)` construction in instance methods (e.g., in `__getitem__`, `__invert__`, `__add__`, `read_bits_from_file`, `divide_into_two`, `permute`, `unpermute`) with `self.__class__(...)` so that subclasses return instances of themselves.

2. **Implement `MmapBitVector`:**
   - Create a new subclass `MmapBitVector` in `BitVector/mmap_bitvector.py` (or as part of `BitVector/BitVector.py` / `BitVector/__init__.py`) that inherits from `BitVector`. I will add it to a new file `BitVector/mmap_bitvector.py`.
   - Override `__slots__ = ("_mmap",)` to track the `mmap` object.
   - Override `_allocate_vector`, `_set_vector`, `_extend_vector`, and `_copy_vector` to allocate and manipulate memory via anonymous `mmap` mappings and `memoryview`.
   - Export `MmapBitVector` in `BitVector/__init__.py`.

3. **Write tests:**
   - Add tests for `MmapBitVector` in `tests/test_mmap.py` to ensure it works correctly and performance is roughly comparable to standard `BitVector`.
   - Ensure the `test_protocol` passes and the original benchmark script works smoothly.

4. **Complete pre commit steps:**
   - Complete pre commit steps to ensure proper testing, verification, review, and reflection are done.

5. **Submit changes:**
   - Call submit with proper commit message.
