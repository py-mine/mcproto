from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterator, Mapping, Sequence
from enum import IntEnum
from typing import ClassVar, Hashable, Protocol, Union, cast, final, runtime_checkable

from attrs import define
from typing_extensions import Self, TypeAlias, override

from mcproto.buffer import Buffer
from mcproto.protocol.base_io import FLOAT_FORMATS_TYPE, INT_FORMATS_TYPE, StructFormat
from mcproto.types.abc import MCType
from mcproto.utils.abc import RequiredParamsABCMixin

__all__ = [
    "ByteArrayNBT",
    "ByteNBT",
    "CompoundNBT",
    "DoubleNBT",
    "EndNBT",
    "FloatNBT",
    "IntArrayNBT",
    "IntNBT",
    "ListNBT",
    "LongArrayNBT",
    "LongNBT",
    "NBTag",
    "NBTagConvertible",
    "NBTagType",
    "ShortNBT",
    "StringNBT",
]

"""
Implementation of the NBT (Named Binary Tag) format used in Minecraft as described in the NBT specification

Source : `Minecraft NBT Spec <https://web.archive.org/web/20110723210920/http://www.minecraft.net/docs/NBT.txt>`_

Named Binary Tag specification

NBT (Named Binary Tag) is a tag based binary format designed to carry large amounts of binary data with smaller
amounts of additional data.
An NBT file consists of a single GZIPped Named Tag of type TAG_Compound.

A Named Tag has the following format:

    byte tagType
    TAG_String name
    [payload]

* The tagType is a single byte defining the contents of the payload of the tag.
* The name is a descriptive name, and can be anything (eg "cat", "banana", "Hello World!").
  The purpose for this name is to name tags so parsing is easier and can be made to only look for certain recognized
  tag names. Exception: If tagType is TAG_End, the name is skipped and assumed to be "".
* The [payload] varies by tagType.

Note that ONLY Named Tags carry the name and tagType data. Explicitly identified Tags (such as TAG_String)
only contains the payload.

.. seealso:: :class:`NBTagType`
"""

# region NBT Specification,


class NBTagType(IntEnum):
    """Enumeration of the different types of NBT tags.

    See the documentation of the individual variants for more information.
    """

    END = 0
    """
    This tag is used to mark the end of a list. It doesn't carry any payload, and it cannot be named!

    If this type appears where a Named Tag is expected, the name is assumed to be ``""``.
    (In other words, this Tag is always just a single ``0x00`` byte when named, and nothing in all other cases)
    """

    BYTE = 1
    """A single signed byte (8 bits)."""

    SHORT = 2
    """A signed short (16 bits, big endian)."""

    INT = 3
    """A signed integer (32 bits, big endian)."""

    LONG = 4
    """A signed long (64 bits, big endian)."""

    FLOAT = 5
    """A floating point value (32 bits, big endian, IEEE 754-2008, binary32)."""

    DOUBLE = 6
    """A floating point value (64 bits, big endian, IEEE 754-2008, binary64)."""

    BYTE_ARRAY = 7
    """The payload is a TAG_Int representing the length, followed by an array of <length> bytes."""

    STRING = 8
    """
    The payload is a TAG_Short representing the length, followed by an array of <length> bytes,
    holding a string in UTF-8 format.
    """

    LIST = 9
    """
    The payload is a TAG_Byte representing the type of the items in the list,
    followed by a TAG_Int representing the length of the list,
    followed by an array of <length> NBTags.

    All the tags in the list must be of the same type.
    """

    COMPOUND = 10
    """
    A sequential list of Named Tags. This array keeps going until a TAG_End is found.

    * If there's a nested TAG_Compound within this tag, that one will also have a TAG_End,
      so simply reading until the next TAG_End will not work.
    * The names of the named tags have to be unique within each TAG_Compound.
    * The order of the tags is not guaranteed.
    """

    INT_ARRAY = 11
    """
    The payload is a TAG_Int representing the length, followed by an array of <length> TAG_Int elements.
    """

    LONG_ARRAY = 12
    """The payload is a TAG_Int representing the length, followed by an array of <length> TAG_Long elements."""


