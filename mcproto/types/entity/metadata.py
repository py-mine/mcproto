from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Any, ClassVar, Literal, TypeVar, cast, final, overload


from typing_extensions import override, dataclass_transform

from mcproto.buffer import Buffer
from mcproto.protocol import StructFormat
from mcproto.types.abc import MCType


"""
    BYTE = 0
    VARINT = 1
    VARLONG = 2
    FLOAT = 3
    STRING = 4
    TEXT_COMPONENT = 5
    OPT_TEXT_COMPONENT = 6
    SLOT = 7
    BOOLEAN = 8
    ROTATION = 9
    POSITION = 10
    OPT_POSITION = 11
    DIRECTION = 12
    OPT_UUID = 13
    BLOCK_STATE = 14
    NBT = 15
    PARTICLE = 16
    VILLAGER_DATA = 17
    OPT_VARINT = 18
    POSE = 19
    CAT_VARIANT = 20
    FROG_VARIANT = 21
    OPT_GLOBAL_POS = 22
    PAINTING_VARIANT = 23
    SNIFFER_STATE = 24
    VECTOR3 = 25
    QUATERNION = 26
"""


class EntityMetadataEntry(MCType):
    """Represents an entry in an entity metadata list.

    :param index: The index of the entry.
    :param entry_type: The type of the entry.
    :param value: The value of the entry.
    :param default: The default value of the entry.
    :param hidden: Whether the entry is hidden from the metadata list.
    :param name: The name of the entry. This is used for debugging purposes and not always set. DO NOT RELY ON THIS
    """

    ENTRY_TYPE: ClassVar[int] = None  # type: ignore

    index: int
    value: Any

    __slots__ = ("index", "value", "hidden", "default", "name")

    def __init__(
        self, index: int, value: Any = None, default: Any = None, hidden: bool = False, name: str | None = None
    ):
        self.index = index
        self.value = default if value is None else value
        self.hidden = hidden
        self.default = default
        self.name = name  # for debugging purposes

        self.validate()

    def setter(self, value: Any) -> None:
        """Set the value of the entry."""
        self.value = value

    def getter(self) -> Any:
        """Get the value of the entry."""
        return self.value

    def _write_header(self, buf: Buffer) -> None:
        """Write the index and type of the entry.

        :param buf: The buffer to write to.
        """
        buf.write_value(StructFormat.UBYTE, self.index)
        buf.write_varint(self.ENTRY_TYPE)

    @overload
    @classmethod
    def read_header(cls, buf: Buffer, return_type: Literal[True]) -> tuple[int, int]: ...

    @overload
    @classmethod
    def read_header(cls, buf: Buffer, return_type: Literal[False] = False) -> int: ...

    @classmethod
    def read_header(cls, buf: Buffer, return_type: bool = False) -> tuple[int, int] | int:
        """Read the index and type of the entry, and optionally return the type.

        :param buf: The buffer to read from.
        :param return_type: Whether to return the type of the entry. If this is set to false, the type will be read but
            not returned.
        :return: The index of the entry.

        :raises ValueError: If return_type is False and the entity type does not match the expected type.
        """
        index = buf.read_value(StructFormat.UBYTE)
        if index == 0xFF:
            if return_type:
                return index, -1
            raise ValueError("Index 0xFF is reserved for the end of the metadata list.")

        entry_type = buf.read_varint()
        if entry_type != cls.ENTRY_TYPE and not return_type:
            raise TypeError(f"Expected entry type {cls.ENTRY_TYPE}, got {entry_type}.")
        if return_type:
            return index, entry_type
        return index

    @override
    def validate(self) -> None:
        if self.index < 0 or self.index > 0xFF:
            raise ValueError("Index must be between 0 and 0xFF.")

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(index={self.index}, value={self.value})"

    @override
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, EntityMetadataEntry):
            return NotImplemented
        return self.index == value.index and self.value == value.value

    @classmethod
    @abstractmethod
    def read_value(cls, buf: Buffer) -> Any:
        """Read the value of the entry from the buffer.

        :param buf: The buffer to read from.
        :return: The value of the entry.
        """
        ...

    @override
    @classmethod
    @final
    def deserialize(cls, buf: Buffer) -> EntityMetadataEntry:
        """Deserialize the entity metadata entry.

        :param buf: The buffer to read from.
        :return: The entity metadata entry.
        """
        index = cls.read_header(buf)
        value = cls.read_value(buf)
        return cls(index=index, value=value)


