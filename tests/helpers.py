from __future__ import annotations

import asyncio
import inspect
import re
import unittest.mock
from collections.abc import Callable, Coroutine
from typing import Any, ClassVar, Generic, NamedTuple, TypeVar

import pytest
from typing_extensions import ParamSpec, TypeIs, override

from mcproto.buffer import Buffer
from mcproto.utils.abc import Serializable

T = TypeVar("T")
P = ParamSpec("P")
T_Mock = TypeVar("T_Mock", bound=unittest.mock.Mock)

__all__ = [
    "CustomMockMixin",
    "SynchronizedMixin",
    "TestExc",
    "UnpropagatingMockMixin",
    "gen_serializable_test",
    "synchronize",
]


def synchronize(f: Callable[P, Coroutine[Any, Any, T]]) -> Callable[P, T]:
    """Take an asynchronous function, and return a synchronous alternative.

    This is needed because we sometimes want to test asynchronous behavior in a synchronous test function,
    where we can't simply await something. This function uses [`asyncio.run`][asyncio.run] and generates a
    wrapper around the original asynchronous function, that awaits the result in a blocking synchronous way,
    returning the obtained value.
    """

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return asyncio.run(f(*args, **kwargs))

    return wrapper


class SynchronizedMixin:
    """Class acting as another wrapped object, with all async methods synchronized.

    This class needs [`_WRAPPED_ATTRIBUTE`][.] class variable to be set as the name of the internally
    held attribute, holding the object we'll be wrapping around.

    Child classes of this mixin will have their lookup logic changed, to instead perform a lookup
    on the wrapped attribute. Only if that lookup fails, we fallback to this class, meaning if both
    the wrapped attribute and this class have some attribute defined, the attribute from the wrapped
    object is returned. The only exceptions to this are lookup of the `_WRAPPED_ATTRIBUTE` variable,
    and of the attribute name stored under the `_WRAPPED_ATTRIBUTE` (the wrapped object).

    If the attribute held by the wrapped object is an asynchronous function, instead of returning it
    directly, the [`synchronize`][(m).] function will be called, returning a wrapped synchronous alternative
    for the requested async function.

    This is useful when we need to quickly create a synchronous alternative to a class holding async methods.
    However it isn't useful in production, since will cause typing issues (attributes will be accessible, but
    type checkers won't know that they exist here, because of the dynamic nature of this implementation).
    """

    _WRAPPED_ATTRIBUTE: ClassVar[str]

    @override
    def __getattribute__(self, /, name: str) -> Any:
        """Return attributes of the wrapped object, if the attribute is a coroutine function, synchronize it.

        The only exception to this behavior is getting the [`_WRAPPED_ATTRIBUTE`][..] variable itself, or the
        attribute named as the content of the `_WRAPPED_ATTRIBUTE` variable. All other attribute access will
        be delegated to the wrapped attribute. If the wrapped object doesn't have given attribute, the lookup
        will fallback to regular lookup for variables belonging to this class.
        """
        if name == "_WRAPPED_ATTRIBUTE" or name == self._WRAPPED_ATTRIBUTE:  # noqa: PLR1714 # Order is important
            return super().__getattribute__(name)

        wrapped = getattr(self, self._WRAPPED_ATTRIBUTE)

        if hasattr(wrapped, name):
            obj = getattr(wrapped, name)
            if inspect.iscoroutinefunction(obj):
                return synchronize(obj)
            return obj

        return super().__getattribute__(name)

    @override
    def __setattr__(self, /, name: str, value: object) -> None:
        """Allow for changing attributes of the wrapped object.

        * If wrapped object isn't yet set, fall back to [`__setattr__`][?object.] of this class.
        * If wrapped object doesn't already contain the attribute we want to set, also fallback to this class.
        * Otherwise, run `__setattr__` on it to update it.
        """
        try:
            wrapped = getattr(self, self._WRAPPED_ATTRIBUTE)
        except AttributeError:
            return super().__setattr__(name, value)
        else:
            if hasattr(wrapped, name):
                return setattr(wrapped, name, value)

        return super().__setattr__(name, value)


