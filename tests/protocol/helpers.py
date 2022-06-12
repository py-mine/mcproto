from typing import Optional
from unittest.mock import AsyncMock, Mock

from mcproto.protocol.abc import BaseAsyncReader, BaseAsyncWriter, BaseSyncReader, BaseSyncWriter
from tests.helpers import SynchronizedMixin


class WriteFunctionMock(Mock):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.combined_data = bytearray()

    def __call__(self, data: bytearray) -> None:
        """Override mock's __call__ to extend our combined_data bytearray.

        This allows us to keep track of exactly what data was written by the mocked write function
        in total, rather than only having tools like assert_called_with, which don't combine the
        data of each call.
        """
        self.combined_data.extend(data)
        return super().__call__(data)

    def assert_has_data(self, data: bytearray, ensure_called: bool = True) -> None:
        """Ensure that the total data to write by the mocked function matches expected data."""
        if ensure_called:
            self.assert_called()

        if self.combined_data != data:
            raise AssertionError(f"Write function mock expected data {data!r}, but was {self.call_data!r}")


class WriteFunctionAsyncMock(WriteFunctionMock, AsyncMock):
    ...


class ReadFunctionMock(Mock):
    def __init__(self, *a, combined_data: Optional[bytearray] = None, **kw):
        super().__init__(*a, **kw)
        if combined_data is None:
            combined_data = bytearray()
        self.combined_data = combined_data

    def __call__(self, length: int) -> bytearray:
        """Override mock's __call__ to make it return part of our combined_data bytearray.

        This allows us to define the combined data we want the mocked read function to be
        returning, and have each call only take requested part (length) of that data.
        """
        self.return_value = self.combined_data[:length]
        del self.combined_data[:length]
        return super().__call__(length)

    def assert_read_everything(self) -> None:
        """Ensure that the passed combined_data was fully read and depleted by one, or more calls."""
        if len(self.combined_data) != 0:
            raise AssertionError(
                f"Read function didn't deplete all of it's data, remaining data: {self.combined_data!r}"
            )


class ReadFunctionAsyncMock(ReadFunctionMock, AsyncMock):
    ...


class SyncWriter(BaseSyncWriter):
    """Initializable concrete implementation of BaseSyncWriter ABC."""

    def write(self, data: bytearray) -> None:
        """Concrete implementation of abstract write method.

        Since classes using abc.ABC can't be initialized if they have any abstract methods
        which weren't overridden with a concrete implementation, this is a fake implementation,
        without any actual logic, purely to allow the initialization of this class.

        This method is expected to be mocked using WriteFunctionMock if it's expected to get called
        during testing. If this method gets called without being mocked, it will raise NotImplementedError.
        """
        raise NotImplementedError(
            "This concrete override of abstract write method isn't intended for actual use!\n"
            " - If you're writing a new test, did you forget to mock it?\n"
            " - If you're seeing this in an existing test, this method got called without the test expecting it,"
            " this probably means you changed something in the code leading to this call, but you haven't updated"
            " the tests to mock this function."
        )


class SyncReader(BaseSyncReader):
    """Testable concrete implementation of BaseSyncReader ABC."""

    def read(self, length: int) -> bytearray:
        """Concrete implementation of abstract read method.

        Since classes using abc.ABC can't be initialized if they have any abstract methods
        which weren't overridden with a concrete implementation, this is a fake implementation,
        without any actual logic, purely to allow the initialization of this class.

        This method is expected to be mocked using ReadFunctionMock if it's expected to get called
        during testing. If this method gets called without being mocked, it will raise NotImplementedError.
        """
        raise NotImplementedError(
            "This concrete override of abstract read method isn't intended for actual use!\n"
            " - If you're writing a new test, did you forget to mock it?\n"
            " - If you're seeing this in an existing test, this method got called without the test expecting it,"
            " this probably means you changed something in the code leading to this call, but you haven't updated"
            " the tests to mock this function."
        )


class AsyncWriter(BaseAsyncWriter):
    """Initializable concrete implementation of BaseAsyncWriter ABC."""

    async def write(self, data: bytearray) -> None:
        """Concrete implementation of abstract write method.

        Since classes using abc.ABC can't be initialized if they have any abstract methods
        which weren't overridden with a concrete implementation, this is a fake implementation,
        without any actual logic, purely to allow the initialization of this class.

        This method is expected to be mocked using WriteFunctionAsyncMock if it's expected to get called
        during testing. If this method gets called without being mocked, it will raise NotImplementedError.
        """
        raise NotImplementedError(
            "This concrete override of abstract write method isn't intended for actual use!\n"
            " - If you're writing a new test, did you forget to mock it?\n"
            " - If you're seeing this in an existing test, this method got called without the test expecting it,"
            " this probably means you changed something in the code leading to this call, but you haven't updated"
            " the tests to mock this function."
        )


class AsyncReader(BaseAsyncReader):
    """Testable concrete implementation of BaseAsyncReader ABC."""

    async def read(self, length: int) -> bytearray:
        """Concrete implementation of abstract read method.

        Since classes using abc.ABC can't be initialized if they have any abstract methods
        which weren't overridden with a concrete implementation, this is a fake implementation,
        without any actual logic, purely to allow the initialization of this class.

        This method is expected to be mocked using ReadFunctionAsyncMock if it's expected to get called
        during testing. If this method gets called without being mocked, it will raise NotImplementedError.
        """
        raise NotImplementedError(
            "This concrete override of abstract read method isn't intended for actual use!\n"
            " - If you're writing a new test, did you forget to mock it?\n"
            " - If you're seeing this in an existing test, this method got called without the test expecting it,"
            " this probably means you changed something in the code leading to this call, but you haven't updated"
            " the tests to mock this function."
        )


class WrappedAsyncReader(SynchronizedMixin):
    """Wrapped synchronous implementation of asynchronous AsyncReader class."""

    _WRAPPED_ATTRIBUTE = "_reader"

    def __init__(self):
        self._reader = AsyncReader()


class WrappedAsyncWriter(SynchronizedMixin):
    """Wrapped synchronous implementation of asynchronous AsyncWriter class."""

    _WRAPPED_ATTRIBUTE = "_writer"

    def __init__(self):
        self._writer = AsyncWriter()


def to_two_complement(number: int, bytes: int) -> int:
    """Helper function to convert a number into two's complement format."""
    return number + 2 ** (bytes * 8)


def from_two_complement(number: int, bytes: int) -> int:
    """Helper function to get the real value from int in two's complement format."""
    return number - 2 ** (bytes * 8) + 1