class ProxyEntityMetadataEntry(MCType):
    """A proxy entity metadata entry which is used to designate a part of a metadata entry in a human-readable format.

    For example, this can be used to represent a certain mask for a ByteEME entry.
    """

    ENTRY_TYPE: ClassVar[int] = None  # type: ignore

    bound_entry: EntityMetadataEntry

    __slots__ = ("bound_entry",)

    def __init__(self, bound_entry: EntityMetadataEntry, *args: Any, **kwargs: Any):
        self.bound_entry = bound_entry
        self.validate()

    @override
    def serialize_to(self, buf: Buffer) -> None:
        raise NotImplementedError("Proxy entity metadata entries cannot be serialized.")

    @override
    @classmethod
    def deserialize(cls, buf: Buffer) -> ProxyEntityMetadataEntry:
        raise NotImplementedError("Proxy entity metadata entries cannot be deserialized.")

    @abstractmethod
    def setter(self, value: Any) -> None:
        """Set the value of the entry by modifying the bound entry."""
        ...

    @abstractmethod
    def getter(self) -> Any:
        """Get the value of the entry by reading the bound entry."""
        ...


EntityDefault = TypeVar("EntityDefault")


class _DefaultEntityMetadataEntry:
    m_default: Any
    m_type: type[EntityMetadataEntry]
    m_index: int

    __slots__ = ("m_default", "m_type")


def entry(entry_type: type[EntityMetadataEntry], value: EntityDefault) -> EntityDefault:
    """Create a entity metadata entry with the given value.

    :param entry_type: The type of the entry.
    :param default: The default value of the entry.
    :return: The default entity metadata entry.
    """

    class DefaultEntityMetadataEntry(_DefaultEntityMetadataEntry):
        m_default = value
        m_type = entry_type
        m_index = -1

        __slots__ = ()

    # This will be taken care of by EntityMetadata
    return DefaultEntityMetadataEntry  # type: ignore


ProxyInitializer = TypeVar("ProxyInitializer")


class _ProxyEntityMetadataEntry:
    """Class used to pass the bound entry and additional arguments to the proxy entity metadata entry.

    Explanation:
    m_bound_entry: The real entry that the proxy will modify.
    m_args: Additional arguments for the proxy entity metadata entry.
    m_kwargs: Additional keyword arguments for the proxy entity metadata entry.
    m_type: The type of the proxy entity metadata entry, this defines how the proxy will modify the real entry.
     All of the above are set by the proxy() function.

    m_bound_index: The index of the bound entry in the metadata list.
     This is set by the EntityMetadataCreator.
    """

    m_bound_entry: EntityMetadataEntry
    m_args: tuple[Any]
    m_kwargs: dict[str, Any]
    m_type: type[ProxyEntityMetadataEntry]
    m_bound_index: int

    __slots__ = ("m_bound_entry", "m_args", "m_kwargs", "m_type", "m_bound_index")


