from mcproto.protocol.abc import BaseWriter, BaseReader


class Buffer(BaseWriter, BaseReader, bytearray):
    __slots__ = ("pos")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pos = 0

    def write(self, data: bytes) -> None:
        self.extend(data)

    def read(self, length: int) -> bytearray:
        try:
            return self[self.pos : self.pos + length]
        finally:
            self.pos += length

    def clear(self) -> None:
        """Clear out all of the stored data and reset position."""
        super().clear()
        self.reset()

    def reset(self) -> None:
        """Reset the position in the buffer."""
        self.pos = 0
