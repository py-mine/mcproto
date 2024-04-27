from __future__ import annotations

import warnings
from abc import ABCMeta
from enum import IntEnum
from typing import ClassVar, List, Mapping, Union, cast

from typing_extensions import TypeAlias

from mcproto.buffer import Buffer
from mcproto.protocol.base_io import StructFormat
from mcproto.types.abc import MCType

__all__ = [
    "NBTagType",
    "NBTag",
    "EndNBT",
    "ByteNBT",
    "ShortNBT",
    "IntNBT",
    "LongNBT",
    "FloatNBT",
    "DoubleNBT",
    "ByteArrayNBT",
    "StringNBT",
    "ListNBT",
    "CompoundNBT",
    "IntArrayNBT",
    "LongArrayNBT",
]


# region NBT Specification
"""
Source : https://web.archive.org/web/20110723210920/http://www.minecraft.net/docs/NBT.txt

Named Binary Tag specification

NBT (Named Binary Tag) is a tag based binary format designed to carry large amounts of binary data with smaller amounts
of additional data.
An NBT file consists of a single GZIPped Named Tag of type TAG_Compound.

A Named Tag has the following format:

    byte tagType
    TAG_String name
    [payload]

The tagType is a single byte defining the contents of the payload of the tag.

The name is a descriptive name, and can be anything (eg "cat", "banana", "Hello World!"). It has nothing to do with the
tagType.
The purpose for this name is to name tags so parsing is easier and can be made to only look for certain recognized tag
names.
Exception: If tagType is TAG_End, the name is skipped and assumed to be "".

The [payload] varies by tagType.

Note that ONLY Named Tags carry the name and tagType data. Explicitly identified Tags (such as TAG_String above) only
contains the payload.


The tag types and respective payloads are:

    TYPE: 0  NAME: TAG_End
    Payload: None.
    Note:    This tag is used to mark the end of a list.
             Cannot be named! If type 0 appears where a Named Tag is expected, the name is assumed to be "".
             (In other words, this Tag is always just a single 0 byte when named, and nothing in all other cases)

    TYPE: 1  NAME: TAG_Byte
    Payload: A single signed byte (8 bits)

    TYPE: 2  NAME: TAG_Short
    Payload: A signed short (16 bits, big endian)

    TYPE: 3  NAME: TAG_Int
    Payload: A signed short (32 bits, big endian)

    TYPE: 4  NAME: TAG_Long
    Payload: A signed long (64 bits, big endian)

    TYPE: 5  NAME: TAG_Float
    Payload: A floating point value (32 bits, big endian, IEEE 754-2008, binary32)

    TYPE: 6  NAME: TAG_Double
    Payload: A floating point value (64 bits, big endian, IEEE 754-2008, binary64)

    TYPE: 7  NAME: TAG_Byte_Array
    Payload: TAG_Int length
             An array of bytes of unspecified format. The length of this array is <length> bytes

    TYPE: 8  NAME: TAG_String
    Payload: TAG_Short length
             An array of bytes defining a string in UTF-8 format. The length of this array is <length> bytes

    TYPE: 9  NAME: TAG_List
    Payload: TAG_Byte tagId
             TAG_Int length
             A sequential list of Tags (not Named Tags), of type <typeId>. The length of this array is <length> Tags
    Notes:   All tags share the same type.

    TYPE: 10 NAME: TAG_Compound
    Payload: A sequential list of Named Tags. This array keeps going until a TAG_End is found.
             TAG_End end
    Notes:   If there's a nested TAG_Compound within this tag, that one will also have a TAG_End, so simply reading
    until the next TAG_End will not work.
             The names of the named tags have to be unique within each TAG_Compound
             The order of the tags is not guaranteed.


    // NEW TAGS
    TYPE: 11 NAME: TAG_Int_Array
    Payload: TAG_Int length
             An array of integers. The length of this array is <length> integers

    TYPE: 12 NAME: TAG_Long_Array
    Payload: TAG_Int length
             An array of longs. The length of this array is <length> longs


"""
# endregion
# region NBT base classes/types


class NBTagType(IntEnum):
    """Types of NBT tags."""

    END = 0
    BYTE = 1
    SHORT = 2
    INT = 3
    LONG = 4
    FLOAT = 5
    DOUBLE = 6
    BYTE_ARRAY = 7
    STRING = 8
    LIST = 9
    COMPOUND = 10
    INT_ARRAY = 11
    LONG_ARRAY = 12


PayloadType: TypeAlias = Union[
    int,
    float,
    bytearray,
    bytes,
    str,
    List["PayloadType"],
    Mapping[str, "PayloadType"],
    List[int],
    "NBTag",
    List["NBTag"],
]


class _MetaNBTag(ABCMeta):
    """Metaclass for NBT tags."""

    TYPE: NBTagType = NBTagType.COMPOUND

    def __new__(cls, name: str, bases: tuple[type], namespace: dict, **kwargs):
        new_cls: NBTag = super().__new__(cls, name, bases, namespace)  # type: ignore
        if name != "NBTag":
            NBTag.ASSOCIATED_TYPES[new_cls.TYPE] = new_cls  # type: ignore
        return new_cls