def proxy(
    bound_entry: EntityDefault,  # type: ignore # Used only once but I prefer to keep the type hint
    proxy: type[ProxyEntityMetadataEntry],
    *args: Any,
    **kwargs: Any,
) -> ProxyInitializer:  # type: ignore
    """Initialize the proxy entity metadata entry with the given bound entry and additional arguments.

    :param bound_entry: The bound entry.
    :param proxy: The proxy entity metadata entry type.
    :param args: Additional arguments for the proxy entity metadata entry.
    :param kwargs: Additional keyword arguments for the proxy entity metadata entry.

    :return: The proxy entity metadata entry initializer.
    """
    if not isinstance(bound_entry, type):
        raise TypeError("The bound entry must be an entity metadata entry type.")
    if not issubclass(bound_entry, _DefaultEntityMetadataEntry):
        raise TypeError("The bound entry must be an entity metadata entry.")

    class ProxyEntityMetadataEntry(_ProxyEntityMetadataEntry):
        m_bound_entry = bound_entry  # type: ignore # This will be taken care of by EntityMetadata
        m_args = args
        m_kwargs = kwargs
        m_type = proxy

        m_bound_index = -1

        __slots__ = ()

    return ProxyEntityMetadataEntry  # type: ignore


@dataclass_transform(kw_only_default=True)  # field_specifiers=(entry, proxy))
class EntityMetadataCreator(ABCMeta):
    """Metaclass for the EntityMetadata.

    This metaclass is used to create the EntityMetadata with the correct attributes to allow for using them
    like dataclasses.

    The entry() and proxy() functions are used to set the attributes of the entity class.
    ```
    """

    m_defaults: ClassVar[dict[str, type[_DefaultEntityMetadataEntry | _ProxyEntityMetadataEntry]]]
    m_index: ClassVar[dict[int, str]]
    m_metadata: ClassVar[
        dict[str, EntityMetadataEntry | ProxyEntityMetadataEntry]
    ]  # This is not an actual classvar, but I
    # Do not want it to appear in the __init__ signature

    def __new__(cls, name: str, bases: tuple[type], namespace: dict[str, Any]) -> EntityMetadata:
        """Create a new EntityMetadata."""
        new_cls = super().__new__(cls, name, bases, namespace)
        cls.setup_class(new_cls)
        return cast("EntityMetadata", new_cls)

    def setup_class(cls: type[EntityMetadata]) -> None:
        """Set up the class for the entity metadata.

        This function will create a few class attributes :
        - m_defaults: A dictionary that maps the names of the entries to their "setup class" (the return of entry()
        or proxy())
        - m_index: A mapping of the names of the entity metadata entries to their index

        The m_metadata is mentioned here but nothing is created yet. __init__ will take care of this.

        """
        cls.m_defaults = {}
        cls.m_index = {}

        bound_index: dict[int, int] = {}
        current_index = 0
        # Find all the entries in the class

        attributes: list[str] = []
        for parent in reversed(cls.mro()):
            for name in vars(parent):
                if name in attributes:
                    continue
                attributes.append(name)

        for name in attributes:
            # Default is assigned in the class definition
            default = getattr(cls, name, None)
            if default is None:
                raise ValueError(f"Default value for {name} is not set. Use the entry() or proxy() functions.")
            # Check if we have a default entry
            if isinstance(default, type) and issubclass(default, _DefaultEntityMetadataEntry):
                # Set the index of the entry
                default.m_index = current_index

                # Add the index to the index mapping
                cls.m_index[current_index] = name

                # Add the entry to the bound_index mapping to be used by the proxy entries
                bound_index[id(default)] = current_index

                # Increment the index
                current_index += 1
            elif isinstance(default, type) and issubclass(default, _ProxyEntityMetadataEntry):
                # Find the bound entry
                if id(default.m_bound_entry) not in bound_index:
                    raise ValueError(f"Bound entry for {name} is not set.")
                bound_entry = bound_index[id(default.m_bound_entry)]

                # Set the index of the proxy entry
                default.m_bound_index = bound_entry
            else:
                continue
            # Add the entry to the defaults
            cls.m_defaults[name] = default