class UnpropagatingMockMixin(Generic[T_Mock]):
    """Provides common functionality for our [`Mock`][unittest.mock.] classes.

    By default, mock objects propagate themselves by returning a new instance of the same mock
    class, with same initialization attributes. This is done whenever we're accessing new
    attributes that mock class.

    This propagation makes sense for simple mocks without any additional restrictions, however when
    dealing with limited mocks to some `spec_set`, it doesn't usually make sense to propagate
    those same `spec_set` restrictions, since we generally don't have attributes/methods of a
    class be of/return the same class.

    This mixin class stops this propagation, and instead returns instances of specified mock class,
    defined in [`child_mock_type`][.] class variable, which is by default set to [`MagicMock`][unittest.mock.],
    as it can safely represent most objects.

    Note:
        This propagation handling will only be done for the mock classes that inherited from this
        mixin class. That means if the [`child_mock_type`][.] is one of the regular mock classes,
        and the mock is propagated, a regular mock class is returned as that new attribute. This
        regular class then won't have the same overrides, and will therefore propagate itself, like
        any other mock class would.

        If you wish to counteract this, you can set the [`child_mock_type`][.] to a mock class
        that also inherits from this mixin class, perhaps to your class itself, overriding any
        propagation recursively.
    """

    child_mock_type: T_Mock = unittest.mock.MagicMock

    # Since this is a mixin class, we can access some attributes defined in mock classes safely.
    # Define the types of these variables here, for proper static type analysis.
    _mock_sealed: bool
    _extract_mock_name: Callable[[], str]

    def _get_child_mock(self, **kwargs: object) -> T_Mock:
        """Make [`child_mock_type`][..] instances instead of instances of the same class.

        By default, this method creates a new mock instance of the same original class, and passes
        over the same initialization arguments. This overrides that behavior to instead create an
        instance of `child_mock_type` class.
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


class CustomMockMixin(UnpropagatingMockMixin[T_Mock], Generic[T_Mock]):
    """Provides common functionality for our custom mock types.

    * Stops propagation of same `spec_set` restricted mock in child mocks
      (see [`UnpropagatingMockMixin`][(m).] for more info)
    * Allows using the `spec_set` attribute as class attribute
    """

    spec_set = None

    def __init__(self, **kwargs: object):
        if "spec_set" in kwargs:
            self.spec_set = kwargs.pop("spec_set")
        super().__init__(spec_set=self.spec_set, **kwargs)  # pyright: ignore[reportCallIssue]  # Mixin class, this __init__ is valid


def isexception(obj: object) -> TypeIs[type[Exception] | TestExc]:
    """Check if the object is an exception."""
    return (isinstance(obj, type) and issubclass(obj, Exception)) or isinstance(obj, TestExc)


class TestExc(NamedTuple):
    """Named tuple to check if an exception is raised with a specific message.

    Args:
        exception: The exception type.
        match:
            If specified, a string containing a regular expression, or a regular expression object, that is
            tested against the string representation of the exception using [`re.search`][re.search].

        kwargs: The keyword arguments passed to the exception.

    If [`kwargs`][.] is not `None`, the exception instance will need to have the same attributes with the same values.
    """

    exception: type[Exception] | tuple[type[Exception], ...]
    match: str | re.Pattern[str] | None = None
    kwargs: dict[str, Any] | None = None

    @classmethod
    def from_exception(cls, exception: type[Exception] | tuple[type[Exception], ...] | TestExc) -> TestExc:
        """Create a [`TestExc`][(m).] from an exception, does nothing if the object is already a `TestExc`."""
        if isinstance(exception, TestExc):
            return exception
        return cls(exception)


def gen_serializable_test(
    context: dict[str, Any],
    cls: type[Serializable],
    fields: list[tuple[str, type | str]],
    serialize_deserialize: list[tuple[tuple[Any, ...], bytes]] | None = None,
    validation_fail: list[tuple[tuple[Any, ...], type[Exception] | TestExc]] | None = None,
    deserialization_fail: list[tuple[bytes, type[Exception] | TestExc]] | None = None,
):
    """Generate tests for a serializable class.

    This function generates tests for the serialization, deserialization, validation, and deserialization error
    handling

    Args:
        context: The context to add the test functions to. This is usually `globals()`.
        cls: The serializable class to test.
        fields: A list of tuples containing the field names and types of the serializable class.
        serialize_deserialize:
            A list of tuples containing:

            - The tuple representing the arguments to pass to the [`Serializable`][mcproto.utils.abc.] class
            - The expected bytes
        validation_fail:
            A list of tuples containing the arguments to pass to the [`Serializable`][mcproto.utils.abc.] class
            and the expected exception, either as is or wrapped in a [`TestExc`][(m).] object.
        deserialization_fail:
            A list of tuples containing the bytes to pass to the
            [`deserialize`][mcproto.utils.abc.Serializable.deserialize] method of the class and the expected exception,
            either as is or wrapped in a [`TestExc`][(m).] object.

    Example usage:
        See `tests.mcproto.utils.test_serializable.py` (specifically the `ToyClass`)

        This will add 1 class test with 4 test functions containing the tests for serialization, deserialization,
        validation, and deserialization error handling

    Note:
        The test cases will use `__eq__` to compare the objects, so make sure to implement it in the class if
        you are not using the autogenerated method from [`attrs.define`][?attrs.define].

    """
    # This holds the parameters for the serialization and deserialization tests
    parameters: list[tuple[dict[str, Any], bytes]] = []

    # This holds the parameters for the validation tests
    validation_fail_kw: list[tuple[dict[str, Any], TestExc]] = []

    for data, exp_bytes in [] if serialize_deserialize is None else serialize_deserialize:
        kwargs = dict(zip([f[0] for f in fields], data))
        parameters.append((kwargs, exp_bytes))

    for data, exc in [] if validation_fail is None else validation_fail:
        kwargs = dict(zip([f[0] for f in fields], data))
        exc_wrapped = TestExc.from_exception(exc)
        validation_fail_kw.append((kwargs, exc_wrapped))

    # Just make sure that the exceptions are wrapped in TestExc
    deserialization_fail = (
        []
        if deserialization_fail is None
        else [(data, TestExc.from_exception(exc)) for data, exc in deserialization_fail]
    )

    def generate_name(param: dict[str, Any] | bytes, i: int) -> str:
        """Generate a name for the test case."""
        length = 30
        result = f"{i:02d}] : "  # the first [ is added by pytest
        if isinstance(param, bytes):
            result += repr(param[:length]) + "..." if len(param) > (length + 3) else repr(param)
        elif isinstance(param, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
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
            validation_fail_kw,
            ids=tuple(generate_name(kwargs, i) for i, (kwargs, _) in enumerate(validation_fail_kw)),
        )
        def test_validation(self, kwargs: dict[str, Any], exc: TestExc):
            """Test validation of the object."""
            with pytest.raises(exc.exception, match=exc.match) as exc_info:
                _ = cls(**kwargs)

            # If exc.kwargs is not None, check them against the exception
            if exc.kwargs is not None:
                for key, value in exc.kwargs.items():
                    assert value == getattr(exc_info.value, key), (
                        f"{key}: {value!r} != {getattr(exc_info.value, key)!r}"
                    )

        @pytest.mark.parametrize(
            ("content", "exc"),
            deserialization_fail,
            ids=tuple(generate_name(content, i) for i, (content, _) in enumerate(deserialization_fail)),
        )
        def test_deserialization_error(self, content: bytes, exc: TestExc):
            """Test deserialization error handling."""
            buf = Buffer(content)
            with pytest.raises(exc.exception, match=exc.match) as exc_info:
                _ = cls.deserialize(buf)

            # If exc.kwargs is not None, check them against the exception
            if exc.kwargs is not None:
                for key, value in exc.kwargs.items():
                    assert value == getattr(exc_info.value, key), (
                        f"{key}: {value!r} != {getattr(exc_info.value, key)!r}"
                    )

    if len(parameters) == 0:
        # If there are no serialization tests, remove them
        del TestClass.test_serialization
        del TestClass.test_deserialization

    if len(validation_fail_kw) == 0:
        # If there are no validation tests, remove them
        del TestClass.test_validation

    if len(deserialization_fail) == 0:
        # If there are no deserialization error tests, remove them
        del TestClass.test_deserialization_error

    # Set the names of the class
    TestClass.__name__ = f"TestGen{cls.__name__}"

    # Add the test functions to the global context
    context[TestClass.__name__] = TestClass  # BERK