PayloadType: TypeAlias = Union[
    int,
    float,
    bytes,
    str,
    "NBTag",
    "Sequence[PayloadType]",
    "Mapping[str, PayloadType]",
]
"""Represents the type of a payload that can be stored in an NBT tag."""


@runtime_checkable
class NBTagConvertible(Protocol):
    """Protocol for objects that can be converted to an NBT tag."""

    __slots__ = ()

    def to_nbt(self, name: str = "") -> NBTag:
        """Convert the object to an NBT tag.

        :param name: The name of the tag.
        :return: The NBT tag created from the object.
        """
        raise NotImplementedError("Derived classes need to implement this method.")


FromObjectType: TypeAlias = Union[
    int,
    float,
    bytes,
    str,
    "NBTagConvertible",
    "Sequence[FromObjectType]",
    "Mapping[str, FromObjectType]",
]
"""Represents any object holding some data that can be converted to an NBT tag(s)."""

FromObjectSchema: TypeAlias = Union[
    "type[NBTag]",
    "type[NBTagConvertible]",
    "Sequence[FromObjectSchema]",
    "Mapping[str, FromObjectSchema]",
]
"""Represents the type of a schema, used to define how an object should be converted to an NBT tag(s)."""


class NBTag(MCType, NBTagConvertible, Hashable):
    """Base class for NBT tags.

    In MC v1.20.2+ the type and name of the root tag is not written to the buffer, and unless specified,
    the type of the tag is assumed to be TAG_Compound.
    """

    __slots__ = ("name", "payload")

    @override  # Add some extra kwargs to control serialization
    def serialize(self, with_type: bool = True, with_name: bool = True) -> Buffer:
        """Serialize the NBT tag to a new buffer.

        :param with_type:
            Whether to include the type of the tag in the serialization. (Passed to :meth:`_write_header`)
        :param with_name:
            Whether to include the name of the tag in the serialization. (Passed to :meth:`_write_header`)
        :return: The buffer containing the serialized NBT tag.

        .. note:: The ``with_type`` and ``with_name`` parameters only control the first level of serialization.
        """
        buf = Buffer()
        self.serialize_to(buf, with_name=with_name, with_type=with_type)
        return buf

    @override
    @classmethod
    def deserialize(cls, buf: Buffer, with_name: bool = True, with_type: bool = True) -> Self:
        """Deserialize the NBT tag.

        :param buf: The buffer to read from.
        :param with_name: Whether to read the name of the tag. (Passed to :meth:`_read_header`)
        :param with_type: Whether to read the type of the tag. (Passed to :meth:`_read_header`)
        :return:
            The deserialized NBT tag.

            This tag will be an instance of the class, that is associated with the tag type
            obtained from :meth:`_read_header` (see: :const:`ASSOCIATED_TYPES`).
        """
        name, tag_type = cls._read_header(buf, with_name=with_name, read_type=with_type)

        tag_class = ASSOCIATED_TYPES[tag_type]
        if cls not in (NBTag, tag_class):
            raise TypeError(f"Expected a {cls.__name__} tag, but found a different tag ({tag_class.__name__}).")

        tag = tag_class.read_from(buf, with_type=False, with_name=False)
        tag.name = name
        return tag  # type: ignore

    @override
    @abstractmethod
    def serialize_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        """Serialize the NBT tag to a buffer.

        :param buf: The buffer to write to.
        :param with_type: Whether to include the type of the tag in the serialization.
        :param with_name: Whether to include the name of the tag in the serialization.

        .. seealso:: :meth:`serialize`
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> NBTag:
        """Read the NBT tag from the buffer.

        Implementation shortcut used in :meth:`deserialize`. (Subclasses can override this, avoiding some
        repetition when compared to overriding ``deserialize`` directly.)
        """
        raise NotImplementedError

    def _write_header(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        """Write the header of the NBT tag to the buffer.

        :param buf: The buffer to write to.
        :param with_type: Whether to include the type of the tag in the serialization.
        :param with_name: Whether to include the name of the tag in the serialization.
        """
        if with_type:
            tag_type = _get_tag_type(self)
            buf.write_value(StructFormat.BYTE, tag_type.value)
        if with_name and self.name:
            StringNBT(self.name).serialize_to(buf, with_type=False, with_name=False)

    @classmethod
    def _read_header(cls, buf: Buffer, read_type: bool = True, with_name: bool = True) -> tuple[str, NBTagType]:
        """Read the header of the NBT tag.

        :param buf: The buffer to read from.
        :param read_type: Whether to read the type of the tag from the buffer.
            * If ``True``, the tag type will be read from the buffer
            * If ``False`` and called from a subclass, the tag type will be inferred from the subclass.
            * If ``False`` and called from the base class, the tag type will be TAG_Compound.
        :param with_name: Whether to read the name of the tag. If set to ``False``, the tag will have the name ``""``.

        :return: A tuple containing the name and the tag type.

        .. note::
            It is possible that this function reads nothing from the buffer if both ``with_name`` and
            ``read_type`` are set to ``False``.
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

    @staticmethod
    def from_object(data: FromObjectType, schema: FromObjectSchema, name: str = "") -> NBTag:
        """Create an NBT tag from a python object and a schema.

        :param data:
            The python object to create the NBT tag from.
        :param schema:
            The schema used to create the NBT tags.

            This is a description of the types of the ``data`` in the python object.
            It can be a subclass of :class:`NBTag` (e.g. :class:`IntNBT`, :class:`StringNBT`, :class:`CompoundNBT`,
            etc.), a :class:`dict`, a :class:`list`, a :class:`tuple`, or a class that has a `to_nbt` method.

            Example of schema:

            .. code-block:: python

                schema = {
                    "string": StringNBT,
                    "list_of_floats": [FloatNBT],
                    "list_of_compounds": [{
                        "key": StringNBT,
                        "value": IntNBT,
                    }],
                    "list_of_lists": [[IntNBT], [StringNBT]],
                }

            This would be translated into a :class:`CompoundNBT`.
        :param name: The name of the NBT tag.
        :return: The NBT tag created from the python object.
        """
        # Case 0 : schema is an object with a `to_nbt` method (could be a subclass of NBTag for all we know, as long
        # as the data is an instance of the schema it will work)
        if isinstance(schema, type) and hasattr(schema, "to_nbt") and isinstance(data, schema):
            return data.to_nbt(name=name)

        # Case 1 : schema is a NBTag subclass
        if isinstance(schema, type) and issubclass(schema, NBTag):
            if schema in (CompoundNBT, ListNBT):
                raise ValueError("Use a list or a dictionary in the schema to create a CompoundNBT or a ListNBT.")
            # Check if the data contains the name (if it is a dictionary)
            if isinstance(data, dict):
                data = cast("Mapping[str, FromObjectType]", data)
                if len(data) != 1:
                    raise ValueError("Expected a dictionary with a single key-value pair.")
                # We also check if the name isn't already set
                if name:
                    raise ValueError("The name is already set.")
                key, value = next(iter(data.items()))
                # Recursive call to go to the next part
                return NBTag.from_object(value, schema, name=key)
            # Else we check if the data can be a payload for the tag
            if not isinstance(data, (bytes, str, int, float, list)):
                raise TypeError(f"Expected one of (bytes, str, int, float, list), but found {type(data).__name__}.")
            # Check if the data is a list of integers
            if isinstance(data, list) and not all(isinstance(item, int) for item in data):
                raise TypeError("Expected a list of integers, but a non-integer element was found.")
            data = cast(Union[bytes, str, int, float, "list[int]"], data)
            # Create the tag with the data and the name
            return schema(data, name=name)  # type: ignore # The schema is a subclass of NBTag

        # Sanity check : Verify that all type schemas have been handled
        if not isinstance(schema, (list, tuple, dict)):
            raise TypeError(
                "The schema must be a list, dict, a subclass of NBTag or an object with a `to_nbt` method."
            )

        # Case 2 : schema is a dictionary
        payload: list[NBTag] = []
        if isinstance(schema, dict):
            # We can unpack the dictionary and create a CompoundNBT tag
            if not isinstance(data, dict):
                raise TypeError(f"Expected a dictionary, but found a different type ({type(data).__name__}).")

            # Iterate over the dictionary
            for key, value in data.items():
                # Recursive calls
                payload.append(NBTag.from_object(value, schema[key], name=key))
            # Finally we assign the payload and the name to the CompoundNBT tag
            return CompoundNBT(payload, name=name)

        # Case 3 : schema is a list or a tuple
        # We need to check if every element in the schema has the same type
        # but keep in mind that dict and list are also valid types, as long
        # as there are only dicts, or only lists in the schema
        if not isinstance(data, list):
            raise TypeError(f"Expected a list, but found {type(data).__name__}.")
        if len(schema) == 1:
            # We have two cases here, either the schema supports an unknown number of elements of a single type ...
            children_schema = schema[0]
            # No name in list items
            payload = [NBTag.from_object(item, children_schema) for item in data]
            return ListNBT(payload, name=name)

        # ... or the schema is a list of schemas
        # Check if the schema and the data have the same length
        if len(schema) != len(data):
            raise ValueError(f"The schema and the data must have the same length. ({len(schema)=} != {len(data)=})")
        if len(schema) == 0:
            return ListNBT([], name=name)

        # Check that the schema only has one type of elements
        first_schema = schema[0]
        # Dict/List case
        if isinstance(first_schema, (list, dict)) and not all(isinstance(item, type(first_schema)) for item in schema):
            raise TypeError(f"Expected a list of lists or dictionaries, but found a different type ({schema=}).")
        # NBTag case
        # Ignore branch coverage, `schema` will never be an empty list here
        if isinstance(first_schema, type) and not all(item == first_schema for item in schema):  # pragma: no branch
            raise TypeError(f"The schema must contain a single type of elements. ({schema=})")

        for item, sub_schema in zip(data, schema):
            payload.append(NBTag.from_object(item, sub_schema))
        return ListNBT(payload, name=name)

    def to_object(
        self,
        include_schema: bool = False,
        include_name: bool = False,
    ) -> PayloadType | Mapping[str, PayloadType] | tuple[PayloadType | Mapping[str, PayloadType], FromObjectSchema]:
        """Convert the NBT tag to a python object.

        :param include_schema: Whether to return a schema describing the types of the original tag.
        :param include_name: Whether to include the name of the tag in the output.
            If the tag has no name, the name will be set to "".

        :return:
            Either of:
                * A python object representing the payload of the tag. (default)
                * A dictionary containing the name associated with a python object representing the payload of the tag.
                * A tuple which includes one of the above and a schema describing the types of the original tag.
        """
        if type(self) is EndNBT:
            return NotImplemented
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
    def to_nbt(self, name: str = "") -> NBTag:
        """Convert the object to an NBT tag.

        .. warning:: This is already an NBT tag, so it will modify the name of the tag and return itself.
        """
        self.name = name
        return self

    @property
    @abstractmethod
    def value(self) -> PayloadType:
        """Get the payload of the NBT tag in a python-friendly format."""
        raise NotImplementedError

    @override
    def __hash__(self) -> int:
        return hash((self.name, self.payload, type(self)))

    @override
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, NBTag):
            return NotImplemented
        return (self.name, self.payload, type(self)) == (value.name, value.payload, type(value))


