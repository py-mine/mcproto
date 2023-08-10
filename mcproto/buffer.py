from __future__ import annotations

from mcproto.protocol.base_io import BaseSyncReader, BaseSyncWriter

__all__ = ["Buffer"]


class Buffer(BaseSyncWriter, BaseSyncReader, bytearray):
    """In-memory bytearray-like buffer supporting the common read/write operations."""

    __slots__ = ("pos",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pos = 0

    def write(self, data: bytes) -> None:
        """Write/Store given ``data`` into the buffer."""
        self.extend(data)

    def read(self, length: int) -> bytearray:
        """Read data stored in the buffer.

        Reading data doesn't remove that data, rather that data is treated as already read, and
        next read will start from the first unread byte. If freeing the data is necessary, check
        the :meth:`.clear` function.

        :param length:
            Amount of bytes to be read.

            If the requested amount can't be read (buffer doesn't contain that much data/buffer
            doesn't contain any data), an :exc:`IOError` will be reaised.

            If there were some data in the buffer, but it was less than requested, this remaining
            data will still be depleted and the partial data that was read will be a part of the
            error message in the :exc:`IOError`. This behavior is here to mimic reading from a real
            socket connection.
        """
        end = self.pos + length

        if end > len(self):
            data = self[self.pos : len(self)]
            bytes_read = len(self) - self.pos
            self.pos = len(self)
            raise IOError(
                "Requested to read more data than available."
                f" Read {bytes_read} bytes: {data}, out of {length} requested bytes."
            )

        try:
            return self[self.pos : end]
        finally:
            self.pos = end

    def clear(self, only_already_read: bool = False) -> None:
        """Clear out the stored data and reset position.

        :param only_already_read:
            When set to ``True``, only the data that was already marked as read will be cleared,
            and the position will be reset (to start at the remaining data). This can be useful
            for avoiding needlessly storing large amounts of data in memory, if this data is no
            longer useful.

            Otherwise, if set to ``False``, all of the data is cleared, and the position is reset,
            essentially resulting in a blank buffer.
        """
        if only_already_read:
            del self[: self.pos]
        else:
            super().clear()
        self.pos = 0

    def reset(self) -> None:
        """Reset the position in the buffer.

        Since the buffer doesn't automatically clear the already read data, it is possible to simply
        reset the position and read the data it contains again.
        """
        self.pos = 0

    def flush(self) -> bytearray:
        """Read all of the remaining data in the buffer and clear it out."""
        data = self[self.pos : len(self)]
        self.clear()
        return data

    @property
    def remaining(self) -> int:
        """Get the amount of bytes that's still remaining in the buffer to be read."""
        return len(self) - self.pos
