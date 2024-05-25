from __future__ import annotations

import asyncio
import inspect
import unittest.mock
from collections.abc import Callable, Coroutine
from typing import Any, Generic, TypeVar
from typing_extensions import TypeGuard

import pytest
from typing_extensions import ParamSpec, override

from mcproto.buffer import Buffer
from mcproto.utils.abc import Serializable

T = TypeVar("T")
P = ParamSpec("P")
T_Mock = TypeVar("T_Mock", bound=unittest.mock.Mock)

__all__ = ["synchronize", "SynchronizedMixin", "UnpropagatingMockMixin", "CustomMockMixin", "gen_serializable_test"]


def synchronize(f: Callable[P, Coroutine[Any, Any, T]]) -> Callable[P, T]:
    """Take an asynchronous function, and return a synchronous alternative.

    This is needed because we sometimes want to test asynchronous behavior in a synchronous test function,
    where we can't simply await something. This function uses `asyncio.run` and generates a wrapper
    around the original asynchronous function, that awaits the result in a blocking synchronous way,
    returning the obtained value.
    """

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return asyncio.run(f(*args, **kwargs))

    return wrapper


class SynchronizedMixin:
    """Class acting as another wrapped object, with all async methods synchronized.

    This class needs :attr:`._WRAPPED_ATTRIBUTE` class variable to be set as the name of the internally
    held attribute, holding the object we'll be wrapping around.

    Child classes of this mixin will have their lookup logic changed, to instead perform a lookup
    on the wrapped attribute. Only if that lookup fails, we fallback to this class, meaning if both
    the wrapped attribute and this class have some attribute defined, the attribute from the wrapped
    object is returned. The only exceptions to this are lookup of the ``_WRAPPED_ATTRIBUTE`` variable,
    and of the attribute name stored under the ``_WRAPPED_ATTRIBUTE`` (the wrapped object).

    If the attribute held by the wrapped object is an asynchronous function, instead of returning it
    directly, the :func:`.synchronize` function will be called, returning a wrapped synchronous
    alternative for the requested async function.

    This is useful when we need to quickly create a synchronous alternative to a class holding async methods.
    However it isn't useful in production, since will cause typing issues (attributes will be accessible, but
    type checkers won't know that they exist here, because of the dynamic nature of this implementation).
    """

    _WRAPPED_ATTRIBUTE: str

    @override
    def __getattribute__(self, __name: str) -> Any:
        """Return attributes of the wrapped object, if the attribute is a coroutine function, synchronize it.

        The only exception to this behavior is getting the :attr:`._WRAPPED_ATTRIBUTE` variable itself, or the
        attribute named as the content of the ``_WRAPPED_ATTRIBUTE`` variable. All other attribute access will
        be delegated to the wrapped attribute. If the wrapped object doesn't have given attribute, the lookup
        will fallback to regular lookup for variables belonging to this class.
        """
        if __name == "_WRAPPED_ATTRIBUTE" or __name == self._WRAPPED_ATTRIBUTE:  # noqa: PLR1714 # Order is important
            return super().__getattribute__(__name)

        wrapped = getattr(self, self._WRAPPED_ATTRIBUTE)

        if hasattr(wrapped, __name):
            obj = getattr(wrapped, __name)
            if inspect.iscoroutinefunction(obj):
                return synchronize(obj)
            return obj

        return super().__getattribute__(__name)

    @override
    def __setattr__(self, __name: str, __value: object) -> None:
        """Allow for changing attributes of the wrapped object.

        * If wrapped object isn't yet set, fall back to :meth:`~object.__setattr__` of this class.
        * If wrapped object doesn't already contain the attribute we want to set, also fallback to this class.
        * Otherwise, run ``__setattr__`` on it to update it.
        """
        try:
            wrapped = getattr(self, self._WRAPPED_ATTRIBUTE)
        except AttributeError:
            return super().__setattr__(__name, __value)
        else:
            if hasattr(wrapped, __name):
                return setattr(wrapped, __name, __value)

        return super().__setattr__(__name, __value)


