Wait, `mmap.mmap(-1, ...)` allocates memory dynamically.
If we do `self.vector.extend([0] * two_byte_ints_to_add)` in `__iadd__`, `memoryview` doesn't have `extend`.
So for `pad_from_left`, `pad_from_right`, `__iadd__`, `__add__`, etc., we will need a `_resize_vector` method.
Let's see where the size of `vector` changes:
- `__add__` (creates a new `BitVector`, currently copies then extends) -> We can modify `__add__` to allocate the new size upfront and then copy the old vector, then append the new one.
- `__iadd__` -> Modifies self. We can add a `_resize_vector(new_size_ints)` method. For `array.array`, it just does `.extend()`. For `MmapBitVector`, it will allocate a new mmap, copy the old one, and replace `self.vector`.
- `pad_from_left` -> Modifies self.
- `pad_from_right` -> Modifies self.

Let's modify `BitVector.py` directly?
Wait, if I just modify `BitVector.py` to use `Mmap` under the hood if a `mmap=True` flag is passed?
The prompt specifically says: "Implement an mmap version of BitVectorProtocol. How does it's performance compare to the BitVector.BitVector implementation?"
It suggests there should be a distinct class/implementation.

If I create `MmapBitVector.py`, I can just write a wrapper around `mmap` that provides the same API, but actually I can just inherit from `BitVector` and fix the couple of methods that don't play nicely with fixed-size views, like `__add__` and `__iadd__`.
Actually, how many methods need fixing if I inherit?
Let's look at `__and__`. It uses `res = BitVector(size=...)`.
If I override `__and__` in `MmapBitVector`:
```python
class MmapBitVector(BitVector):
    def __and__(self, other):
        # copy __and__ code but change to self.__class__
```
This is getting messy to maintain two copies.
It is much better to just make `BitVector.py` subclass-friendly by:
1. Replacing `BitVector(` with `self.__class__(`.
2. Adding `_create_new(cls, **kwargs)`? Or just using `self.__class__`.
3. Adding `_set_vector(self, new_vec)` to replace `self.vector = list(...)` and `self.vector = array.array(...)`.
4. Overriding `_resize_vector(self, new_size_ints)` instead of `self.vector.extend(...)`.

Let's list all changes to `BitVector.py`:
- Replace `BitVector(bitlist=slicebits)` -> `self.__class__(bitlist=slicebits)`
- Replace `BitVector(size=size)` -> `self.__class__(size=size)`
- Replace `BitVector(bitstring="")` -> `self.__class__(bitstring="")`
- Replace `BitVector(intVal=self.int_val() - 1)` -> `self.__class__(intVal=self.int_val() - 1)`
- Replace `res.vector = array.array("H", lpb)` -> `res._set_vector(lpb)`
- Replace `self.vector = list(...)` -> `self._set_vector(list(...))`
- Add `_set_vector(self, new_vec)`:
  ```python
    def _set_vector(self, new_vec: list[int] | array.array | memoryview) -> None:
        if isinstance(self.vector, array.array):
            self.vector = array.array("H", new_vec)
        elif isinstance(self.vector, memoryview):
            if isinstance(new_vec, memoryview):
                self.vector[:] = new_vec
            else:
                self.vector[:] = array.array("H", new_vec)
        else:
            self.vector = new_vec
  ```
- What about `__add__`?
  `__add__` creates `new_bv = self.__class__(size=0)`, sets `new_bv.size = self.size`, does `new_bv._copy_from(self.vector)`.
  Wait, instead of `size=0`, just allocate `size=self.size + other.size`.
  ```python
        new_bv = self.__class__(size=self.size + other.size)
        if isinstance(self.vector, array.array) and isinstance(new_bv.vector, array.array):
            new_bv.vector[:len(self.vector)] = self.vector
        elif hasattr(new_bv.vector, '__setitem__'): # list or memoryview
            new_bv.vector[:len(self.vector)] = self.vector
  ```
  Then skip the `extend()` part!
- Let's check `__iadd__`:
  ```python
        two_byte_ints_to_add = (self.size + other.size + 15) // 16 - len(self.vector)
        self._extend_vector(two_byte_ints_to_add)
  ```
  where `_extend_vector` is:
  ```python
    def _extend_vector(self, ints_to_add: int) -> None:
        if ints_to_add > 0:
            if hasattr(self.vector, 'extend'):
                self.vector.extend([0] * ints_to_add)
            elif isinstance(self.vector, memoryview):
                # need to resize... but we shouldn't know about mmap here
                pass
  ```
  Wait, if we introduce `_extend_vector`, `MmapBitVector` can override it!
  ```python
  class MmapBitVector(BitVector):
      def _extend_vector(self, ints_to_add: int) -> None:
          if ints_to_add > 0:
              new_size = len(self.vector) + ints_to_add
              new_mmap = mmap.mmap(-1, new_size * 2)
              new_vec = memoryview(new_mmap).cast('H')
              new_vec[:len(self.vector)] = self.vector
              self._mmap.close()
              self._mmap = new_mmap
              self.vector = new_vec
  ```
  This is beautifully simple!