# endregion
# region NBT tags types


@final
@define(hash=False, eq=False)
class EndNBT(NBTag, Hashable):
    """Sentinel tag used to mark the end of a TAG_Compound."""

    payload: None = None
    name: str = ""

    @override
    def serialize_to(self, buf: Buffer, with_type: bool = True, with_name: bool = False) -> None:
        self._write_header(buf, with_type=with_type, with_name=False)

    @override
    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> EndNBT:
        _, tag_type = cls._read_header(buf, read_type=with_type, with_name=with_name)
        if _get_tag_type(cls) != tag_type:
            raise TypeError(f"Expected a {_get_tag_type(cls).name} tag, but found a different tag ({tag_type.name}).")
        return EndNBT()

    @override
    def to_object(
        self, include_schema: bool = False, include_name: bool = False
    ) -> PayloadType | Mapping[str, PayloadType]:
        return NotImplemented

    @property
    @override
    def value(self) -> PayloadType:
        return NotImplemented


@define(hash=False, eq=False)
class _NumberNBTag(NBTag, RequiredParamsABCMixin, Hashable):
    """Base class for NBT tags representing a number.

    This class is not meant to be used directly, but rather through its subclasses.
    """

    _REQUIRED_CLASS_VARS = ("STRUCT_FORMAT", "DATA_SIZE")

    STRUCT_FORMAT: ClassVar[INT_FORMATS_TYPE] = NotImplemented  # type: ignore
    DATA_SIZE: ClassVar[int] = NotImplemented

    payload: int
    name: str = ""

    @override
    def serialize_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        self._write_header(buf, with_type=with_type, with_name=with_name)
        buf.write_value(self.STRUCT_FORMAT, self.payload)

    @override
    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> Self:
        name, tag_type = cls._read_header(buf, read_type=with_type, with_name=with_name)
        if _get_tag_type(cls) != tag_type:
            raise TypeError(f"Expected a {_get_tag_type(cls).name} tag, but found a different tag ({tag_type.name}).")

        if buf.remaining < cls.DATA_SIZE:
            raise IOError(f"Buffer does not contain enough data to read a {tag_type.name}.")

        return cls(buf.read_value(cls.STRUCT_FORMAT), name=name)

    @override
    def validate(self) -> None:
        if not isinstance(self.payload, int):  # type: ignore
            raise TypeError(f"Expected an int, but found {type(self.payload).__name__}.")
        int_min = -(1 << (self.DATA_SIZE * 8 - 1))
        int_max = (1 << (self.DATA_SIZE * 8 - 1)) - 1
        if not int_min <= self.payload <= int_max:
            raise OverflowError(f"Value out of range for a {type(self).__name__} tag.")

    @property
    @override
    def value(self) -> int:
        return self.payload

    def __int__(self) -> int:
        return self.payload