class UnpropagatingMockMixin(Generic[T_Mock]):
    """Provides common functionality for our :class:`~unittest.mock.Mock` classes.

    By default, mock objects propagate themselves by returning a new instance of the same mock
    class, with same initialization attributes. This is done whenever we're accessing new
    attributes that mock class.

    This propagation makes sense for simple mocks without any additional restrictions, however when
    dealing with limited mocks to some ``spec_set``, it doesn't usually make sense to propagate
    those same ``spec_set`` restrictions, since we generally don't have attributes/methods of a
    class be of/return the same class.

    This mixin class stops this propagation, and instead returns instances of specified mock class,
    defined in :attr:`.child_mock_type` class variable, which is by default set to
    :class:`~unittest.mock.MagicMock`, as it can safely represent most objects.

    .. note:
        This propagation handling will only be done for the mock classes that inherited from this
        mixin class. That means if the :attr:`.child_mock_type` is one of the regular mock classes,
        and the mock is propagated, a regular mock class is returned as that new attribute. This
        regular class then won't have the same overrides, and will therefore propagate itself, like
        any other mock class would.

        If you wish to counteract this, you can set the :attr:`.child_mock_type` to a mock class
        that also inherits from this mixin class, perhaps to your class itself, overriding any
        propagation recursively.
    """

    child_mock_type: T_Mock = unittest.mock.MagicMock

    # Since this is a mixin class, we can access some attributes defined in mock classes safely.
    # Define the types of these variables here, for proper static type analysis.
    _mock_sealed: bool
    _extract_mock_name: Callable[[], str]

    def _get_child_mock(self, **kwargs) -> T_Mock:
        """Make :attr:`.child_mock_type`` instances instead of instances of the same class.

        By default, this method creates a new mock instance of the same original class, and passes
        over the same initialization arguments. This overrides that behavior to instead create an
        instance of :attr:`.child_mock_type` class.
        """
        # Mocks can be sealed, in which case we wouldn't want to allow propagation of any kind
        # and rather raise an AttributeError, informing that given attr isn't accessible
        if self._mock_sealed:
            mock_name = self._extract_mock_name()
            obj_name = f"{mock_name}.{kwargs['name']}" if "name" in kwargs else f"{mock_name}()"
            raise AttributeError(f"Can't access {obj_name}, mock is sealed.")

        # Propagate any other children as simple `unittest.mock.Mock` instances
        # rather than `self.__class__` instances
        return self.child_mock_type(**kwargs)


class CustomMockMixin(UnpropagatingMockMixin):
    """Provides common functionality for our custom mock types.

    * Stops propagation of same ``spec_set`` restricted mock in child mocks
      (see :class:`.UnpropagatingMockMixin` for more info)
    * Allows using the ``spec_set`` attribute as class attribute
    """

    spec_set = None

    def __init__(self, **kwargs):
        if "spec_set" in kwargs:
            self.spec_set = kwargs.pop("spec_set")
        super().__init__(spec_set=self.spec_set, **kwargs)  # type: ignore # Mixin class, this __init__ is valid


def isexception(obj: object) -> TypeGuard[type[Exception] | Exception]:
    """Check if the object is an exception."""
    return (isinstance(obj, type) and issubclass(obj, Exception)) or isinstance(obj, Exception)


def get_exception(exception: type[Exception] | Exception) -> tuple[type[Exception], str | None]:
    """Get the exception type and message."""
    if isinstance(exception, type):
        return exception, None
    return type(exception), str(exception)


