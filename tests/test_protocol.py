from typing import cast

from BitVector import BitVector, BitVectorProtocol


def test_protocol() -> None:
    bv = BitVector(intVal=42, size=8)
    bv_proto = cast(BitVectorProtocol, bv)
    assert bv_proto.int_val() == 42
    assert bv_proto._getsize() == 8
    assert len(bv_proto) == 8
    assert str(bv_proto) == "00101010"


# Mock classes to hit protocol stubs since protocol itself cannot be instantiated
# The protocol isn't meant to have code coverage on its own stubs.
# But pytest-cov counts `pass` or `...` as executable statements unless ignored
