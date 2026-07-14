# Plan

1.  **Refactor `BitVector` initializations:**
    - I will go through `BitVector.py` and replace all explicitly instantiations of `BitVector(...)` with `self.__class__(...)` where applicable. Wait, there is a class method `__init__` itself which shouldn't change. I'll search for `BitVector(`.
    - Inside `__getitem__`: `BitVector(bitlist=slicebits)` -> `self.__class__(bitlist=slicebits)`.
    - Inside `__invert__`: `res = BitVector(size=self.size)` -> `res = self.__class__(size=self.size)`. Wait, it's missing but `__and__`, `__or__`, `__xor__` do this. Wait, `__xor__` does `res = BitVector(size=size)`. Change to `res = self.__class__(size=size)`.
    - Inside `read_bits_from_file`: `return BitVector(bitstring=bitstring)` -> `return self.__class__(bitstring=bitstring)`.
    - Inside `divide_into_two`: `return [BitVector(bitlist=...), BitVector(bitlist=...)]` -> `return [self.__class__(bitlist=...), ...]`.
    - Inside `permute`, `unpermute`: `BitVector(size=...)` -> `self.__class__(size=...)`.
    - Inside `__add__`: `BitVector(size=0)` -> `self.__class__(size=0)`. Wait, `__add__` calls `new_bv = BitVector(size=0)`. We should change this to `new_bv = self.__class__(size=0)`. Wait, does `__add__` do `new_bv.vector = self.vector.copy()`? Yes. If it's an mmap memoryview, `copy()` doesn't exist on memoryview! Oh boy, wait. memoryview doesn't have `.copy()`.
    - Let's check: `if isinstance(self.vector, array.array)`: `new_bv.vector = array.array("H", self.vector)`. I need to change how vectors are copied.

2.  **Generic Vector Allocation and Copying:**
    - Let's add a helper method in `BitVector` to allocate vectors:
      ```python
      def _allocate_vector(self, two_byte_ints_needed: int) -> None:
          self.vector = array.array("H", [0] * two_byte_ints_needed)

      def _copy_vector(self, other_vector) -> None:
          if isinstance(other_vector, array.array):
              self.vector = array.array("H", other_vector)
          elif isinstance(other_vector, memoryview):
              self.vector[:] = other_vector
          else:
              self.vector = other_vector.copy()

      def _set_vector_from_list(self, lpb: list[int]) -> None:
          if isinstance(self.vector, array.array):
              self.vector = array.array("H", lpb)
          elif isinstance(self.vector, memoryview):
              self.vector[:] = array.array("H", lpb)
          else:
              self.vector = lpb.copy()
      ```
    - I should look closely at how `__add__`, `__iadd__`, `__and__`, `__or__`, `__xor__` do things and refactor them to use these helpers.

Let's do this step by step and make sure it works!