def gen_serializable_test(
    context: dict[str, Any],
    cls: type[Serializable],
    fields: list[tuple[str, type | str]],
    test_data: list[
        tuple[tuple[Any, ...], bytes]
        | tuple[tuple[Any, ...], type[Exception] | Exception]
        | tuple[type[Exception] | Exception, bytes]
    ],
):
    """Generate tests for a serializable class.

    This function generates tests for the serialization, deserialization, validation, and deserialization error
    handling

    :param context: The context to add the test functions to. This is usually `globals()`.
    :param cls: The serializable class to test.
    :param fields: A list of tuples containing the field names and types of the serializable class.
    :param test_data: A list of test data. Each element is a tuple containing either:
        - A tuple of parameters to pass to the serializable class constructor and the expected bytes after
        serialization
        - A tuple of parameters to pass to the serializable class constructor and the expected exception during
        validation
        - An exception to expect during deserialization and the bytes to deserialize

        Exception can be either a type or an instance of an exception, in the latter case the exception message will
        be used to match the exception, and can contain regex patterns.

    Example usage:

    .. literalinclude:: /../tests/mcproto/utils/test_serializable.py
        :start-after: # region ToyClass
        :linenos:
        :language: python

    This will add 1 class test with 4 test functions containing the tests for serialization, deserialization,
    validation, and deserialization error handling

    .. note::
        The test cases will use :meth:`__eq__` to compare the objects, so make sure to implement it in the class if
        you are not using a dataclass.

    """
    # Separate the test data into parameters for each test function
    # This holds the parameters for the serialization and deserialization tests
    parameters: list[tuple[dict[str, Any], bytes]] = []

    # This holds the parameters for the validation tests
    validation_fail: list[tuple[dict[str, Any], type[Exception] | Exception]] = []

    # This holds the parameters for the deserialization error tests
    deserialization_fail: list[tuple[bytes, type[Exception] | Exception]] = []

    for data_or_exc, expected_bytes_or_exc in test_data:
        if isinstance(data_or_exc, tuple) and isinstance(expected_bytes_or_exc, bytes):
            kwargs = dict(zip([f[0] for f in fields], data_or_exc))
            parameters.append((kwargs, expected_bytes_or_exc))
        elif isexception(data_or_exc) and isinstance(expected_bytes_or_exc, bytes):
            deserialization_fail.append((expected_bytes_or_exc, data_or_exc))
        elif isinstance(data_or_exc, tuple) and isexception(expected_bytes_or_exc):
            kwargs = dict(zip([f[0] for f in fields], data_or_exc))
            validation_fail.append((kwargs, expected_bytes_or_exc))

    def generate_name(param: dict[str, Any] | bytes, i: int) -> str:
        """Generate a name for the test case."""
        length = 30
        result = f"{i:02d}] : "  # the first [ is added by pytest
        if isinstance(param, bytes):
            result += repr(param[:length]) + "..." if len(param) > (length + 3) else repr(param)
        elif isinstance(param, dict):
            begin = ", ".join(f"{k}={v!r}" for k, v in param.items())
            result += begin[:length] + "..." if len(begin) > (length + 3) else begin
        else:
            raise TypeError(f"Wrong type for param : {param!r}")
        result = result.replace("\n", "\\n").replace("\r", "\\r")
        result += f" [{cls.__name__}"  # the other [ is added by pytest
        return result

    class TestClass:
        """Test class for the generated tests."""

        @pytest.mark.parametrize(
            ("kwargs", "expected_bytes"),
            parameters,
            ids=tuple(generate_name(kwargs, i) for i, (kwargs, _) in enumerate(parameters)),
        )
        def test_serialization(self, kwargs: dict[str, Any], expected_bytes: bytes):
            """Test serialization of the object."""
            obj = cls(**kwargs)
            serialized_bytes = bytes(obj.serialize())
            assert serialized_bytes == expected_bytes, f"{serialized_bytes} != {expected_bytes}"

        @pytest.mark.parametrize(
            ("kwargs", "expected_bytes"),
            parameters,
            ids=tuple(generate_name(kwargs, i) for i, (kwargs, _) in enumerate(parameters)),
        )
        def test_deserialization(self, kwargs: dict[str, Any], expected_bytes: bytes):
            """Test deserialization of the object."""
            buf = Buffer(expected_bytes)
            obj = cls.deserialize(buf)
            equality = cls(**kwargs) == obj
            error_message: list[str] = []
            # Try to find the mismatched field
            if not equality:
                for field, value in kwargs.items():
                    obj_val = getattr(obj, field, None)
                    if obj_val is None:  # Either skip it, or it is intended to be None
                        continue
                    if obj_val != value:
                        error_message.append(f"{field}={obj_val} != {value}")
                        break
            if error_message:
                assert equality, f"Object not equal: {', '.join(error_message)}"
            else:
                assert equality, f"Object not equal: {obj} != {cls(**kwargs)} (expected)"
            assert buf.remaining == 0, f"Buffer has {buf.remaining} bytes remaining"

        @pytest.mark.parametrize(
            ("kwargs", "exc"),
            validation_fail,
            ids=tuple(generate_name(kwargs, i) for i, (kwargs, _) in enumerate(validation_fail)),
        )
        def test_validation(self, kwargs: dict[str, Any], exc: type[Exception] | Exception):
            """Test validation of the object."""
            exc, msg = get_exception(exc)
            with pytest.raises(exc, match=msg):
                cls(**kwargs)

        @pytest.mark.parametrize(
            ("content", "exc"),
            deserialization_fail,
            ids=tuple(generate_name(content, i) for i, (content, _) in enumerate(deserialization_fail)),
        )
        def test_deserialization_error(self, content: bytes, exc: type[Exception] | Exception):
            """Test deserialization error handling."""
            buf = Buffer(content)
            exc, msg = get_exception(exc)
            with pytest.raises(exc, match=msg):
                cls.deserialize(buf)

    if len(parameters) == 0:
        # If there are no serialization tests, remove them
        del TestClass.test_serialization
        del TestClass.test_deserialization

    if len(validation_fail) == 0:
        # If there are no validation tests, remove them
        del TestClass.test_validation

    if len(deserialization_fail) == 0:
        # If there are no deserialization error tests, remove them
        del TestClass.test_deserialization_error

    # Set the names of the class
    TestClass.__name__ = f"TestGen{cls.__name__}"

    # Add the test functions to the global context
    context[TestClass.__name__] = TestClass  # BERK
