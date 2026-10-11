from __future__ import annotations

from unittest.mock import AsyncMock, Mock

from typing_extensions import override


class WriteFunctionMock(Mock):
    """Mock write function, storing the written data."""

    def __init__(self, *a: object, **kw: object):
        super().__init__(*a, **kw)
        self.combined_data = bytearray()

    @override
    def __call__(self, data: bytes) -> None:
        """Override mock's `__call__` to extend our `combined_data` bytearray.

        This allows us to keep track of exactly what data was written by the mocked write function
        in total, rather than only having tools like [`assert_called_with`][?unittest.mock.Mock.],
        which might let us get the data from individual calls, but not the combined data, which is
        what we'll need.
        """
        self.combined_data.extend(data)
        return super().__call__(data)

    @override
    def assert_has_data(self, data: bytearray, ensure_called: bool = True) -> None:
        """Ensure that the combined write data by the mocked function matches expected `data`."""
        if ensure_called:
            self.assert_called()

        if self.combined_data != data:
            raise AssertionError(f"Write function mock expected data {data!r}, but was {self.call_data!r}")


class WriteFunctionAsyncMock(WriteFunctionMock, AsyncMock):  # pyright: ignore[reportUnsafeMultipleInheritance]
    """Asynchronous mock write function, storing the written data."""


class ReadFunctionMock(Mock):
    """Mock read function, giving pre-defined data."""

    def __init__(self, *a: object, combined_data: bytearray | None = None, **kw: object):
        super().__init__(*a, **kw)
        if combined_data is None:
            combined_data = bytearray()
        self.combined_data = combined_data

    @override
    def __call__(self, length: int) -> bytearray:
        """Override mock's `__call__` to make it return part of our `combined_data` bytearray.

        This allows us to make the return value always be the next requested part (length) of
        the `combined_data`. It would be difficult to replicate this with regular mocks,
        because some functions can end up making multiple read calls, and each time the result
        needs to be different (the next part).
        """
        self.return_value = self.combined_data[:length]
        del self.combined_data[:length]
        return super().__call__(length)

    @override
    def assert_read_everything(self, ensure_called: bool = True) -> None:
        """Ensure that the passed `combined_data` was fully read and depleted."""
        if ensure_called:
            self.assert_called()

        if len(self.combined_data) != 0:
            raise AssertionError(
                f"Read function didn't deplete all of it's data, remaining data: {self.combined_data!r}"
            )


class ReadFunctionAsyncMock(ReadFunctionMock, AsyncMock):  # pyright: ignore[reportUnsafeMultipleInheritance]
    """Asynchronous mock read function, giving pre-defined data."""
