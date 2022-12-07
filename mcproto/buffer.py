from mcproto.protocol.base_io import BaseSyncReader, BaseSyncWriter

__all__ = ["Buffer"]


class Buffer(BaseSyncWriter, BaseSyncReader, bytearray):
    __slots__ = ("pos",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pos = 0

    def write(self, data: bytes) -> None:
        """Write new data into the buffer."""
        self.extend(data)

    def read(self, length: int) -> bytearray:
        """Read data stored in the buffer.

        Reading data doesn't remove that data, rather that data is treated as already read, and
        next read will start from the first unread byte. If freeing the data is necessary, check the clear function.

        Trying to read more data than is available will raise an IOError, however it will deplete the remaining data
        and the partial data that was read will be a part of the error message. This behavior is here to mimic reading
        from a socket connection.
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
        """
        Clear out the stored data and reset position.

        If `only_already_read` is True, only clear out the data which was already read, and reset the position.
        This is mostly useful to avoid keeping large chunks of data in memory for no reason.
        """
        if only_already_read:
            del self[: self.pos]
        else:
            super().clear()
        self.pos = 0

    def reset(self) -> None:
        """Reset the position in the buffer."""
        self.pos = 0

    def flush(self) -> bytearray:
        """Read all of the remaining data in the buffer and clear it out."""
        data = self[self.pos : len(self)]
        self.clear()
        return data

    @property
    def remaining(self) -> int:
        """Get the amount of bytes that's still remaining in be buffer to be read."""
        return len(self) - self.pos