@final
class ByteNBT(_NumberNBTag, Hashable):
    """NBT tag representing a single byte value, represented as a signed 8-bit integer."""

    STRUCT_FORMAT: ClassVar[INT_FORMATS_TYPE] = StructFormat.BYTE
    DATA_SIZE: ClassVar[int] = 1

    __slots__ = ()


@final
class ShortNBT(_NumberNBTag, Hashable):
    """NBT tag representing a short value, represented as a signed 16-bit integer."""

    STRUCT_FORMAT: ClassVar[INT_FORMATS_TYPE] = StructFormat.SHORT
    DATA_SIZE: ClassVar[int] = 2

    __slots__ = ()


@final
class IntNBT(_NumberNBTag, Hashable):
    """NBT tag representing an integer value, represented as a signed 32-bit integer."""

    STRUCT_FORMAT: ClassVar[INT_FORMATS_TYPE] = StructFormat.INT
    DATA_SIZE: ClassVar[int] = 4

    __slots__ = ()


@final
class LongNBT(_NumberNBTag, Hashable):
    """NBT tag representing a long value, represented as a signed 64-bit integer."""

    STRUCT_FORMAT: ClassVar[INT_FORMATS_TYPE] = StructFormat.LONGLONG
    DATA_SIZE: ClassVar[int] = 8

    __slots__ = ()


