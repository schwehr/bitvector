Let's review where `__add__` calls `BitVector`:
```python
    def __add__(self, other: BitVector) -> Self:
        new_bv = self.__class__(size=0)
        new_bv.size = self.size
        # How to copy?
        new_bv._copy_from(self.vector)
        two_byte_ints_to_add = (self.size + other.size + 15) // 16 - len(self.vector)
        new_bv._extend_vector(two_byte_ints_to_add)
```
If we do this, `__add__` doesn't need to change much, just use `self.__class__` and `_copy_from` and `_extend_vector`.

Let's look at `__init__` in `BitVector.py`.
```python
            two_byte_ints_needed = (size + 15) // 16
            self.vector = array.array("H", [0] * two_byte_ints_needed)
```
Change to:
```python
            two_byte_ints_needed = (size + 15) // 16
            self._allocate_vector(two_byte_ints_needed)
```
And add `_allocate_vector`:
```python
    def _allocate_vector(self, two_byte_ints_needed: int) -> None:
        self.vector = array.array("H", [0] * two_byte_ints_needed)
```
And we also change it in `__init__` for `bitlist`, `bitstring`, `hexstring`, `textstring`, `rawbytes`.

Let's double check `__add__` copy block:
```python
        if isinstance(self.vector, array.array) and isinstance(
            new_bv.vector, array.array
        ):
            new_bv.vector.frombytes(self.vector.tobytes())
        elif isinstance(self.vector, list):
            new_bv.vector = self.vector.copy()
```
I can replace this with `new_bv._copy_from(self.vector)`:
```python
    def _copy_from(self, source_vector) -> None:
        if isinstance(source_vector, array.array) and isinstance(self.vector, array.array):
            self.vector.frombytes(source_vector.tobytes())
        elif isinstance(self.vector, memoryview):
            self.vector[:] = source_vector
        else:
            self.vector = source_vector.copy()
```
Wait, if `__add__` initializes `new_bv = self.__class__(size=0)`, then `len(new_bv.vector) == 0`.
If we then do `new_bv._copy_from(self.vector)`, `memoryview` will complain about size mismatch if we do `self.vector[:] = source_vector`!
Ah! `memoryview` cannot grow dynamically. So initializing with `size=0` and then `_copy_from` and `_extend_vector` is bad for `MmapBitVector`. `_copy_from` would fail, because `new_bv` has size 0!
We must initialize `new_bv` with the FINAL size upfront!
```python
    def __add__(self, other: BitVector) -> Self:
        new_bv = self.__class__(size=self.size + other.size)
        new_bv._copy_from_left(self.vector, self.size)
        ...
```
Wait, `BitVector`'s current `__add__` does:
1. `new_bv = BitVector(size=0)`
2. `new_bv.size = self.size`
3. Copies `self.vector` into `new_bv.vector`.
4. Extends `new_bv.vector` by `two_byte_ints_to_add` zeros.
5. Appends `other.vector` using bit shifting.

If we change `__add__` to:
```python
    def __add__(self, other: BitVector) -> Self:
        new_bv = self.__class__(size=self.size + other.size)
        new_bv._copy_from_left(self.vector)

        # then bitshift the rest
        new_bv.size = self.size
        # perform the shifts as before...
        # and at the end:
        new_bv.size = self.size + other.size
```
This is a bit tricky.
Let's see the current `BitVector.__add__`.
