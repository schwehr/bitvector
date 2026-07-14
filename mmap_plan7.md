Ah! `self.vector` gets reassigned to a `list` inside `circular_rot_left` and `circular_rot_right`!
```python
        self.vector = list(map(operator.__rshift__, self.vector, [1] * size))
```
If `self.vector` becomes a list, then memoryview is completely lost!
Oh wow. If we use MmapBitVector, we CANNOT reassign `self.vector = list(...)`. We MUST mutate it in place or do `self.vector[:] = ...`.

Actually, since the task asks to "Implement an mmap version of BitVectorProtocol", I can just implement `MmapBitVector` as a separate class that implements the protocol! I don't necessarily have to inherit from `BitVector` or modify it heavily, although reusing code is good.

But inheriting from `BitVector` and just overriding the methods that reassign `self.vector` might be a lot of methods.
Let's see which methods reassign `self.vector`:
- `__init__`
- `circular_rot_left`
- `circular_rot_right`
- `pad_from_left`
- `pad_from_right`
- `reverse` doesn't exist? Wait, there is a `reverse` maybe.
- `__add__` (creates a new one and modifies its `vector`)
- `__iadd__` (extends)
- `__and__`, `__or__`, `__xor__`, `__invert__` (create new ones and assign `res.vector`)

If I just create `MmapBitVector` in `BitVector/mmap_bitvector.py` and implement all methods by composing or copying from `BitVector`, it might be easier. Wait, copying 2000 lines of code is a bad idea.

Alternatively, I could fix `BitVector.py` so that instead of `self.vector = list(...)` it does:
```python
        self._set_vector_from_list(list(map(operator.__rshift__, self.vector, [1] * size)))
```
And then define `_set_vector_from_list` in `BitVector`:
```python
    def _set_vector_from_list(self, lpb: list[int]) -> None:
        if isinstance(self.vector, array.array):
            self.vector = array.array("H", lpb)
        elif isinstance(self.vector, memoryview):
            self.vector[:] = array.array("H", lpb)
        else:
            self.vector = lpb
```
Wait, if `MmapBitVector` inherits from `BitVector`, and `BitVector` uses `self.__class__` for all new allocations, and uses `_allocate_vector`, `_set_vector_from_list`, `_copy_vector`, `_resize_vector` for all vector modifications, then it will fully support memoryviews!
