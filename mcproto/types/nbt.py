from __future__ import annotations

from abc import abstractmethod
from enum import IntEnum
from typing import Union, cast, Protocol, runtime_checkable
from collections.abc import Iterator, Mapping, Sequence

from typing_extensions import TypeAlias, override

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

# region NBT Specification


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
    Sequence["PayloadType"],
    Mapping[str, "PayloadType"],
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
    NBTagConvertible,
    Sequence["FromObjectType"],
    Mapping[str, "FromObjectType"],
]
"""Represents any object holding some data that can be converted to an NBT tag(s)."""

FromObjectSchema: TypeAlias = Union[
    type["NBTag"],
    type[NBTagConvertible],
    Sequence["FromObjectSchema"],
    Mapping[str, "FromObjectSchema"],
]
"""Represents the type of a schema, used to define how an object should be converted to an NBT tag(s)."""


class NBTag(MCType, NBTagConvertible):
    """Base class for NBT tags.

    In MC v1.20.2+ the type and name of the root tag is not written to the buffer, and unless specified,
    the type of the tag is assumed to be TAG_Compound.
    """

    __slots__ = ("name", "payload")

    def __init__(self, payload: PayloadType, name: str = ""):
        self.name = name
        self.payload = payload

    @override
    def serialize(self, with_type: bool = True, with_name: bool = True) -> Buffer:
        """Serialize the NBT tag to a buffer.

        :param with_type:
            Whether to include the type of the tag in the serialization. (Passed to :meth:`_write_header`)
        :param with_name:
            Whether to include the name of the tag in the serialization. (Passed to :meth:`_write_header`)
        :return: The buffer containing the serialized NBT tag.

        .. note:: The ``with_type`` and ``with_name`` parameters only control the first level of serialization.
        """
        buf = Buffer()
        self.write_to(buf, with_name=with_name, with_type=with_type)
        return buf

    @override
    @classmethod
    def deserialize(cls, buf: Buffer, with_name: bool = True, with_type: bool = True) -> NBTag:
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
        return tag

    @abstractmethod
    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        """Write the NBT tag to the buffer.

        Implementation shortcut used in :meth:`serialize`. (Subclasses can override this, avoiding some
        repetition when compared to overriding ``serialize`` directly.)
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
            StringNBT(self.name).write_to(buf, with_type=False, with_name=False)

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
            return schema(data, name=name)

        # Sanity check : Verify that all type schemas have been handled
        if not isinstance(schema, (list, tuple, dict)):
            raise TypeError(
                "The schema must be a list, dict, a subclass of NBTag or an object with a `to_nbt` method."
            )

        # Case 2 : schema is a dictionary
        if isinstance(schema, dict):
            # We can unpack the dictionary and create a CompoundNBT tag
            if not isinstance(data, dict):
                raise TypeError(f"Expected a dictionary, but found {type(data).__name__}.")
            # Iterate over the dictionary
            payload: list[NBTag] = []
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
        payload: list[NBTag] = []
        if len(schema) == 1:
            # We have two cases here, either the schema supports an unknown number of elements of a single type ...
            children_schema = schema[0]
            for item in data:
                # No name in list items
                payload.append(NBTag.from_object(item, children_schema))
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
        if isinstance(first_schema, type) and not all(item == first_schema for item in schema):
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
    def __eq__(self, other: object) -> bool:
        """Check equality between two NBT tags."""
        if not isinstance(other, NBTag):
            return NotImplemented
        if type(self) is not type(other):
            return False
        return self.name == other.name and self.payload == other.payload

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


class ByteNBT(NBTag):
    """NBT tag representing a single byte value, represented as a signed 8-bit integer."""

    __slots__ = ()
    payload: int

    @override
    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        self._write_header(buf, with_type=with_type, with_name=with_name)
        if self.payload < -(1 << 7) or self.payload >= 1 << 7:
            raise OverflowError("Byte value out of range.")

        buf.write_value(StructFormat.BYTE, self.payload)

    @override
    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> ByteNBT:
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
        return self.payload


class ShortNBT(ByteNBT):
    """NBT tag representing a short value, represented as a signed 16-bit integer."""

    __slots__ = ()

    @override
    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        self._write_header(buf, with_type=with_type, with_name=with_name)

        if self.payload < -(1 << 15) or self.payload >= 1 << 15:
            raise OverflowError("Short value out of range.")

        buf.write_value(StructFormat.SHORT, self.payload)

    @override
    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> ShortNBT:
        name, tag_type = cls._read_header(buf, read_type=with_type, with_name=with_name)
        if _get_tag_type(cls) != tag_type:
            raise TypeError(f"Expected a {_get_tag_type(cls).name} tag, but found a different tag ({tag_type.name}).")

        if buf.remaining < 2:
            raise IOError("Buffer does not contain enough data to read a short.")

        return ShortNBT(buf.read_value(StructFormat.SHORT), name=name)


class IntNBT(ByteNBT):
    """NBT tag representing an integer value, represented as a signed 32-bit integer."""

    __slots__ = ()

    @override
    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        self._write_header(buf, with_type=with_type, with_name=with_name)

        if self.payload < -(1 << 31) or self.payload >= 1 << 31:
            raise OverflowError("Integer value out of range.")

        # No more messing around with the struct, we want 32 bits of data no matter what
        buf.write_value(StructFormat.INT, self.payload)

    @override
    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> IntNBT:
        name, tag_type = cls._read_header(buf, read_type=with_type, with_name=with_name)
        if _get_tag_type(cls) != tag_type:
            raise TypeError(f"Expected a {_get_tag_type(cls).name} tag, but found a different tag ({tag_type.name}).")

        if buf.remaining < 4:
            raise IOError("Buffer does not contain enough data to read an int.")

        return IntNBT(buf.read_value(StructFormat.INT), name=name)


class LongNBT(ByteNBT):
    """NBT tag representing a long value, represented as a signed 64-bit integer."""

    __slots__ = ()

    @override
    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        self._write_header(buf, with_type=with_type, with_name=with_name)

        if self.payload < -(1 << 63) or self.payload >= 1 << 63:
            raise OverflowError("Long value out of range.")

        # No more messing around with the struct, we want 64 bits of data no matter what
        buf.write_value(StructFormat.LONGLONG, self.payload)

    @override
    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> LongNBT:
        name, tag_type = cls._read_header(buf, read_type=with_type, with_name=with_name)
        if _get_tag_type(cls) != tag_type:
            raise TypeError(f"Expected a {_get_tag_type(cls).name} tag, but found a different tag ({tag_type.name}).")

        if buf.remaining < 8:
            raise IOError("Buffer does not contain enough data to read a long.")

        return LongNBT(buf.read_value(StructFormat.LONGLONG), name=name)


class FloatNBT(NBTag):
    """NBT tag representing a floating-point value, represented as a 32-bit IEEE 754-2008 binary32 value."""

    payload: float

    __slots__ = ()

    @override
    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        self._write_header(buf, with_type=with_type, with_name=with_name)
        buf.write_value(StructFormat.FLOAT, self.payload)

    @override
    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> FloatNBT:
        name, tag_type = cls._read_header(buf, read_type=with_type, with_name=with_name)
        if _get_tag_type(cls) != tag_type:
            raise TypeError(f"Expected a {_get_tag_type(cls).name} tag, but found a different tag ({tag_type.name}).")

        if buf.remaining < 4:
            raise IOError("Buffer does not contain enough data to read a float.")

        return FloatNBT(buf.read_value(StructFormat.FLOAT), name=name)

    def __float__(self) -> float:
        """Get the float value of the FloatNBT tag."""
        return self.payload

    @property
    @override
    def value(self) -> float:
        return self.payload


class DoubleNBT(FloatNBT):
    """NBT tag representing a double-precision floating-point value, represented as a 64-bit IEEE 754-2008 binary64."""

    __slots__ = ()

    @override
    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
        self._write_header(buf, with_type=with_type, with_name=with_name)
        buf.write_value(StructFormat.DOUBLE, self.payload)

    @override
    @classmethod
    def read_from(cls, buf: Buffer, with_type: bool = True, with_name: bool = True) -> DoubleNBT:
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
        self._write_header(buf, with_type=with_type, with_name=with_name)
        IntNBT(len(self.payload)).write_to(buf, with_type=False, with_name=False)
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


class StringNBT(NBTag):
    """NBT tag representing an UTF-8 string value. The length of the string is stored as a signed 16-bit integer."""

    __slots__ = ()

    payload: str

    @override
    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
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
        return self.payload

    @property
    @override
    def value(self) -> str:
        return self.payload


class ListNBT(NBTag):
    """NBT tag representing a list of tags. All tags in the list must be of the same type."""

    __slots__ = ()

    payload: list[NBTag]

    @override
    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
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
                cast(
                    "tuple[PayloadType, FromObjectSchema]",
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
        return [tag.value for tag in self.payload]


class CompoundNBT(NBTag):
    """NBT tag representing a compound of named tags."""

    __slots__ = ()

    payload: list[NBTag]

    @override
    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
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
        result = cast(Mapping[str, PayloadType], result)
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


class IntArrayNBT(NBTag):
    """NBT tag representing an array of integers. The length of the array is stored as a signed 32-bit integer."""

    __slots__ = ()

    payload: list[int]

    @override
    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
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
        return self.payload


class LongArrayNBT(IntArrayNBT):
    """NBT tag representing an array of longs. The length of the array is stored as a signed 32-bit integer."""

    __slots__ = ()

    @override
    def write_to(self, buf: Buffer, with_type: bool = True, with_name: bool = True) -> None:
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
    """Get the tag type of an NBTag object or class."""
    cls = tag if isinstance(tag, type) else type(tag)

    if cls is NBTag:
        return NBTagType.COMPOUND
    for tag_type, tag_cls in ASSOCIATED_TYPES.items():
        if cls is tag_cls:
            return tag_type

    raise ValueError(f"Unknown tag type {cls!r}.")  # pragma: no cover


# endregion
