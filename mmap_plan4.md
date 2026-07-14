Wait, this implies `MmapBitVector` might be better implemented completely separately? No, it's just that `BitVector.py` is not designed for fixed-size arrays. But `BitVector` *can* be fixed size if we just construct a new one of the right size.
For `MmapBitVector`, we can override `__add__`, `__iadd__`, `pad_from_left`, `pad_from_right`.
Or we can modify `BitVector`'s `__add__` to allocate the full size right away!
Let's modify `__add__` in `BitVector.py`:
```python
        new_bv = self.__class__(size=self.size + other.size)
        # copy bits from self
        for i in range(len(self.vector)):
            new_bv.vector[i] = self.vector[i]

        # then we need to do the shifting logic for the other bits
        # Wait, the current shifting logic works on the array directly.
```
Let's see `__add__` in `BitVector.py`. It extends the array and then does bit shifting.
If we change it to allocate the full size first:
```python
        new_bv = self.__class__(size=0) # wait
```
I can just do:
```python
        new_bv = self.__class__(size=self.size + other.size)
        # copy self bits
        if isinstance(self.vector, array.array) and isinstance(new_bv.vector, array.array):
            # this works because new_bv is an array of correct size, we can slice assign
            new_bv.vector[:len(self.vector)] = self.vector
        elif isinstance(new_bv.vector, memoryview):
            new_bv.vector[:len(self.vector)] = self.vector
        else:
            ...
```
Wait, if `new_bv` is allocated with `self.size + other.size`, `len(new_bv.vector)` is already `two_byte_ints_needed` for the combined size!
So copying `self.vector` into it just means:
```python
        new_bv.vector[:len(self.vector)] = self.vector
```
And then the shifting loop just processes the `other.vector` and adds it in! This would be much cleaner and work for both `array.array` and `memoryview`. Let's test if this is equivalent.