class NBTag(MCType, metaclass=_MetaNBTag):
    """Base class for NBT tags."""

    __slots__ = ("name", "payload")

    TYPE: ClassVar[NBTagType] = NBTagType.COMPOUND

    ASSOCIATED_TYPES: ClassVar[dict[NBTagType, type[NBTag]]] = {}

    def __init__(self, payload: PayloadType, name: str = ""):
        if self.__class__ == NBTag:
            raise TypeError("Cannot instantiate an NBTag object directly, use a subclass instead.")
        self.name = name
        self.payload = payload

    def serialize(self, with_type: bool = True, with_name: bool = True) -> Buffer:
        """Serialize the NBT tag to a buffer.

        :param with_type: Whether to include the type of the tag in the serialization.
        :param with_name: Whether to include the name of the tag in the serialization.

        :note: These parameters only control the first level of serialization.
        :return: The buffer containing the serialized NBT tag.
        """
        buf = Buffer()
        self.write_to(buf, with_name=with_name, with_type=with_type)
        return buf

    def _write_header(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> bool:
        if with_type:
            buf.write_value(StructFormat.BYTE, self.TYPE.value)
        if self.TYPE == NBTagType.END:
            return False
        if with_name:
            if not self.name:
                raise ValueError("Named tags must have a name.")
            StringNBT(self.name).write_to(buf, with_type=False, with_name=False)
        return True

    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        """Write the NBT tag to the buffer."""
        ...

    @classmethod
    def deserialize(cls, buf: Buffer, with_name: bool = True, with_type: bool = True) -> NBTag:
        """Deserialize the NBT tag.

        :param buf: The buffer to read from.
        :param with_name: Whether to read the name of the tag. If set to False, the tag will have the name "".
        :param with_type: Whether to read the type of the tag.
            If set to True, the tag will be read from the buffer and
                the return type will be inferred from the tag type.
            If set to False and called from a subclass, the tag type will be inferred from the subclass.
            If set to False and called from the base class, the tag type will be TAG_Compound.

            If with_type is set to False, the buffer must not start with the tag type byte.

        :return: The deserialized NBT tag.
        """
        name, tag_type = cls._read_header(buf, with_name=with_name, read_type=with_type)

        tag_class = NBTag.ASSOCIATED_TYPES[tag_type]
        if cls not in (NBTag, tag_class):
            raise TypeError(f"Expected a {cls.__name__} tag, but found a different tag ({tag_class.__name__}).")

        tag = tag_class.read_from(buf, with_type=False, with_name=False)
        tag.name = name
        return tag

    @classmethod
    def _read_header(cls, buf: Buffer, read_type: bool = True, with_name: bool = True) -> tuple[str, NBTagType]:
        """Read the header of the NBT tag.

        :param buf: The buffer to read from.
        :param read_type: Whether to read the type of the tag from the buffer.
        :param with_name: Whether to read the name of the tag. If set to False, the tag will have the name "".

        :return: A tuple containing the name and the tag type.


        :note: It is possible that this function reads nothing from the buffer if both with_name and read_type are set
            to False.
        """
        tag_type: NBTagType = cls.TYPE  # default value
        if read_type:
            try:
                tag_type = NBTagType(buf.read_value(StructFormat.BYTE))
            except OSError:
                raise IOError("Buffer is empty.") from None
            except ValueError:
                raise TypeError("Invalid tag type.") from None

        if tag_type == NBTagType.END:
            return "", tag_type

        name = StringNBT.read_from(buf, with_type=False, with_name=False).value if with_name else ""

        return name, tag_type

    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> NBTag:
        """Read the NBT tag from the buffer.

        :param buf: The buffer to read from.
        :param with_type: Whether to read the type of the tag.
            If set to True, the tag will be read from the buffer and
                the return type will be inferred from the tag type.
            If set to False and called from a subclass, the tag type will be inferred from the subclass.
            If set to False and called from the base class, the tag type will be TAG_Compound.
        :param with_name: Whether to read the name of the tag. If set to False, the tag will have the name "".

        :return: The NBT tag.
        """
        return cls.deserialize(buf, with_name=with_name, with_type=with_type)

    @staticmethod
    def from_object(data: object, /, name: str = "", *, use_int_array: bool = True) -> NBTag:  # noqa: PLR0911,PLR0912
        """Create an NBT tag from an arbitrary (compatible) Python object.

        :param data: The object to convert to an NBT tag.
        :param use_int_array: Whether to use IntArrayNBT and LongArrayNBT for lists of integers.
            If set to False, all lists of integers will be considered as ListNBT.
        :param name: The name of the resulting tag. Used for recursive calls.

        :return: The NBT tag representing the object.

        :note: The function will attempt to convert the object to an NBT tag in the following way:
            - If the object is a dictionary with a single key, the key will be used as the name of the tag.
            - If the object is an integer, it will be converted to a ByteNBT, ShortNBT, IntNBT, or LongNBT tag
                depending on the value.
            - If the object is a list, it will be converted to a ListNBT tag.
            - If the object is a dictionary, it will be converted to a CompoundNBT tag.
            - If the object is a string, it will be converted to a StringNBT tag.
            - If the object is a float, it will be converted to a FloatNBT tag.
            - If the object can be serialized to bytes, it will be converted to a ByteArrayNBT tag.


            - If you want an object to be serialized in a specific way, you can implement:

            ```python
            def to_nbt(self, name: str = "") -> NBTag:
                ...
            ```
        """
        if hasattr(data, "to_nbt"):  # For objects that can be converted to NBT
            return data.to_nbt(name=name)  # type: ignore

        if isinstance(data, int):
            if -(1 << 7) <= data < 1 << 7:
                return ByteNBT(data, name=name)
            if -(1 << 15) <= data < 1 << 15:
                return ShortNBT(data, name=name)
            if -(1 << 31) <= data < 1 << 31:
                return IntNBT(data, name=name)
            if -(1 << 63) <= data < 1 << 63:
                return LongNBT(data, name=name)
            raise ValueError(f"Integer {data} is out of range.")
        if isinstance(data, float):
            return FloatNBT(data, name=name)
        if isinstance(data, str):
            return StringNBT(data, name=name)
        if isinstance(data, (bytearray, bytes)):
            if isinstance(data, bytearray):
                data = bytes(data)
            return ByteArrayNBT(data, name=name)
        if isinstance(data, list):
            if not data:
                # Type END is used to mark an empty list
                return ListNBT([], name=name)
            first_type = type(data[0])
            if any(type(item) != first_type for item in data):
                raise TypeError("All items in a list must be of the same type.")

            if issubclass(first_type, int) and use_int_array:
                # Check the range of the integers in the list
                use_int = all(-(1 << 31) <= item < 1 << 31 for item in data)
                use_long = all(-(1 << 63) <= item < 1 << 63 for item in data)
                if use_int:
                    return IntArrayNBT(data, name=name)
                if not use_long:  # Too big to fit in a long, won't fit in a List of Longs either
                    raise ValueError("Integer list contains values out of range.")
                return LongArrayNBT(data, name=name)
            return ListNBT([NBTag.from_object(item, use_int_array=use_int_array) for item in data], name=name)
        if isinstance(data, dict):
            if len(data) == 0:
                return CompoundNBT([], name=name)
            if len(data) == 1 and name == "":
                key, value = next(iter(data.items()))
                return NBTag.from_object(value, name=key, use_int_array=use_int_array)
            payload = []
            for key, value in data.items():
                tag = NBTag.from_object(value, name=key, use_int_array=use_int_array)
                payload.append(tag)
            return CompoundNBT(payload, name)
        if data is None:
            warnings.warn("Converting None to an END tag.", stacklevel=2)
            return EndNBT()  # Should not be used

        try:
            # Check if the object can be converted to bytes
            return ByteArrayNBT(bytes(data), name=name)  # type: ignore
        except (TypeError, ValueError):
            pass
        raise TypeError(f"Cannot convert object of type {type(data)} to an NBT tag.")

    def to_object(self) -> Mapping[str, PayloadType] | PayloadType:
        """Convert the NBT payload to a dictionary."""
        return CompoundNBT(self.payload).to_object()  # allow NBTag.to_object to act as a dict

    def __getitem__(self, key: str | int) -> PayloadType:
        """Get a tag from the list or compound tag."""
        if self.TYPE not in (NBTagType.LIST, NBTagType.COMPOUND, NBTagType.INT_ARRAY, NBTagType.LONG_ARRAY):
            raise TypeError(f"Cannot get a tag by index from a non-LIST or non-COMPOUND tag ({self.TYPE}).")

        if not isinstance(self.payload, list):
            raise AttributeError(
                f"The payload of the tag is not a list ({self.TYPE}).\n"
                "Check that the initialization of the tag is correct."
            )
        if not isinstance(key, (str, int)):  # type: ignore
            raise TypeError("Key must be a string or an integer.")

        if isinstance(key, str):
            if self.TYPE != NBTagType.COMPOUND:
                raise TypeError(f"Cannot get a tag by name from a non-COMPOUND tag ({self.TYPE}).")
            if not all(isinstance(tag, NBTag) for tag in self.payload):
                raise AttributeError("The payload of the tag is not a list of NBTag objects.")
            for tag in self.payload:
                tag = cast(NBTag, tag)
                if tag.name == key:
                    return tag
            raise KeyError(f"No tag with the name {key!r} found.")

        # Key is an integer
        if key < -len(self.payload) or key >= len(self.payload):
            raise IndexError(f"Index {key} out of range.")
        return self.payload[key]

    def __repr__(self) -> str:
        if self.name:
            return f"{self.__class__.__name__}[{self.name!r}]({self.payload!r})"
        return f"{self.__class__.__name__}({self.payload!r})"

    def __eq__(self, other: object) -> bool:
        """Check equality between two NBT tags."""
        if not isinstance(other, NBTag):
            raise NotImplementedError("Cannot compare an NBTag to a non-NBTag object.")
        return self.name == other.name and self.TYPE == other.TYPE and self.payload == other.payload

    def to_nbt(self, name: str = "") -> NBTag:
        """Convert the object to an NBT tag.

        ..warning This is already an NBT tag, so it will modify the name of the tag and return itself.
        """
        self.name = name
        return self

    @property
    def value(self) -> PayloadType:
        """Get the payload of the NBT tag in a python-friendly format."""
        obj = self.to_object()
        if isinstance(obj, dict) and self.name:
            return obj[self.name]
        return obj


# endregion
# region NBT tags types


class EndNBT(NBTag):
    """Sentinel tag used to mark the end of a TAG_Compound."""

    TYPE = NBTagType.END
    __slots__ = ()

    def __init__(self):
        """Create a new EndNBT tag."""
        super().__init__(0, name="")

    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        """Write the EndNBT tag to the buffer.

        :param buf: The buffer to write to.
        :param with_type: Whether to include the type of the tag in the serialization.
        :param with_name: Whether to include the name of the tag in the serialization.
        """
        self._write_header(buf, with_type=with_type, with_name=with_name)

    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> EndNBT:
        """Read the EndNBT tag from the buffer.

        :param buf: The buffer to read from.
        :param with_type: Whether to read the type of the tag from the buffer. If this is False, the type of the class
            will be used.
        :param with_name: Whether to read the name of the tag. Has no effect on the EndNBT tag.

        :return: The EndNBT tag.
        """
        _, tag_type = cls._read_header(buf, read_type=with_type, with_name=with_name)
        if tag_type != cls.TYPE:
            raise TypeError(f"Expected a {cls.TYPE.name} tag, but found a different tag ({tag_type.name}).")
        return EndNBT()

    def to_object(self) -> Mapping[str, PayloadType]:
        """Convert the EndNBT tag to a python object.

        :return: An empty dictionary.
        """
        return {}


class ByteNBT(NBTag):
    """NBT tag representing a single byte value, represented as a signed 8-bit integer."""

    TYPE = NBTagType.BYTE

    __slots__ = ()
    payload: int

    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        """Write the ByteNBT tag to the buffer.

        :param buf: The buffer to write to.
        :param with_type: Whether to include the type of the tag in the serialization.
        :param with_name: Whether to include the name of the tag in the serialization.
        """
        self._write_header(buf, with_type=with_type, with_name=with_name)
        if self.payload < -(1 << 7) or self.payload >= 1 << 7:
            raise OverflowError("Byte value out of range.")

        buf.write_value(StructFormat.BYTE, self.payload)

    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> ByteNBT:
        """Read the ByteNBT tag from the buffer.

        :param buf: The buffer to read from.
        :param with_type: Whether to read the type of the tag from the buffer. If this is False, the type of the class
            will be used.
        :param with_name: Whether to read the name of the tag to the buffer as a TAG_String.

        :return: The ByteNBT tag.
        """
        name, tag_type = cls._read_header(buf, read_type=with_type, with_name=with_name)
        if tag_type != cls.TYPE:
            raise TypeError(f"Expected a {cls.TYPE.name} tag, but found a different tag ({tag_type.name}).")

        if buf.remaining < 1:
            raise IOError("Buffer does not contain enough data to read a byte. (Empty buffer)")

        return ByteNBT(buf.read_value(StructFormat.BYTE), name=name)

    def __int__(self) -> int:
        """Get the integer value of the ByteNBT tag."""
        return self.payload

    def to_object(self) -> Mapping[str, int] | int:
        """Convert the ByteNBT tag to a python object.

        :return: A dictionary containing the name and the integer value of the tag. If the tag has no name, the value
            will be returned directly.
        """
        if self.name:
            return {self.name: self.payload}
        return self.payload

    @property
    def value(self) -> int:
        """Get the integer value of the IntNBT tag."""
        return self.payload


class ShortNBT(ByteNBT):
    """NBT tag representing a short value, represented as a signed 16-bit integer."""

    TYPE = NBTagType.SHORT

    __slots__ = ()

    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        """Write the ShortNBT tag to the buffer.

        :param buf: The buffer to write to.
        :param with_type: Whether to include the type of the tag in the serialization.
        :param with_name: Whether to include the name of the tag in the serialization.

        :note: The short value is written as a signed 16-bit integer in big-endian format.
        """
        self._write_header(buf, with_type=with_type, with_name=with_name)

        if self.payload < -(1 << 15) or self.payload >= 1 << 15:
            raise OverflowError("Short value out of range.")

        buf.write(self.payload.to_bytes(2, "big", signed=True))

    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> ShortNBT:
        """Read the ShortNBT tag from the buffer.

        :param buf: The buffer to read from.
        :param with_type: Whether to read the type of the tag from the buffer. If this is False, the type of the class
            will be used.
        :param with_name: Whether to read the name of the tag to the buffer as a TAG_String.

        :return: The ShortNBT tag.
        """
        name, tag_type = cls._read_header(buf, read_type=with_type, with_name=with_name)
        if tag_type != cls.TYPE:
            raise TypeError(f"Expected a {cls.TYPE.name} tag, but found a different tag ({tag_type.name}).")

        if buf.remaining < 2:
            raise IOError("Buffer does not contain enough data to read a short.")

        return ShortNBT(int.from_bytes(buf.read(2), "big", signed=True), name=name)


class IntNBT(ByteNBT):
    """NBT tag representing an integer value, represented as a signed 32-bit integer."""

    TYPE = NBTagType.INT

    __slots__ = ()

    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        """Write the IntNBT tag to the buffer.

        :param buf: The buffer to write to.
        :param with_type: Whether to include the type of the tag in the serialization.
        :param with_name: Whether to include the name of the tag in the serialization.

        :note: The integer value is written as a signed 32-bit integer in big-endian format.
        """
        self._write_header(buf, with_type=with_type, with_name=with_name)

        if self.payload < -(1 << 31) or self.payload >= 1 << 31:
            raise OverflowError("Integer value out of range.")

        # No more messing around with the struct, we want 32 bits of data no matter what
        buf.write(self.payload.to_bytes(4, "big", signed=True))

    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> IntNBT:
        """Read the IntNBT tag from the buffer.

        :param buf: The buffer to read from.
        :param with_type: Whether to read the type of the tag from the buffer. If this is False, the type of the class
            will be used.
        :param with_name: Whether to read the name of the tag to the buffer as a TAG_String.

        :return: The IntNBT tag.
        """
        name, tag_type = cls._read_header(buf, read_type=with_type, with_name=with_name)
        if tag_type != cls.TYPE:
            raise TypeError(f"Expected a {cls.TYPE.name} tag, but found a different tag ({tag_type.name}).")

        if buf.remaining < 4:
            raise IOError("Buffer does not contain enough data to read an int.")

        return IntNBT(int.from_bytes(buf.read(4), "big", signed=True), name=name)


class LongNBT(ByteNBT):
    """NBT tag representing a long value, represented as a signed 64-bit integer."""

    TYPE = NBTagType.LONG

    __slots__ = ()

    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        """Write the LongNBT tag to the buffer.

        :param buf: The buffer to write to.
        :param with_type: Whether to include the type of the tag in the serialization.
        :param with_name: Whether to include the name of the tag in the serialization.

        :note: The long value is written as a signed 64-bit integer in big-endian format.
        """
        self._write_header(buf, with_type=with_type, with_name=with_name)

        if self.payload < -(1 << 63) or self.payload >= 1 << 63:
            raise OverflowError("Long value out of range.")

        # No more messing around with the struct, we want 64 bits of data no matter what
        buf.write(self.payload.to_bytes(8, "big", signed=True))

    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> LongNBT:
        """Read the LongNBT tag from the buffer.

        :param buf: The buffer to read from.
        :param with_type: Whether to read the type of the tag from the buffer. If this is False, the type of the class
            will be used.
        :param with_name: Whether to read the name of the tag to the buffer as a TAG_String.

        :return: The LongNBT tag.
        """
        name, tag_type = cls._read_header(buf, read_type=with_type, with_name=with_name)
        if tag_type != cls.TYPE:
            raise TypeError(f"Expected a {cls.TYPE.name} tag, but found a different tag ({tag_type.name}).")

        if buf.remaining < 8:
            raise IOError("Buffer does not contain enough data to read a long.")

        payload = int.from_bytes(buf.read(8), "big", signed=True)
        return LongNBT(payload, name=name)


class FloatNBT(NBTag):
    """NBT tag representing a floating-point value, represented as a 32-bit IEEE 754-2008 binary32 value."""

    TYPE = NBTagType.FLOAT

    payload: float

    __slots__ = ()

    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        """Write the FloatNBT tag to the buffer.

        :param buf: The buffer to write to.
        :param with_type: Whether to include the type of the tag in the serialization.
        :param with_name: Whether to include the name of the tag in the serialization.

        :note: The float value is written as a 32-bit floating-point value in big-endian format.
        """
        self._write_header(buf, with_type=with_type, with_name=with_name)
        buf.write_value(StructFormat.FLOAT, self.payload)

    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> FloatNBT:
        """Read the FloatNBT tag from the buffer.

        :param buf: The buffer to read from.
        :param with_type: Whether to read the type of the tag from the buffer. If this is False, the type of the class
            will be used.
        :param with_name: Whether to read the name of the tag to the buffer as a TAG_String.

        :return: The FloatNBT tag.
        """
        name, tag_type = cls._read_header(buf, read_type=with_type, with_name=with_name)
        if tag_type != cls.TYPE:
            raise TypeError(f"Expected a {cls.TYPE.name} tag, but found a different tag ({tag_type.name}).")

        if buf.remaining < 4:
            raise IOError("Buffer does not contain enough data to read a float.")

        return FloatNBT(buf.read_value(StructFormat.FLOAT), name=name)

    def __float__(self) -> float:
        """Get the float value of the FloatNBT tag."""
        return self.payload

    def to_object(self) -> Mapping[str, float] | float:
        """Convert the FloatNBT tag to a python object.

        :return: A dictionary containing the name and the float value of the tag. If the tag has no name, the value
            will be returned directly.
        """
        if self.name:
            return {self.name: self.payload}
        return self.payload

    def __eq__(self, other: object) -> bool:
        """Check equality between two FloatNBT tags.

        :param other: The other FloatNBT tag to compare to.

        :return: True if the tags are equal, False otherwise.

        :note: The float values are compared with a small epsilon (1e-6) to account for floating-point errors.
        """
        if not isinstance(other, NBTag):
            raise NotImplementedError("Cannot compare an NBTag to a non-NBTag object.")
        # Compare the float values with a small epsilon
        if not (self.name == other.name and self.TYPE == other.TYPE):
            return False
        if not isinstance(other, self.__class__):  # pragma: no cover
            return False  # Should not happen if nobody messes with the TYPE attribute

        return abs(self.payload - other.payload) < 1e-6

    @property
    def value(self) -> float:
        """Get the float value of the FloatNBT tag."""
        return self.payload


class DoubleNBT(FloatNBT):
    """NBT tag representing a double-precision floating-point value, represented as a 64-bit IEEE 754-2008 binary64."""

    TYPE = NBTagType.DOUBLE

    __slots__ = ()

    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        """Write the DoubleNBT tag to the buffer.

        :param buf: The buffer to write to.
        :param with_type: Whether to include the type of the tag in the serialization.
        :param with_name: Whether to include the name of the tag in the serialization.

        :note: The double value is written as a 64-bit floating-point value in big-endian format.
        """
        self._write_header(buf, with_type=with_type, with_name=with_name)
        buf.write_value(StructFormat.DOUBLE, self.payload)

    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> DoubleNBT:
        """Read the DoubleNBT tag from the buffer.

        :param buf: The buffer to read from.
        :param with_type: Whether to read the type of the tag from the buffer. If this is False, the type of the class
            will be used.
        :param with_name: Whether to read the name of the tag to the buffer as a TAG_String.

        :return: The DoubleNBT tag.
        """
        name, tag_type = cls._read_header(buf, read_type=with_type, with_name=with_name)
        if tag_type != cls.TYPE:
            raise TypeError(f"Expected a {cls.TYPE.name} tag, but found a different tag ({tag_type.name}).")

        if buf.remaining < 8:
            raise IOError("Buffer does not contain enough data to read a double.")

        return DoubleNBT(buf.read_value(StructFormat.DOUBLE), name=name)


class ByteArrayNBT(NBTag):
    """NBT tag representing an array of bytes. The length of the array is stored as a signed 32-bit integer."""

    TYPE = NBTagType.BYTE_ARRAY

    __slots__ = ()

    payload: bytearray

    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        """Write the ByteArrayNBT tag to the buffer.

        :param buf: The buffer to write to.
        :param with_type: Whether to include the type of the tag in the serialization.
        :param with_name: Whether to include the name of the tag in the serialization.

        :note: The length of the byte array is written as a signed 32-bit integer in big-endian format.
        """
        self._write_header(buf, with_type=with_type, with_name=with_name)
        IntNBT(len(self.payload)).write_to(buf, with_type=False, with_name=False)
        buf.write(self.payload)

    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> ByteArrayNBT:
        """Read the ByteArrayNBT tag from the buffer.

        :param buf: The buffer to read from.
        :param with_type: Whether to read the type of the tag from the buffer. If this is False, the type of the class
            will be used.
        :param with_name: Whether to read the name of the tag to the buffer as a TAG_String.

        :return: The ByteArrayNBT tag.
        """
        name, tag_type = cls._read_header(buf, read_type=with_type, with_name=with_name)
        if tag_type != cls.TYPE:
            raise TypeError(f"Expected a {cls.TYPE.name} tag, but found a different tag ({tag_type.name}).")
        try:
            length = IntNBT.read_from(buf, with_type=False, with_name=False).value
        except IOError:
            raise IOError("Buffer does not contain enough data to read a byte array.") from None

        if length < 0:
            raise ValueError("Invalid byte array length.")

        if buf.remaining < length:
            raise IOError(
                f"Buffer does not contain enough data to read the byte array ({buf.remaining} < {length} bytes)."
            )

        return ByteArrayNBT(buf.read(length), name=name)

    def __bytes__(self) -> bytes:
        """Get the bytes value of the ByteArrayNBT tag."""
        return self.payload

    def to_object(self) -> Mapping[str, bytearray] | bytearray:
        """Convert the ByteArrayNBT tag to a python object.

        :return: A dictionary containing the name and the byte array value of the tag. If the tag has no name, the
            value will be returned directly.
        """
        if self.name:
            return {self.name: self.payload}
        return self.payload

    def __repr__(self) -> str:
        """Get a string representation of the ByteArrayNBT tag."""
        if self.name:
            return f"{self.__class__.__name__}[{self.name!r}](length={len(self.payload)})"
        if len(self.payload) < 8:
            return f"{self.__class__.__name__}(length={len(self.payload)}, {self.payload!r})"
        return f"{self.__class__.__name__}(length={len(self.payload)}, {bytes(self.payload[:7])!r}...)"

    @property
    def value(self) -> bytearray:
        """Get the bytes value of the ByteArrayNBT tag."""
        return self.payload


class StringNBT(NBTag):
    """NBT tag representing an UTF-8 string value. The length of the string is stored as a signed 16-bit integer."""

    TYPE = NBTagType.STRING

    __slots__ = ()

    payload: str

    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        """Write the StringNBT tag to the buffer.

        :param buf: The buffer to write to.
        :param with_type: Whether to include the type of the tag in the serialization.
        :param with_name: Whether to include the name of the tag in the serialization.

        :note: The length of the string is written as a signed 16-bit integer in big-endian format.
        """
        self._write_header(buf, with_type=with_type, with_name=with_name)
        if len(self.payload) > 32767:
            # Check the length of the string (can't generate strings that long in tests)
            raise ValueError("Maximum character limit for writing strings is 32767 characters.")  # pragma: no cover

        data = bytearray(self.payload, "utf-8")
        ShortNBT(len(data)).write_to(buf, with_type=False, with_name=False)
        buf.write(data)

    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> StringNBT:
        """Read the StringNBT tag from the buffer.

        :param buf: The buffer to read from.
        :param with_type: Whether to read the type of the tag from the buffer. If this is False, the type of the class
            will be used.
        :param with_name: Whether to read the name of the tag to the buffer as a TAG_String.

        :return: The StringNBT tag.
        """
        name, tag_type = cls._read_header(buf, read_type=with_type, with_name=with_name)
        if tag_type != cls.TYPE:
            raise TypeError(f"Expected a {cls.TYPE.name} tag, but found a different tag ({tag_type.name}).")
        try:
            length = ShortNBT.read_from(buf, with_type=False, with_name=False).value
        except IOError:
            raise IOError("Buffer does not contain enough data to read a string.") from None

        if length < 0:
            raise ValueError("Invalid string length.")

        if buf.remaining < length:
            raise IOError("Buffer does not contain enough data to read the string.")
        data = buf.read(length)
        try:
            return StringNBT(data.decode("utf-8"), name=name)
        except UnicodeDecodeError:
            raise  # We want to know it

    def __str__(self) -> str:
        """Get the string value of the StringNBT tag."""
        return self.payload

    def to_object(self) -> Mapping[str, str] | str:
        """Convert the StringNBT tag to a python object.

        :return: A dictionary containing the name and the string value of the tag. If the tag has no name, the value
            will be returned directly.
        """
        if self.name:
            return {self.name: self.payload}
        return self.payload

    @property
    def value(self) -> str:
        """Get the string value of the StringNBT tag."""
        return self.payload


class ListNBT(NBTag):
    """NBT tag representing a list of tags. All tags in the list must be of the same type."""

    TYPE = NBTagType.LIST

    __slots__ = ()

    payload: list[NBTag]

    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        """Write the ListNBT tag to the buffer.

        :param buf: The buffer to write to.
        :param with_type: Whether to include the type of the tag in the serialization.
        :param with_name: Whether to include the name of the tag in the serialization.

        :note: The tag type of the list is written as a single byte, followed by the length of the list as a signed
        32-bit integer in big-endian format. The tags in the list are then serialized one by one.
        """
        self._write_header(buf, with_type=with_type, with_name=with_name)

        if not self.payload:
            # Set the tag type to TAG_End if the list is empty
            EndNBT().write_to(buf, with_name=False)
            IntNBT(0).write_to(buf, with_name=False, with_type=False)
            return

        if not all(isinstance(tag, NBTag) for tag in self.payload):  # type: ignore # We want to check anyway
            raise ValueError(
                f"All items in a list must be NBTags. Got {self.payload!r}.\nUse NBTag.from_object() to convert "
                "objects to tags first."
            )

        tag_type = self.payload[0].TYPE
        ByteNBT(tag_type).write_to(buf, with_name=False, with_type=False)
        IntNBT(len(self.payload)).write_to(buf, with_name=False, with_type=False)
        for tag in self.payload:
            if tag_type != tag.TYPE:
                raise ValueError(f"All tags in a list must be of the same type, got tag {tag!r}")
            if tag.name != "":
                raise ValueError(f"All tags in a list must be unnamed, got tag {tag!r}")

            tag.write_to(buf, with_type=False, with_name=False)

    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> ListNBT:
        """Read the ListNBT tag from the buffer.

        :param buf: The buffer to read from.
        :param with_type: Whether to read the type of the tag from the buffer. If this is False, the type of the class
            will be used.
        :param with_name: Whether to read the name of the tag to the buffer as a TAG_String.

        :return: The ListNBT tag.
        """
        name, tag_type = cls._read_header(buf, read_type=with_type, with_name=with_name)
        if tag_type != cls.TYPE:
            raise TypeError(f"Expected a {cls.TYPE.name} tag, but found a different tag ({tag_type.name}).")
        list_tag_type = ByteNBT.read_from(buf, with_type=False, with_name=False).payload
        try:
            length = IntNBT.read_from(buf, with_type=False, with_name=False).value
        except IOError:
            raise IOError("Buffer does not contain enough data to read a list.") from None

        if length < 0 or list_tag_type == NBTagType.END:
            return ListNBT([], name=name)

        try:
            list_tag_type = NBTagType(list_tag_type)
        except ValueError:
            raise TypeError(f"Unknown tag type {list_tag_type}.") from None

        list_type_class = NBTag.ASSOCIATED_TYPES.get(list_tag_type, NBTag)
        if list_type_class == NBTag:
            raise TypeError(f"Unknown tag type {list_tag_type}.")  # pragma: no cover
        try:
            payload = [
                # The type is already known, so we don't need to read it again
                # List items are unnamed, so we don't need to read the name
                list_type_class.read_from(buf, with_type=False, with_name=False)
                for _ in range(length)
            ]
        except IOError:
            raise IOError("Buffer does not contain enough data to read the list.") from None
        return ListNBT(payload, name=name)

    def __iter__(self):
        """Iterate over the tags in the list."""
        yield from self.payload

    def __repr__(self) -> str:
        """Get a string representation of the ListNBT tag."""
        if self.name:
            return f"{self.__class__.__name__}[{self.name!r}](length={len(self.payload)}, {self.payload!r})"
        if len(self.payload) < 8:
            return f"{self.__class__.__name__}(length={len(self.payload)}, {self.payload!r})"
        return f"{self.__class__.__name__}(length={len(self.payload)}, {self.payload[:7]!r}...)"

    def to_object(self) -> Mapping[str, list[PayloadType]] | list[PayloadType]:
        """Convert the ListNBT tag to a python object.

        :return: A dictionary containing the name and the list of tags. If the tag has no name, the list will be
            returned directly.
        """
        self.payload: list[NBTag]
        if self.name:
            return {self.name: [tag.to_object() for tag in self.payload]}  # Extract the (unnamed) object from each tag
        return [tag.to_object() for tag in self.payload]  # Extract the (unnamed) object from each tag


class CompoundNBT(NBTag):
    """NBT tag representing a compound of named tags."""

    TYPE = NBTagType.COMPOUND

    __slots__ = ()

    payload: list[NBTag]

    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        """Write the CompoundNBT tag to the buffer.

        :param buf: The buffer to write to.
        :param with_type: Whether to include the type of the tag in the serialization.
        :param with_name: Whether to include the name of the tag in the serialization. THis only affects the name of
            the compound tag itself, not the names of the tags inside the compound.

        :note: The tags in the compound are serialized one by one, followed by an EndNBT tag.
        """
        self._write_header(buf, with_type=with_type, with_name=with_name)
        if not self.payload:
            EndNBT().write_to(buf, with_name=False, with_type=True)
            return
        if not all(isinstance(tag, NBTag) for tag in self.payload):  # type: ignore # We want to check anyway
            raise ValueError(
                f"All items in a compound must be NBTags. Got {self.payload!r}.\n"
                "Use NBTag.from_object() to convert objects to tags first."
            )

        if not all(tag.name for tag in self.payload):
            raise ValueError(f"All tags in a compound must be named, got tags {self.payload!r}")

        if len(self.payload) != len({tag.name for tag in self.payload}):  # Check for duplicate names
            raise ValueError("All tags in a compound must have unique names.")

        for tag in self.payload:
            tag.write_to(buf)
        EndNBT().write_to(buf, with_name=False, with_type=True)

    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> CompoundNBT:
        """Read the CompoundNBT tag from the buffer.

        :param buf: The buffer to read from.
        :param with_type: Whether to read the type of the tag from the buffer. If this is False, the type of the class
            will be used.
        :param with_name: Whether to read the name of the tag to the buffer as a TAG_String.

        :return: The CompoundNBT tag.
        """
        name, tag_type = cls._read_header(buf, read_type=with_type, with_name=with_name)
        if tag_type != cls.TYPE:
            raise TypeError(f"Expected a {cls.TYPE.name} tag, but found a different tag ({tag_type.name}).")

        payload = []
        while True:
            child_name, child_type = cls._read_header(buf, with_name=True, read_type=True)
            if child_type == NBTagType.END:
                break
            # The name and type of the tag have already been read
            tag = NBTag.ASSOCIATED_TYPES[child_type].read_from(buf, with_type=False, with_name=False)
            tag.name = child_name
            payload.append(tag)
        return CompoundNBT(payload, name=name)

    def __iter__(self):
        """Iterate over the tags in the compound."""
        for tag in self.payload:
            yield tag.name, tag

    def __repr__(self) -> str:
        """Get a string representation of the CompoundNBT tag."""
        if self.name:
            return f"{self.__class__.__name__}[{self.name!r}]({dict(self)})"
        return f"{self.__class__.__name__}({dict(self)})"

    def to_object(self) -> Mapping[str, Mapping[str, PayloadType]]:
        """Convert the CompoundNBT tag to a python object.

        :return: A dictionary containing the name and the dictionary of tags. If the tag has no name, the dictionary
            will be returned directly.
        """
        result = {}
        for tag in self.payload:
            if tag.name in result:
                raise ValueError(f"Duplicate tag name {tag.name!r} in the compound.")
            if tag.name == "":
                raise ValueError("All tags in a compound must have a name.")
            result.update(cast("dict[str, PayloadType]", tag.to_object()))
        if self.name:
            return {self.name: result}
        return result

    def __eq__(self, other: object) -> bool:
        """Check equality between two CompoundNBT tags.

        :param other: The other CompoundNBT tag to compare to.

        :return: True if the tags are equal, False otherwise.

        :note: The order of the tags is not guaranteed, but the names of the tags must match. This function assumes
            that there are no duplicate tags in the compound.
        """
        # The order of the tags is not guaranteed
        if not isinstance(other, NBTag):
            raise NotImplementedError("Cannot compare an NBTag to a non-NBTag object.")
        if self.name != other.name or self.TYPE != other.TYPE:
            return False
        if not isinstance(other, self.__class__):  # pragma: no cover
            return False  # Should not happen if nobody messes with the TYPE attribute
        if len(self.payload) != len(other.payload):
            return False
        return all(tag in other.payload for tag in self.payload)


class IntArrayNBT(NBTag):
    """NBT tag representing an array of integers. The length of the array is stored as a signed 32-bit integer."""

    TYPE = NBTagType.INT_ARRAY

    __slots__ = ()

    payload: list[int]

    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        """Write the IntArrayNBT tag to the buffer.

        :param buf: The buffer to write to.
        :param with_type: Whether to include the type of the tag in the serialization.
        :param with_name: Whether to include the name of the tag in the serialization.

        :note: The length of the integer array is written as a signed 32-bit integer in big-endian format.
        """
        self._write_header(buf, with_type=with_type, with_name=with_name)

        if any(not isinstance(item, int) for item in self.payload):  # type: ignore # We want to check anyway
            raise ValueError("All items in an integer array must be integers.")

        if any(item < -(1 << 31) or item >= 1 << 31 for item in self.payload):
            raise OverflowError("Integer array contains values out of range.")

        IntNBT(len(self.payload)).write_to(buf, with_name=False, with_type=False)
        for i in self.payload:
            IntNBT(i).write_to(buf, with_name=False, with_type=False)

    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> IntArrayNBT:
        """Read the IntArrayNBT tag from the buffer.

        :param buf: The buffer to read from.
        :param with_type: Whether to read the type of the tag from the buffer. If this is False, the type of the class
            will be used.
        :param with_name: Whether to read the name of the tag to the buffer as a TAG_String.

        :return: The IntArrayNBT tag.
        """
        name, tag_type = cls._read_header(buf, read_type=with_type, with_name=with_name)
        if tag_type != NBTagType.INT_ARRAY:
            raise TypeError(f"Expected an INT_ARRAY tag, but found a different tag ({tag_type}).")
        length = IntNBT.read_from(buf, with_type=False, with_name=False).value
        try:
            payload = [IntNBT.read_from(buf, with_type == NBTagType.INT, with_name=False).value for _ in range(length)]
        except IOError:
            raise IOError(
                "Buffer does not contain enough data to read the entire integer array. (Incomplete data)"
            ) from None
        return IntArrayNBT(payload, name=name)

    def __repr__(self) -> str:
        """Get a string representation of the IntArrayNBT tag."""
        if self.name:
            return f"{self.__class__.__name__}[{self.name!r}](length={len(self.payload)}, {self.payload!r})"
        if len(self.payload) < 8:
            return f"{self.__class__.__name__}(length={len(self.payload)}, {self.payload!r})"
        return f"{self.__class__.__name__}(length={len(self.payload)}, {self.payload[:7]!r}...)"

    def __iter__(self):
        """Iterate over the integers in the array."""
        yield from self.payload

    def to_object(self) -> Mapping[str, list[int]] | list[int]:
        """Convert the IntArrayNBT tag to a python object.

        :return: A dictionary containing the name and the list of integers. If the tag has no name, the list will be
            returned directly.
        """
        if self.name:
            return {self.name: self.payload}
        return self.payload

    @property
    def value(self) -> list[int]:
        """Get the list of integers in the IntArrayNBT tag."""
        return self.payload


class LongArrayNBT(IntArrayNBT):
    """NBT tag representing an array of longs. The length of the array is stored as a signed 32-bit integer."""

    TYPE = NBTagType.LONG_ARRAY

    __slots__ = ()

    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        """Write the LongArrayNBT tag to the buffer.

        :param buf: The buffer to write to.
        :param with_type: Whether to include the type of the tag in the serialization.
        :param with_name: Whether to include the name of the tag in the serialization.

        :note: The length of the long array is written as a signed 32-bit integer in big-endian format.
        """
        self._write_header(buf, with_type=with_type, with_name=with_name)

        if any(not isinstance(item, int) for item in self.payload):  # type: ignore # We want to check anyway
            raise ValueError(f"All items in a long array must be integers. ({self.payload})")

        if any(item < -(1 << 63) or item >= 1 << 63 for item in self.payload):
            raise OverflowError(f"Long array contains values out of range. ({self.payload})")

        IntNBT(len(self.payload)).write_to(buf, with_name=False, with_type=False)
        for i in self.payload:
            LongNBT(i).write_to(buf, with_name=False, with_type=False)

    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> LongArrayNBT:
        """Read the LongArrayNBT tag from the buffer.

        :param buf: The buffer to read from.
        :param with_type: Whether to read the type of the tag from the buffer. If this is False, the type of the class
            will be used.
        :param with_name: Whether to read the name of the tag to the buffer as a TAG_String.

        :return: The LongArrayNBT tag.
        """
        name, tag_type = cls._read_header(buf, read_type=with_type, with_name=with_name)
        if tag_type != NBTagType.LONG_ARRAY:
            raise TypeError(f"Expected a LONG_ARRAY tag, but found a different tag ({tag_type}).")
        length = IntNBT.read_from(buf, with_type=False, with_name=False).payload

        try:
            payload = [LongNBT.read_from(buf, with_type=False, with_name=False).payload for _ in range(length)]
        except IOError:
            raise IOError(
                "Buffer does not contain enough data to read the entire long array. (Incomplete data)"
            ) from None
        return LongArrayNBT(payload, name=name)


# endregion
