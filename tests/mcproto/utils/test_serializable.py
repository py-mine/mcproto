from __future__ import annotations

from typing import final

from mcproto.buffer import Buffer
from mcproto.utils.abc import Serializable, dataclass
from tests.helpers import gen_serializable_test


@final
@dataclass
class ToyClass(Serializable):
    """Toy class for testing demonstrating the use of gen_serializable_test on `Serializable`."""

    a: int
    b: str

    def serialize_to(self, buf: Buffer):
        """Write the object to a buffer."""
        buf.write_varint(self.a)
        buf.write_utf(self.b)

    @classmethod
    def deserialize(cls, buf: Buffer) -> ToyClass:
        """Deserialize the object from a buffer."""
        a = buf.read_varint()
        if a == 0:
            raise ZeroDivisionError("a must be non-zero")
        b = buf.read_utf()
        return cls(a, b)

    def validate(self) -> None:
        """Validate the object's attributes."""
        if self.a == 0:
            raise ZeroDivisionError("a must be non-zero")
        if len(self.b) > 10:
            raise ValueError("b must be less than 10 characters")


gen_serializable_test(
    context=globals(),
    cls=ToyClass,
    fields=[("a", int), ("b", str)],
    test_data=[
        ((1, "hello"), b"\x01\x05hello"),
        ((2, "world"), b"\x02\x05world"),
        ((0, "hello"), ZeroDivisionError),
        ((1, "hello world"), ValueError),
        (ZeroDivisionError, b"\x00"),
        (IOError, b"\x01"),
    ],
)
