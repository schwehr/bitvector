import array
import mmap
from typing import Any

from BitVector.BitVector import BitVector


class MmapBitVector(BitVector):
    """
    A memory-efficient bit vector using mmap instead of an in-memory array.
    """

    __slots__ = ("_mmap",)

    def _allocate_vector(self, two_byte_ints_needed: int) -> None:
        if two_byte_ints_needed > 0:
            self._mmap = mmap.mmap(-1, two_byte_ints_needed * 2)
            self.vector = memoryview(self._mmap).cast("H")  # type: ignore[assignment]
        else:
            self._mmap = None  # type: ignore[assignment]
            self.vector = []

    def _set_vector(self, new_vec: Any) -> None:
        m = getattr(self, "_mmap", None)
        if m is not None:
            self.vector = None  # type: ignore[assignment]
            m.close()
        ints_needed = len(new_vec)
        if ints_needed > 0:
            self._mmap = mmap.mmap(-1, ints_needed * 2)
            self.vector = memoryview(self._mmap).cast("H")  # type: ignore[assignment]
            if isinstance(new_vec, memoryview):
                self.vector[:] = new_vec  # type: ignore[assignment]
            elif isinstance(new_vec, array.array):
                self.vector[:] = new_vec  # type: ignore[assignment]
            else:
                self.vector[:] = array.array("H", new_vec)  # type: ignore[assignment]
        else:
            self._mmap = None  # type: ignore[assignment]
            self.vector = []

    def _extend_vector(self, ints_to_add: int) -> None:
        if ints_to_add > 0:
            old_ints = len(self.vector)
            new_ints = old_ints + ints_to_add
            new_mmap = mmap.mmap(-1, new_ints * 2)
            new_vec = memoryview(new_mmap).cast("H")
            if old_ints > 0:
                new_vec[:old_ints] = self.vector  # type: ignore[assignment]  # ty: ignore
                self.vector = None  # type: ignore[assignment]
                m = getattr(self, "_mmap", None)
                if m is not None:
                    m.close()
            self._mmap = new_mmap
            self.vector = new_vec  # type: ignore[assignment]

    def _copy_vector(self, source_vector: Any) -> None:
        self._set_vector(source_vector)

    def __del__(self) -> None:
        try:
            self.vector = None  # type: ignore[assignment]
            m = getattr(self, "_mmap", None)
            if m is not None:
                m.close()
        except Exception:
            pass