@define(hash=False, eq=False)
class _FloatingNBTag(NBTag, RequiredParamsABCMixin, Hashable):
    """Base class for NBT tags representing a floating-point number."""

    _REQUIRED_CLASS_VARS = ("STRUCT_FORMAT", "DATA_SIZE")

    STRUCT_FORMAT: ClassVar[FLOAT_FORMATS_TYPE] = NotImplemented  # type: ignore
    DATA_SIZE: ClassVar[int] = NotImplemented

    payload: float
    name: str = ""

    @override
    def __attrs_post_init__(self) -> None:
        if isinstance(self.payload, int):
            self.payload = float(self.payload)
        return super().__attrs_post_init__()

    @override
    def serialize_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        self._write_header(buf, with_type=with_type, with_name=with_name)
        buf.write_value(self.STRUCT_FORMAT, self.payload)

    @override
    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> Self:
        name, tag_type = cls._read_header(buf, read_type=with_type, with_name=with_name)
        if _get_tag_type(cls) != tag_type:
            raise TypeError(f"Expected a {_get_tag_type(cls).name} tag, but found a different tag ({tag_type.name}).")

        if buf.remaining < cls.DATA_SIZE:
            raise IOError(f"Buffer does not contain enough data to read a {tag_type.name}.")

        return cls(buf.read_value(cls.STRUCT_FORMAT), name=name)

    def __float__(self) -> float:
        return self.payload

    @property
    @override
    def value(self) -> float:
        return self.payload

    @override
    def validate(self) -> None:
        if not isinstance(self.payload, (int, float)):  # type: ignore # We want to check anyway
            raise TypeError(f"Expected a float, but found {type(self.payload).__name__}.")


