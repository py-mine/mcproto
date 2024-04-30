from __future__ import annotations

from abc import abstractmethod
from enum import IntEnum
from typing import Iterator, List, Mapping, Sequence, Tuple, Type, Union, cast

from typing_extensions import TypeAlias, override
from typing import Protocol, runtime_checkable  # Have to be imported from the same place

from mcproto.buffer import Buffer
from mcproto.protocol.base_io import StructFormat
from mcproto.types.abc import MCType

__all__ = [
    "NBTagConvertible",
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

"""
Implementation of the NBT (Named Binary Tag) format used in Minecraft as described in the NBT specification
(:seealso: :class:`NBTagType`).
"""
# region NBT Specification


class NBTagType(IntEnum):
    """Enumeration of the different types of NBT tags.

    Source : https://web.archive.org/web/20110723210920/http://www.minecraft.net/docs/NBT.txt

    Named Binary Tag specification

    NBT (Named Binary Tag) is a tag based binary format designed to carry large amounts of binary data with smaller
    amounts of additional data.
    An NBT file consists of a single GZIPped Named Tag of type TAG_Compound.

    A Named Tag has the following format:

        byte tagType
        TAG_String name
        [payload]

    The tagType is a single byte defining the contents of the payload of the tag.

    The name is a descriptive name, and can be anything (eg "cat", "banana", "Hello World!"). It has nothing to do with
    the tagType.
    The purpose for this name is to name tags so parsing is easier and can be made to only look for certain recognized
    tag names.
    Exception: If tagType is TAG_End, the name is skipped and assumed to be "".

    The [payload] varies by tagType.

    Note that ONLY Named Tags carry the name and tagType data. Explicitly identified Tags (such as TAG_String above)
    only contains the payload.


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
                 A sequential list of Tags (not Named Tags), of type <typeId>. The length of this array is <length>
                Tags
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
    bytes,
    str,
    "NBTag",
    Sequence["PayloadType"],
    Mapping[str, "PayloadType"],
]


@runtime_checkable
class NBTagConvertible(Protocol):
    """Protocol for objects that can be converted to an NBT tag."""

    __slots__ = ()

    def to_nbt(self, name: str = "") -> NBTag:
        """Convert the object to an NBT tag.

        :param name: The name of the tag.

        :return: The NBT tag created from the object.
        """
        ...


FromObjectType: TypeAlias = Union[
    int,
    float,
    bytes,
    str,
    NBTagConvertible,
    Sequence["FromObjectType"],
    Mapping[str, "FromObjectType"],
]

FromObjectSchema: TypeAlias = Union[
    Type["NBTag"],
    Type[NBTagConvertible],
    Sequence["FromObjectSchema"],
    Mapping[str, "FromObjectSchema"],
]


class NBTag(MCType, NBTagConvertible):
    """Base class for NBT tags.

    In MC v1.20.2+ the type and name of the root tag are not written to the buffer, and unless specified, the type of
    the tag is assumed to be TAG_Compound.
    """

    __slots__ = ("name", "payload")

    def __init__(self, payload: PayloadType, name: str = ""):
        self.name = name
        self.payload = payload

    @override
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

    def _write_header(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        if with_type:
            tag_type = _get_tag_type(self)
            buf.write_value(StructFormat.BYTE, tag_type.value)
        if with_name and self.name:
            StringNBT(self.name).write_to(buf, with_type=False, with_name=False)

    @abstractmethod
    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        """Write the NBT tag to the buffer."""
        ...

    @override
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

        tag_class = ASSOCIATED_TYPES[tag_type]
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
        if read_type:
            try:
                tag_type = NBTagType(buf.read_value(StructFormat.BYTE))
            except OSError as exc:
                raise IOError("Buffer is empty.") from exc
            except ValueError as exc:
                raise TypeError("Invalid tag type.") from exc
        else:
            tag_type = _get_tag_type(cls)

        if tag_type is NBTagType.END:
            return "", tag_type

        name = StringNBT.read_from(buf, with_type=False, with_name=False).value if with_name else ""

        return name, tag_type

    @classmethod
    @abstractmethod
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
        ...

    @staticmethod
    def from_object(data: FromObjectType, schema: FromObjectSchema, name: str = "") -> NBTag:
        """Create an NBT tag from a dictionary.

        :param data: The dictionary to create the NBT tag from.
        :param schema: The schema used to create the NBT tags.

            If the schema is a list, the data must be a list and the schema must either contain a single element
            representing the type of the elements in the list or multiple dictionaries or lists representing the types
            of the elements in the list since they are the only types that have a variable type.

        Example:
            ```python
            schema = [IntNBT]
            data = [1, 2, 3]
            schema = [[IntNBT], [StringNBT]]
            data = [[1, 2, 3], ["a", "b", "c"]]
            ```

            If the schema is a dictionary, the data must be a dictionary and the schema must contain the keys and the
            types of the values in the dictionary.

        Example:
            ```python
            schema = {"key": IntNBT}
            data = {"key": 1}
            ```

            If the schema is a subclass of NBTag, the data will be passed to the constructor of the schema.
            If the schema is not a list, dictionary or subclass of NBTag, the data will be converted to an NBT tag
            using the `to_nbt` method of the data.

        :param name: The name of the NBT tag.

        :return: The NBT tag created from the dictionary.
        """
        if isinstance(schema, (list, tuple)):
            if not isinstance(data, list):
                raise TypeError("Expected a list, but found a different type.")
            payload: list[NBTag] = []
            if len(schema) > 1:
                if not all(isinstance(item, (list, dict)) for item in schema):
                    raise TypeError("Expected a list of lists or dictionaries, but found a different type.")
                if len(schema) != len(data):
                    raise ValueError("The schema and the data must have the same length.")
                for item, sub_schema in zip(data, schema):
                    payload.append(NBTag.from_object(item, sub_schema))
            else:
                if len(schema) == 0 and len(data) > 0:
                    raise ValueError("The schema is empty, but the data is not.")
                if len(schema) == 0:
                    return ListNBT([], name=name)

                schema = schema[0]
                for item in data:
                    payload.append(NBTag.from_object(item, schema))
            return ListNBT(payload, name=name)
        if isinstance(schema, dict):
            if not isinstance(data, dict):
                raise TypeError("Expected a dictionary, but found a different type.")
            payload: list[NBTag] = []
            for key, value in data.items():
                payload.append(NBTag.from_object(value, schema[key], name=key))
            return CompoundNBT(payload, name=name)
        if not isinstance(schema, type) or not issubclass(schema, (NBTag, NBTagConvertible)):  # type: ignore
            raise TypeError("The schema must be a list, dict or a subclass of either NBTag or NBTagConvertible.")
        if isinstance(data, schema):
            return data.to_nbt(name=name)
        schema = cast(Type[NBTag], schema)  # Last option
        if issubclass(schema, (CompoundNBT, ListNBT)):
            raise ValueError("The schema must specify the type of the elements in CompoundNBT and ListNBT tags.")
        if isinstance(data, dict):
            if len(data) != 1:
                raise ValueError("Expected a dictionary with a single key-value pair.")
            key, value = next(iter(data.items()))
            return schema.from_object(value, schema, name=key)
        if not isinstance(data, (bytes, str, int, float, list)):
            raise TypeError(f"Expected a bytes, str, int, float, but found {type(data).__name__}.")
        if isinstance(data, list) and not all(isinstance(item, int) for item in data):
            raise TypeError("Expected a list of integers.")  # LongArrayNBT, IntArrayNBT

        data = cast(Union[bytes, str, int, float, List[int]], data)
        return schema(data, name=name)

    def to_object(
        self, include_schema: bool = False, include_name: bool = False
    ) -> PayloadType | Mapping[str, PayloadType] | tuple[PayloadType | Mapping[str, PayloadType], FromObjectSchema]:
        """Convert the NBT tag to a python object.

        :param include_schema: Whether to return a schema describing the types of the original tag.
        :param include_name: Whether to include the name of the tag in the output.
            If the tag has no name, the name will be set to "".

        :return: Either :
            - A python object representing the payload of the tag. (default)
            - A dictionary containing the name associated with a python object representing the payload of the tag.
            - A tuple which includes one of the above and a schema describing the types of the original tag.
        """
        if type(self) is EndNBT:
            raise NotImplementedError("Cannot convert an EndNBT tag to a python object.")
        if type(self) in (CompoundNBT, ListNBT):
            raise TypeError(
                f"Use the `{type(self).__name__}.to_object()` method to convert the tag to a python object."
            )
        result = self.payload if not include_name else {self.name: self.payload}
        if include_schema:
            return result, type(self)
        return result

    @override
    def __repr__(self) -> str:
        if self.name:
            return f"{type(self).__name__}[{self.name!r}]({self.payload!r})"
        return f"{type(self).__name__}({self.payload!r})"

    @override
    def __eq__(self, other: object) -> bool:
        """Check equality between two NBT tags."""
        if not isinstance(other, NBTag):
            raise NotImplementedError("Cannot compare an NBTag to a non-NBTag object.")
        if type(self) is not type(other):
            return False
        return self.name == other.name and self.payload == other.payload

    @override
    def to_nbt(self, name: str = "") -> NBTag:
        """Convert the object to an NBT tag.

        ..warning This is already an NBT tag, so it will modify the name of the tag and return itself.
        """
        self.name = name
        return self

    @property
    @abstractmethod
    def value(self) -> PayloadType:
        """Get the payload of the NBT tag in a python-friendly format."""
        ...


# endregion
# region NBT tags types


class EndNBT(NBTag):
    """Sentinel tag used to mark the end of a TAG_Compound."""

    __slots__ = ()

    def __init__(self):
        """Create a new EndNBT tag."""
        super().__init__(0, name="")

    @override
    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = False) -> None:
        """Write the EndNBT tag to the buffer.

        :param buf: The buffer to write to.
        :param with_type: Whether to include the type of the tag in the serialization.
        :param with_name: Whether to include the name of the tag in the serialization.
        """
        self._write_header(buf, with_type=with_type, with_name=False)

    @override
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
        if _get_tag_type(cls) != tag_type:
            raise TypeError(f"Expected a {_get_tag_type(cls).name} tag, but found a different tag ({tag_type.name}).")
        return EndNBT()

    @override
    def to_object(
        self, include_schema: bool = False, include_name: bool = False
    ) -> PayloadType | Mapping[str, PayloadType]:
        """Convert the EndNBT tag to a python object.

        :param include_schema: Whether to return a schema describing the types of the original tag.
        :param include_name: Whether to include the name of the tag in the output.

        :return: None
        """
        return NotImplemented

    @property
    @override
    def value(self) -> PayloadType:
        """Get the payload of the EndNBT tag in a python-friendly format."""
        return NotImplemented


class ByteNBT(NBTag):
    """NBT tag representing a single byte value, represented as a signed 8-bit integer."""

    __slots__ = ()
    payload: int

    @override
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

    @override
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
        if _get_tag_type(cls) != tag_type:
            raise TypeError(f"Expected a {_get_tag_type(cls).name} tag, but found a different tag ({tag_type.name}).")

        if buf.remaining < 1:
            raise IOError("Buffer does not contain enough data to read a byte. (Empty buffer)")

        return ByteNBT(buf.read_value(StructFormat.BYTE), name=name)

    def __int__(self) -> int:
        """Get the integer value of the ByteNBT tag."""
        return self.payload

    @property
    @override
    def value(self) -> int:
        """Get the integer value of the IntNBT tag."""
        return self.payload


class ShortNBT(ByteNBT):
    """NBT tag representing a short value, represented as a signed 16-bit integer."""

    __slots__ = ()

    @override
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

    @override
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
        if _get_tag_type(cls) != tag_type:
            raise TypeError(f"Expected a {_get_tag_type(cls).name} tag, but found a different tag ({tag_type.name}).")

        if buf.remaining < 2:
            raise IOError("Buffer does not contain enough data to read a short.")

        return ShortNBT(int.from_bytes(buf.read(2), "big", signed=True), name=name)


class IntNBT(ByteNBT):
    """NBT tag representing an integer value, represented as a signed 32-bit integer."""

    __slots__ = ()

    @override
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

    @override
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
        if _get_tag_type(cls) != tag_type:
            raise TypeError(f"Expected a {_get_tag_type(cls).name} tag, but found a different tag ({tag_type.name}).")

        if buf.remaining < 4:
            raise IOError("Buffer does not contain enough data to read an int.")

        return IntNBT(int.from_bytes(buf.read(4), "big", signed=True), name=name)


class LongNBT(ByteNBT):
    """NBT tag representing a long value, represented as a signed 64-bit integer."""

    __slots__ = ()

    @override
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

    @override
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
        if _get_tag_type(cls) != tag_type:
            raise TypeError(f"Expected a {_get_tag_type(cls).name} tag, but found a different tag ({tag_type.name}).")

        if buf.remaining < 8:
            raise IOError("Buffer does not contain enough data to read a long.")

        payload = int.from_bytes(buf.read(8), "big", signed=True)
        return LongNBT(payload, name=name)


class FloatNBT(NBTag):
    """NBT tag representing a floating-point value, represented as a 32-bit IEEE 754-2008 binary32 value."""

    payload: float

    __slots__ = ()

    @override
    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        """Write the FloatNBT tag to the buffer.

        :param buf: The buffer to write to.
        :param with_type: Whether to include the type of the tag in the serialization.
        :param with_name: Whether to include the name of the tag in the serialization.

        :note: The float value is written as a 32-bit floating-point value in big-endian format.
        """
        self._write_header(buf, with_type=with_type, with_name=with_name)
        buf.write_value(StructFormat.FLOAT, self.payload)

    @override
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
        if _get_tag_type(cls) != tag_type:
            raise TypeError(f"Expected a {_get_tag_type(cls).name} tag, but found a different tag ({tag_type.name}).")

        if buf.remaining < 4:
            raise IOError("Buffer does not contain enough data to read a float.")

        return FloatNBT(buf.read_value(StructFormat.FLOAT), name=name)

    def __float__(self) -> float:
        """Get the float value of the FloatNBT tag."""
        return self.payload

    @override
    def __eq__(self, other: object) -> bool:
        """Check equality between two FloatNBT tags.

        :param other: The other FloatNBT tag to compare to.

        :return: True if the tags are equal, False otherwise.

        :note: The float values are compared with a small epsilon (1e-6) to account for floating-point errors.
        """
        if not isinstance(other, NBTag):
            raise NotImplementedError("Cannot compare an NBTag to a non-NBTag object.")
        # Compare the float values with a small epsilon
        if type(self) is not type(other):
            return False
        other.payload = cast(float, other.payload)
        if self.name != other.name:
            return False
        return abs(self.payload - other.payload) < 1e-6

    @property
    @override
    def value(self) -> float:
        """Get the float value of the FloatNBT tag."""
        return self.payload


class DoubleNBT(FloatNBT):
    """NBT tag representing a double-precision floating-point value, represented as a 64-bit IEEE 754-2008 binary64."""

    __slots__ = ()

    @override
    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        """Write the DoubleNBT tag to the buffer.

        :param buf: The buffer to write to.
        :param with_type: Whether to include the type of the tag in the serialization.
        :param with_name: Whether to include the name of the tag in the serialization.

        :note: The double value is written as a 64-bit floating-point value in big-endian format.
        """
        self._write_header(buf, with_type=with_type, with_name=with_name)
        buf.write_value(StructFormat.DOUBLE, self.payload)

    @override
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
        if _get_tag_type(cls) != tag_type:
            raise TypeError(f"Expected a {_get_tag_type(cls).name} tag, but found a different tag ({tag_type.name}).")

        if buf.remaining < 8:
            raise IOError("Buffer does not contain enough data to read a double.")

        return DoubleNBT(buf.read_value(StructFormat.DOUBLE), name=name)


class ByteArrayNBT(NBTag):
    """NBT tag representing an array of bytes. The length of the array is stored as a signed 32-bit integer."""

    __slots__ = ()

    payload: bytes

    @override
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

    @override
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
        if _get_tag_type(cls) != tag_type:
            raise TypeError(f"Expected a {_get_tag_type(cls).name} tag, but found a different tag ({tag_type.name}).")
        try:
            length = IntNBT.read_from(buf, with_type=False, with_name=False).value
        except IOError as exc:
            raise IOError("Buffer does not contain enough data to read a byte array.") from exc

        if length < 0:
            raise ValueError("Invalid byte array length.")

        if buf.remaining < length:
            raise IOError(
                f"Buffer does not contain enough data to read the byte array ({buf.remaining} < {length} bytes)."
            )

        return ByteArrayNBT(bytes(buf.read(length)), name=name)

    def __bytes__(self) -> bytes:
        """Get the bytes value of the ByteArrayNBT tag."""
        return self.payload

    @override
    def __repr__(self) -> str:
        """Get a string representation of the ByteArrayNBT tag."""
        if self.name:
            return f"{type(self).__name__}[{self.name!r}](length={len(self.payload)})"
        if len(self.payload) < 8:
            return f"{type(self).__name__}(length={len(self.payload)}, {self.payload!r})"
        return f"{type(self).__name__}(length={len(self.payload)}, {bytes(self.payload[:7])!r}...)"

    @property
    @override
    def value(self) -> bytes:
        """Get the bytes value of the ByteArrayNBT tag."""
        return self.payload


class StringNBT(NBTag):
    """NBT tag representing an UTF-8 string value. The length of the string is stored as a signed 16-bit integer."""

    __slots__ = ()

    payload: str

    @override
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

        data = bytes(self.payload, "utf-8")
        ShortNBT(len(data)).write_to(buf, with_type=False, with_name=False)
        buf.write(data)

    @override
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
        if _get_tag_type(cls) != tag_type:
            raise TypeError(f"Expected a {_get_tag_type(cls).name} tag, but found a different tag ({tag_type.name}).")
        try:
            length = ShortNBT.read_from(buf, with_type=False, with_name=False).value
        except IOError as exc:
            raise IOError("Buffer does not contain enough data to read a string.") from exc

        if length < 0:
            raise ValueError("Invalid string length.")

        if buf.remaining < length:
            raise IOError("Buffer does not contain enough data to read the string.")
        data = buf.read(length)
        try:
            return StringNBT(data.decode("utf-8"), name=name)
        except UnicodeDecodeError:
            raise  # We want to know it

    @override
    def __str__(self) -> str:
        """Get the string value of the StringNBT tag."""
        return self.payload

    @property
    @override
    def value(self) -> str:
        """Get the string value of the StringNBT tag."""
        return self.payload


class ListNBT(NBTag):
    """NBT tag representing a list of tags. All tags in the list must be of the same type."""

    __slots__ = ()

    payload: list[NBTag]

    @override
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

        tag_type = _get_tag_type(self.payload[0])
        ByteNBT(tag_type).write_to(buf, with_name=False, with_type=False)
        IntNBT(len(self.payload)).write_to(buf, with_name=False, with_type=False)
        for tag in self.payload:
            if tag_type != _get_tag_type(tag):
                raise ValueError(f"All tags in a list must be of the same type, got tag {tag!r}")
            if tag.name != "":
                raise ValueError(f"All tags in a list must be unnamed, got tag {tag!r}")

            tag.write_to(buf, with_type=False, with_name=False)

    @override
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
        if _get_tag_type(cls) != tag_type:
            raise TypeError(f"Expected a {_get_tag_type(cls).name} tag, but found a different tag ({tag_type.name}).")
        list_tag_type = ByteNBT.read_from(buf, with_type=False, with_name=False).payload
        try:
            length = IntNBT.read_from(buf, with_type=False, with_name=False).value
        except IOError as exc:
            raise IOError("Buffer does not contain enough data to read a list.") from exc

        if length < 1 or list_tag_type is NBTagType.END:
            return ListNBT([], name=name)

        try:
            list_tag_type = NBTagType(list_tag_type)
        except ValueError as exc:
            raise TypeError(f"Unknown tag type {list_tag_type}.") from exc

        list_type_class = ASSOCIATED_TYPES.get(list_tag_type, NBTag)
        if list_type_class is NBTag:
            raise TypeError(f"Unknown tag type {list_tag_type}.")  # pragma: no cover
        try:
            payload = [list_type_class.read_from(buf, with_type=False, with_name=False) for _ in range(length)]
        except IOError as exc:
            raise IOError("Buffer does not contain enough data to read the list.") from exc
        return ListNBT(payload, name=name)

    def __iter__(self) -> Iterator[NBTag]:
        """Iterate over the tags in the list."""
        yield from self.payload

    @override
    def __repr__(self) -> str:
        """Get a string representation of the ListNBT tag."""
        if self.name:
            return f"{type(self).__name__}[{self.name!r}](length={len(self.payload)}, {self.payload!r})"
        if len(self.payload) < 8:
            return f"{type(self).__name__}(length={len(self.payload)}, {self.payload!r})"
        return f"{type(self).__name__}(length={len(self.payload)}, {self.payload[:7]!r}...)"

    @override
    def to_object(
        self, include_schema: bool = False, include_name: bool = False
    ) -> (
        list[PayloadType]
        | Mapping[str, list[PayloadType]]
        | tuple[list[PayloadType] | Mapping[str, list[PayloadType]], list[FromObjectSchema]]
    ):
        """Convert the ListNBT tag to a python object.

        :param include_schema: Whether to return a schema describing the types of the original tag.
        :param include_name: Whether to include the name of the tag in the output.
            If the tag has no name, the name will be set to "".

        :return: Either :
        - A list containing the payload of the tag. (default)
        - A dictionary containing the name associated with a list containing the payload of the tag.
        - A tuple which includes one of the above and a list of schemas describing the types of the original tag.
        """
        result = [tag.to_object() for tag in self.payload]
        result = cast(List[PayloadType], result)
        result = result if not include_name else {self.name: result}
        if include_schema:
            subschemas = [
                cast(
                    Tuple[PayloadType, FromObjectSchema],
                    tag.to_object(include_schema=True),
                )[1]
                for tag in self.payload
            ]
            if len(result) == 0:
                return result, []

            first = subschemas[0]
            if all(schema == first for schema in subschemas):
                return result, [first]

            if not isinstance(first, (dict, list)):
                raise TypeError(f"The schema must contain either a dict or a list. Found {first!r}")
            # This will take care of ensuring either everything is a dict or a list
            if not all(isinstance(schema, type(first)) for schema in subschemas):
                raise TypeError(f"All items in the list must have the same type. Found {subschemas!r}")
            return result, subschemas
        return result

    @property
    @override
    def value(self) -> list[PayloadType]:
        """Get the payload of the ListNBT tag in a python-friendly format."""
        return [tag.value for tag in self.payload]


class CompoundNBT(NBTag):
    """NBT tag representing a compound of named tags."""

    __slots__ = ()

    payload: list[NBTag]

    @override
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

    @override
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
        if _get_tag_type(cls) != tag_type:
            raise TypeError(f"Expected a {_get_tag_type(cls).name} tag, but found a different tag ({tag_type.name}).")

        payload: list[NBTag] = []
        while True:
            child_name, child_type = cls._read_header(buf, with_name=True, read_type=True)
            if child_type is NBTagType.END:
                break
            # The name and type of the tag have already been read
            tag = ASSOCIATED_TYPES[child_type].read_from(buf, with_type=False, with_name=False)
            tag.name = child_name
            payload.append(tag)
        return CompoundNBT(payload, name=name)

    def __iter__(self):
        """Iterate over the tags in the compound."""
        for tag in self.payload:
            yield tag.name, tag

    @override
    def __repr__(self) -> str:
        """Get a string representation of the CompoundNBT tag."""
        if self.name:
            return f"{type(self).__name__}[{self.name!r}]({dict(self)})"
        return f"{type(self).__name__}({dict(self)})"

    @override
    def to_object(
        self, include_schema: bool = False, include_name: bool = False
    ) -> (
        Mapping[str, PayloadType]
        | Mapping[str, Mapping[str, PayloadType]]
        | tuple[
            Mapping[str, PayloadType] | Mapping[str, Mapping[str, PayloadType]],
            Mapping[str, FromObjectSchema],
        ]
    ):
        """Convert the CompoundNBT tag to a python object.

        :param include_schema: Whether to return a schema describing the types of the original tag and its children.
        :param include_name: Whether to include the name of the tag in the output.
            If the tag has no name, the name will be set to "".

        :return: Either :
        - A dictionary containing the payload of the tag. (default)
        - A dictionary containing the name associated with a dictionary containing the payload of the tag.
        - A tuple which includes one of the above and a dictionary of schemas describing the types of the original tag.
        """
        result = {tag.name: tag.to_object() for tag in self.payload}
        result = cast(Mapping[str, PayloadType], result)
        result = result if not include_name else {self.name: result}
        if include_schema:
            subschemas = {
                tag.name: cast(
                    Tuple[PayloadType, FromObjectSchema],
                    tag.to_object(include_schema=True),
                )[1]
                for tag in self.payload
            }
            return result, subschemas
        return result

    @override
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
        if type(self) is not type(other):
            return False
        if self.name != other.name:
            return False
        other = cast(CompoundNBT, other)
        if len(self.payload) != len(other.payload):
            return False
        return all(tag in other.payload for tag in self.payload)

    @property
    @override
    def value(self) -> dict[str, PayloadType]:
        """Get the dictionary of tags in the CompoundNBT tag."""
        return {tag.name: tag.value for tag in self.payload}


class IntArrayNBT(NBTag):
    """NBT tag representing an array of integers. The length of the array is stored as a signed 32-bit integer."""

    __slots__ = ()

    payload: list[int]

    @override
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

    @override
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
            payload = [IntNBT.read_from(buf, with_type is NBTagType.INT, with_name=False).value for _ in range(length)]
        except IOError as exc:
            raise IOError(
                "Buffer does not contain enough data to read the entire integer array. (Incomplete data)"
            ) from exc
        return IntArrayNBT(payload, name=name)

    @override
    def __repr__(self) -> str:
        """Get a string representation of the IntArrayNBT tag."""
        if self.name:
            return f"{type(self).__name__}[{self.name!r}](length={len(self.payload)}, {self.payload!r})"
        if len(self.payload) < 8:
            return f"{type(self).__name__}(length={len(self.payload)}, {self.payload!r})"
        return f"{type(self).__name__}(length={len(self.payload)}, {self.payload[:7]!r}...)"

    def __iter__(self) -> Iterator[int]:
        """Iterate over the integers in the array."""
        yield from self.payload

    @property
    @override
    def value(self) -> list[int]:
        """Get the list of integers in the IntArrayNBT tag."""
        return self.payload


class LongArrayNBT(IntArrayNBT):
    """NBT tag representing an array of longs. The length of the array is stored as a signed 32-bit integer."""

    __slots__ = ()

    @override
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

    @override
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
        except IOError as exc:
            raise IOError(
                "Buffer does not contain enough data to read the entire long array. (Incomplete data)"
            ) from exc
        return LongArrayNBT(payload, name=name)


# endregion

# region: NBT Associated Types
ASSOCIATED_TYPES: dict[NBTagType, type[NBTag]] = {
    NBTagType.END: EndNBT,
    NBTagType.BYTE: ByteNBT,
    NBTagType.SHORT: ShortNBT,
    NBTagType.INT: IntNBT,
    NBTagType.LONG: LongNBT,
    NBTagType.FLOAT: FloatNBT,
    NBTagType.DOUBLE: DoubleNBT,
    NBTagType.BYTE_ARRAY: ByteArrayNBT,
    NBTagType.STRING: StringNBT,
    NBTagType.LIST: ListNBT,
    NBTagType.COMPOUND: CompoundNBT,
    NBTagType.INT_ARRAY: IntArrayNBT,
    NBTagType.LONG_ARRAY: LongArrayNBT,
}


def _get_tag_type(tag: NBTag | type[NBTag]) -> NBTagType:
    """Get the tag type of an NBTag object or class.

    :param tag: The tag to get the type of.

    :return: The tag type of the tag.
    """
    cls = tag if isinstance(tag, type) else type(tag)

    if cls is NBTag:
        return NBTagType.COMPOUND
    for tag_type, tag_cls in ASSOCIATED_TYPES.items():
        if cls is tag_cls:
            return tag_type

    raise ValueError(f"Unknown tag type {cls}.")  # pragma: no cover


# endregion
