from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import ClassVar, TYPE_CHECKING

from mcproto.buffer import Buffer

if TYPE_CHECKING:
    from typing_extensions import Self


class RequiredParamsABCMixin:
    """Mixin class to ABCs that require certain attributes to be set in order to allow initialization.

    This class performs a similar check to what ABCs already do for abstractmethods, but for class
    variables. The required class variable names are set with _REQUIRED_CLASS_VARS class variable,
    which itself is automatically required.

    Just like with ABCs, this doesn't prevent creation of classes without these required class vars
    missing, only initialization is prevented. This is done to allow creation of a more specific, but
    still abstract class.

    Additionally, you can also define _REQUIRED_CLASS_VARS_NO_MRO class var, holding names of class vars
    which should be defined on given class directly. That means inheritance will be ignored so even if a
    subclass defines the required class var, unless the latest class also defines it, this check will fail.

    This is often useful for classes that are expected to be slotted, as each subclass need to define
    __slots__, otherwise a __dict__ will automatically be made for it. However this is entirely optional,
    and if _REQUIRED_CLASS_VARS_NO_MRO isn't set, no such check will be performed.
    """

    _REQUIRRED_CLASS_VARS: ClassVar[Sequence[str]]
    _REQUIRED_CLASS_VARS_NO_MRO: ClassVar[Sequence[str]]

    def __new__(cls: type[Self], *a, **kw) -> Self:
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
                    emsg += f"({req_no_mro_attr} found in a subclass, but not explicitly in {cls.__name__})"
                raise TypeError(emsg)

        return super().__new__(cls)


class Serializable(ABC):
    """Base class for any type that should be (de)serializable into/from given buffer data."""

    @abstractmethod
    def serialize(self) -> Buffer:
        """Represent the object as a transmittable sequence of bytes."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        """Construct the object from it's received byte representation."""
        raise NotImplementedError