@final
class FloatNBT(_FloatingNBTag):
    """NBT tag representing a floating-point value, represented as a 32-bit IEEE 754-2008 binary32 value."""

    STRUCT_FORMAT: ClassVar[FLOAT_FORMATS_TYPE] = StructFormat.FLOAT
    DATA_SIZE: ClassVar[int] = 4

    __slots__ = ()


@final
class DoubleNBT(_FloatingNBTag):
    """NBT tag representing a double-precision floating-point value, represented as a 64-bit IEEE 754-2008 binary64."""

    STRUCT_FORMAT: ClassVar[FLOAT_FORMATS_TYPE] = StructFormat.DOUBLE
    DATA_SIZE: ClassVar[int] = 8

    __slots__ = ()


@define(hash=False, eq=False)
class ByteArrayNBT(NBTag, Hashable):
    """NBT tag representing an array of bytes. The length of the array is stored as a signed 32-bit integer."""

    payload: bytes
    name: str = ""

    @override
    def __attrs_post_init__(self) -> None:
        if isinstance(self.payload, bytearray):
            self.payload = bytes(self.payload)
        return super().__attrs_post_init__()

    @override
    def serialize_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        self._write_header(buf, with_type=with_type, with_name=with_name)
        IntNBT(len(self.payload)).serialize_to(buf, with_type=False, with_name=False)
        buf.write(self.payload)

    @override
    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> ByteArrayNBT:
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
        if self.name:
            return f"{type(self).__name__}[{self.name!r}](length={len(self.payload)})"
        if len(self.payload) < 8:
            return f"{type(self).__name__}(length={len(self.payload)}, {self.payload!r})"
        return f"{type(self).__name__}(length={len(self.payload)}, {bytes(self.payload[:7])!r}...)"

    @property
    @override
    def value(self) -> bytes:
        return self.payload

    @override
    def validate(self) -> None:
        if not isinstance(self.payload, (bytearray, bytes)):
            raise TypeError(f"Expected a bytes, but found {type(self.payload).__name__}.")


@define(hash=False, eq=False)
class StringNBT(NBTag, Hashable):
    """NBT tag representing an UTF-8 string value. The length of the string is stored as a signed 16-bit integer."""

    payload: str
    name: str = ""

    @override
    def serialize_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        self._write_header(buf, with_type=with_type, with_name=with_name)
        if len(self.payload) > 32767:
            # Check the length of the string (can't generate strings that long in tests)
            raise ValueError("Maximum character limit for writing strings is 32767 characters.")  # pragma: no cover

        data = bytes(self.payload, "utf-8")
        ShortNBT(len(data)).serialize_to(buf, with_type=False, with_name=False)
        buf.write(data)

    @override
    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> StringNBT:
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
        return StringNBT(data.decode("utf-8"), name=name)

    @override
    def __str__(self) -> str:
        return self.payload

    @property
    @override
    def value(self) -> str:
        return self.payload

    @override
    def validate(self) -> None:
        if not isinstance(self.payload, str):  # type: ignore
            raise TypeError(f"Expected a str, but found {type(self.payload).__name__}.")
        if len(self.payload) > 32767:
            raise ValueError("Maximum character limit for writing strings is 32767 characters.")
        # Check that the string is valid UTF-8
        try:
            self.payload.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise ValueError("Invalid UTF-8 string.") from exc