class EntityMetadata(MCType, metaclass=EntityMetadataCreator):
    """Base for all Entity classes.

    All the entity classes are subclasses of this class.

    You can set attributes of the entity class by using the entry() and proxy() functions.

    Example:

    .. code-block:: python

        class EntityMetadata(EntityMetadata):
            byte_entry: ClassVar[int] = entry(ByteEME, 0) # ByteEME is the type and 0 is the default value
            varint_entry: int = entry(VarIntEME, 0)
            proxy_entry: int = proxy(byte_entry, Masked, mask=0x01)
            proxy_entry2: int = proxy(byte_entry, Masked, mask=0x02)


    Note that the extra arguments for the proxy() function are passed to the proxy class and that the
    bound entry is passed as the first argument without quotes.
    """

    __slots__ = ("m_metadata",)

    def __init__(self, *args: None, **kwargs: Any) -> None:
        if len(args) > 0:
            raise ValueError(
                "EntityMetadata does not accept positional arguments. Specify all metadata entries by name."
            )
        self.m_metadata: dict[str, EntityMetadataEntry | ProxyEntityMetadataEntry] = {}
        for name, default in self.m_defaults.items():
            if issubclass(default, _DefaultEntityMetadataEntry):
                self.m_metadata[name] = default.m_type(index=default.m_index, default=default.m_default, name=name)
            elif issubclass(default, _ProxyEntityMetadataEntry):  # type: ignore # We want to check anyways
                # Bound entry
                bound_name = self.m_index[default.m_bound_index]
                bound_entry = cast(EntityMetadataEntry, self.m_metadata[bound_name])
                self.m_metadata[name] = default.m_type(bound_entry, *default.m_args, **default.m_kwargs)
            else:  # pragma: no cover
                raise ValueError(f"Invalid default value for {name}. Use the entry() or proxy() functions.")  # noqa: TRY004

        for name, value in kwargs.items():
            if name not in self.m_metadata:
                raise ValueError(f"Unknown metadata entry {name}.")
            self.m_metadata[name].setter(value)

    @override
    def __setattr__(self, name: str, value: Any) -> None:
        if name != "m_metadata" and hasattr(self, "m_metadata") and name in self.m_metadata:
            self.m_metadata[name].setter(value)
        else:
            super().__setattr__(name, value)

    @override
    def __getattribute__(self, name: str) -> Any:
        if name != "m_metadata" and hasattr(self, "m_metadata") and name in self.m_metadata:
            return self.m_metadata[name].getter()
        return super().__getattribute__(name)

    @override
    def __repr__(self) -> str:
        # Iterate over m_metadata to get the string representation of the metadata
        metadata: list[str] = []
        for name, entry in self.m_metadata.items():
            metadata.append(f"{name}={entry.getter()}")
        return f"{self.__class__.__name__}({', '.join(metadata)})"

    @override
    def serialize_to(self, buf: Buffer) -> None:
        for entry in self.m_metadata.values():
            # Check if the value is a proxy entry
            if isinstance(entry, ProxyEntityMetadataEntry):
                continue
            # Check if the value differs from the default value
            if entry.value != entry.default:
                entry.serialize_to(buf)
        # Mark the end of the metadata list
        buf.write_value(StructFormat.UBYTE, 0xFF)

    @override
    @classmethod
    def deserialize(cls, buf: Buffer) -> EntityMetadata:
        from mcproto.types.entity.metadata_types import ASSOCIATIONS

        entries: list[tuple[int, Any]] = []

        while True:
            index, entry_type_index = EntityMetadataEntry.read_header(buf, return_type=True)
            if index == 0xFF:
                break
            if entry_type_index not in ASSOCIATIONS:
                raise TypeError(f"Unknown entry type {entry_type_index}.")
            entry_type = ASSOCIATIONS[entry_type_index]

            entry = entry_type.read_value(buf)
            entries.append((index, entry))

        new_instance = cls()  # Initialize the new instance with the default values
        for index, value in entries:
            new_instance.m_metadata[cls.m_index[index]].setter(value)
        return new_instance
