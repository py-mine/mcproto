from __future__ import annotations

from typing import Any, cast, final

from attrs import define
from typing_extensions import override

from mcproto.buffer import Buffer
from mcproto.utils.abc import Serializable
from tests.helpers import ExcTest, gen_serializable_test


class CustomError(Exception):
    """Custom exception for testing."""

    additional_data: Any

    def __init__(self, message: str, additional_data: Any):
        super().__init__(message)
        self.additional_data = additional_data


# region ToyClass
@final
@define(init=True)
class ToyClass(Serializable):
    """Toy class for testing demonstrating the use of gen_serializable_test on `Serializable`."""

    a: int
    b: str | int

    @override
    def __attrs_post_init__(self) -> None:
        if isinstance(self.b, int):
            self.b = str(self.b)

        return super().__attrs_post_init__()

    @override
    def serialize_to(self, buf: Buffer):
        """Write the object to a buffer."""
        self.b = cast(str, self.b)  # Handled by the __attrs_post_init__ method
        buf.write_varint(self.a)
        buf.write_utf(self.b)

    @classmethod
    @override
    def deserialize(cls, buf: Buffer) -> ToyClass:
        """Deserialize the object from a buffer."""
        a = buf.read_varint()
        if a == 0:
            raise CustomError("a must be non-zero", additional_data=a)
        b = buf.read_utf()
        return cls(a, b)

    @override
    def validate(self) -> None:
        """Validate the object's attributes."""
        if self.a == 0:
            raise ZeroDivisionError("a must be non-zero")
        self.b = cast(str, self.b)  # Handled by the __attrs_post_init__ method
        if len(self.b) > 10:
            raise ValueError("b must be less than 10 characters")


# endregion ToyClass

# region Test ToyClass
gen_serializable_test(
    context=globals(),
    cls=ToyClass,
    fields=[("a", int), ("b", str)],
    serialize_deserialize=[
        ((1, "hello"), b"\x01\x05hello"),
        ((2, "world"), b"\x02\x05world"),
        ((3, 1234567890), b"\x03\x0a1234567890"),
    ],
    validation_fail=[
        ((0, "hello"), ExcTest(ZeroDivisionError, "a must be non-zero")),  # Message specified
        ((1, "hello world"), ValueError),  # No message specified
        ((1, 12345678900), ExcTest(ValueError, "b must be less than .*")),  # Message regex
    ],
    deserialization_fail=[
        (b"\x00", CustomError),  # No message specified
        (b"\x00\x05hello", ExcTest(CustomError, "a must be non-zero", {"additional_data": 0})),  # Check fields
        (b"\x01", ExcTest(IOError)),  # No message specified
    ],
)
# endregion Test ToyClass


if __name__ == "__main__":
    ToyClass(1, "hello").serialize()