@define(hash=False, eq=False)
class ListNBT(NBTag, Hashable):
    """NBT tag representing a list of tags. All tags in the list must be of the same type."""

    payload: list[NBTag]
    name: str = ""

    @override
    def serialize_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        self._write_header(buf, with_type=with_type, with_name=with_name)

        if not self.payload:
            # Set the tag type to TAG_End if the list is empty
            EndNBT().serialize_to(buf, with_name=False)
            IntNBT(0).serialize_to(buf, with_name=False, with_type=False)
            return

        tag_type = _get_tag_type(self.payload[0])
        ByteNBT(tag_type).serialize_to(buf, with_name=False, with_type=False)
        IntNBT(len(self.payload)).serialize_to(buf, with_name=False, with_type=False)
        for tag in self.payload:
            tag.serialize_to(buf, with_type=False, with_name=False)

    @override
    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> ListNBT:
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
        result = [tag.to_object() for tag in self.payload]
        result = cast("list[PayloadType]", result)
        result = result if not include_name else {self.name: result}
        if include_schema:
            subschemas = [
                cast("tuple[PayloadType, FromObjectSchema]", tag.to_object(include_schema=True))[1]
                for tag in self.payload
            ]
            if len(result) == 0:
                return result, []

            first = subschemas[0]
            if all(schema == first for schema in subschemas):
                return result, [first]

            # Useful tests but if they fail, this means `test_to_object_morecases` fails
            # because they can only be triggered by a malfunction of to_object in a child class
            # or the `validate` method
            if not isinstance(first, (dict, list)):  # pragma: no cover
                raise TypeError(f"The schema must contain either a dict or a list. Found {first!r}")
            first = cast("dict[str, PayloadType]|list[PayloadType]", first)
            # This will take care of ensuring either everything is a dict or a list
            if not all(isinstance(schema, type(first)) for schema in subschemas):  # pragma: no cover
                raise TypeError(f"All items in the list must have the same type. Found {subschemas!r}")
            return result, subschemas
        return result

    @property
    @override
    def value(self) -> list[PayloadType]:
        return [tag.value for tag in self.payload]

    @override
    def validate(self) -> None:
        if not isinstance(self.payload, list):  # type: ignore
            raise TypeError(f"Expected a list, but found {type(self.payload).__name__}.")
        if not all(isinstance(tag, NBTag) for tag in self.payload):  # type: ignore # We want to check anyway
            raise TypeError("All items in a list must be NBTags.")
        if not self.payload:
            return
        first_tag_type = type(self.payload[0])
        if not all(type(tag) is first_tag_type for tag in self.payload):
            raise TypeError("All tags in a list must be of the same type.")
        if not all(tag.name == "" for tag in self.payload):
            raise ValueError("All tags in a list must be unnamed.")


