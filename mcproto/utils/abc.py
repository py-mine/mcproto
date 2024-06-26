from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, ClassVar

from typing_extensions import Self

from mcproto.buffer import Buffer

__all__ = ["RequiredParamsABCMixin", "Serializable"]


class RequiredParamsABCMixin:
    """Mixin class to ABCs that require certain attributes to be set in order to allow initialization.

    This class performs a similar check to what :class:`~abc.ABC` already does with abstractmethods,
    but for class variables. The required class variable names are set with :attr:`._REQUIRED_CLASS_VARS`
    class variable, which itself is automatically required.

    Just like with ABCs, this doesn't prevent creation of classes without these required class vars
    defined, only initialization is prevented. This is done to allow creation of a more specific, but
    still abstract class.

    Additionally, you can also define :attr:`._REQUIRED_CLASS_VARS_NO_MRO` class var, holding names of
    class vars which should be defined on given class directly. That means inheritance will be ignored
    so even if a subclass defines the required class var, unless the latest class also defines it, this
    check will fail.

    This is often useful for classes that are expected to be slotted, as each subclass will need to define
    ``__slots__``, otherwise a ``__dict__`` will automatically be made for it. However this is entirely
    optional, and if :attr:`._REQUIRED_CLASS_VARS_NO_MRO` isn't set, this check is skipped.
    """

    __slots__ = ()

    _REQUIRED_CLASS_VARS: ClassVar[Sequence[str]]
    _REQUIRED_CLASS_VARS_NO_MRO: ClassVar[Sequence[str]]

    def __new__(cls: type[Self], *a: Any, **kw: Any) -> Self:
        """Enforce required parameters being set for each instance of the concrete classes."""
        _err_msg = f"Can't instantiate abstract {cls.__name__} class without defining " + "{!r} classvar"

        _required_class_vars = getattr(cls, "_REQUIRED_CLASS_VARS", None)
        if _required_class_vars is None:
            raise TypeError(_err_msg.format("_REQUIRED_CLASS_VARS"))

        for req_attr in _required_class_vars:
            if not hasattr(cls, req_attr):
                raise TypeError(_err_msg.format(req_attr))

        _required_class_vars_no_mro = getattr(cls, "_REQUIRED_CLASS_VARS_NO_MRO", None)
        if _required_class_vars_no_mro is None:
            return super().__new__(cls)

        for req_no_mro_attr in _required_class_vars_no_mro:
            if req_no_mro_attr not in vars(cls):
                emsg = _err_msg.format(req_no_mro_attr) + " explicitly"
                if hasattr(cls, req_no_mro_attr):
                    emsg += f" ({req_no_mro_attr} found in a subclass, but not explicitly in {cls.__name__})"
                raise TypeError(emsg)

        return super().__new__(cls)


class Serializable(ABC):
    """Base class for any type that should be (de)serializable into/from :class:`~mcproto.Buffer` data.

    Any class that inherits from this class and adds parameters should use the :func:`~mcproto.utils.abc.define`
    decorator.

    Example usage:

    .. literalinclude:: /../tests/mcproto/utils/test_serializable.py
        :start-after: # region ToyClass
        :end-before: # endregion
        :linenos:
        :language: python
    """

    __slots__ = ()

    def serialize(self) -> Buffer:
        """Represent the object as a :class:`~mcproto.Buffer` (transmittable sequence of bytes)."""
        buf = Buffer()
        self.serialize_to(buf)
        return buf

    @abstractmethod
    def serialize_to(self, buf: Buffer, /) -> None:
        """Write the object to a :class:`~mcproto.buffer.Buffer`."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        """Construct the object from a :class:`~mcproto.buffer.Buffer` (transmittable sequence of bytes)."""
        raise NotImplementedError