@define(hash=False, eq=False)
class CompoundNBT(NBTag, Hashable):
    """NBT tag representing a compound of named tags."""

    payload: list[NBTag]
    name: str = ""

    @override
    def serialize_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        self._write_header(buf, with_type=with_type, with_name=with_name)
        if not self.payload:
            EndNBT().serialize_to(buf, with_name=False, with_type=True)
            return

        for tag in self.payload:
            tag.serialize_to(buf)
        EndNBT().serialize_to(buf, with_name=False, with_type=True)

    @override
    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> CompoundNBT:
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
        result = {tag.name: tag.to_object() for tag in self.payload}
        result = cast("Mapping[str, PayloadType]", result)
        result = result if not include_name else {self.name: result}
        if include_schema:
            subschemas = {
                tag.name: cast(
                    "tuple[PayloadType, FromObjectSchema]",
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

        .. note:: The order of the tags is not guaranteed, but the names of the tags must match. This function assumes
            that there are no duplicate tags in the compound.
        """
        # The order of the tags is not guaranteed
        if not isinstance(other, NBTag):
            return NotImplemented
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
        return {tag.name: tag.value for tag in self.payload}

    @override
    def validate(self) -> None:
        if not isinstance(self.payload, list):  # type: ignore
            raise TypeError(f"Expected a list, but found {type(self.payload).__name__}.")
        if not all(isinstance(tag, NBTag) for tag in self.payload):  # type: ignore
            raise TypeError("All items in a compound must be NBTags.")
        if not all(tag.name for tag in self.payload):
            raise ValueError("All tags in a compound must be named.")
        if len(self.payload) != len({tag.name for tag in self.payload}):
            raise ValueError("All tags in a compound must have unique names.")

    @override
    def __hash__(self) -> int:
        return hash((self.name, frozenset(self.payload), type(self)))  # Use frozenset to ignore the order


@define(hash=False, eq=False)
class _NumberArrayNBTag(NBTag, RequiredParamsABCMixin, Hashable):
    """Base class for NBT tags representing an array of numbers."""

    _REQUIRED_CLASS_VARS = ("STRUCT_FORMAT", "DATA_SIZE")

    STRUCT_FORMAT: ClassVar[INT_FORMATS_TYPE] = NotImplemented  # type: ignore
    DATA_SIZE: ClassVar[int] = NotImplemented

    payload: list[int]
    name: str = ""

    @override
    def serialize_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        self._write_header(buf, with_type=with_type, with_name=with_name)
        IntNBT(len(self.payload)).serialize_to(buf, with_name=False, with_type=False)
        for i in self.payload:
            buf.write_value(self.STRUCT_FORMAT, i)

    @override
    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> Self:
        name, tag_type = cls._read_header(buf, read_type=with_type, with_name=with_name)
        if _get_tag_type(cls) != tag_type:
            raise TypeError(f"Expected a {_get_tag_type(cls).name} tag, but found a different tag ({tag_type.name}).")
        length = IntNBT.read_from(buf, with_type=False, with_name=False).value

        if buf.remaining < length * cls.DATA_SIZE:
            raise IOError(f"Buffer does not contain enough data to read the entire {tag_type.name}.")

        return cls([buf.read_value(cls.STRUCT_FORMAT) for _ in range(length)], name=name)

    @override
    def validate(self) -> None:
        if not isinstance(self.payload, list):  # type: ignore
            raise TypeError(f"Expected a list, but found {type(self.payload).__name__}.")
        if not all(isinstance(item, int) for item in self.payload):  # type: ignore
            raise TypeError("All items in an integer array must be integers.")
        if any(
            item < -(1 << (self.DATA_SIZE * 8 - 1)) or item >= 1 << (self.DATA_SIZE * 8 - 1) for item in self.payload
        ):
            raise OverflowError(f"Integer array contains values out of range. ({self.payload})")

    @property
    @override
    def value(self) -> list[int]:
        return self.payload

    def __iter__(self) -> Iterator[int]:
        yield from self.payload


@final
class IntArrayNBT(_NumberArrayNBTag):
    """NBT tag representing an array of integers. The length of the array is stored as a signed 32-bit integer."""

    STRUCT_FORMAT: ClassVar[INT_FORMATS_TYPE] = StructFormat.INT
    DATA_SIZE: ClassVar[int] = 4

    __slots__ = ()


@final
class LongArrayNBT(_NumberArrayNBTag):
    """NBT tag representing an array of longs. The length of the array is stored as a signed 32-bit integer."""

    STRUCT_FORMAT: ClassVar[INT_FORMATS_TYPE] = StructFormat.LONGLONG
    DATA_SIZE: ClassVar[int] = 8

    __slots__ = ()


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
    """Get the tag type of an NBTag object or class."""
    cls = tag if isinstance(tag, type) else type(tag)

    for tag_type, tag_cls in ASSOCIATED_TYPES.items():
        if cls is tag_cls:
            return tag_type

    raise ValueError(f"Unknown tag type {cls!r}.")  # pragma: no cover


# endregion
