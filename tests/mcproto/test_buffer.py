from __future__ import annotations

import pytest

from mcproto.buffer import Buffer


def test_write():
    """Writing into the buffer should store data."""
    buf = Buffer()
    buf.write(b"Hello")
    assert buf, bytearray(b"Hello")


def test_read():
    """Reading from buffer should return stored data."""
    buf = Buffer(b"Reading is cool")
    data = buf.read(len(buf))
    assert data == b"Reading is cool"


def test_read_multiple():
    """Multiple reads should deplete the data."""
    buf = Buffer(b"Something random")
    data = buf.read(9)
    assert data == b"Something"
    data = buf.read(7)
    assert data == b" random"


def test_no_data_read():
    """Reading more data than available should raise IOError."""
    buf = Buffer(b"Blip")
    with pytest.raises(IOError):
        _ = buf.read(len(buf) + 1)


def test_reset():
    """Resetting should treat already read data as new unread data."""
    buf = Buffer(b"Will it reset?")
    data = buf.read(len(buf))
    buf.reset()
    data2 = buf.read(len(buf))
    assert data == data2
    assert data == b"Will it reset?"


def test_clear():
    """Clearing should remove all stored data from buffer."""
    buf = Buffer(b"Will it clear?")
    buf.clear()
    assert buf == bytearray()


def test_clear_resets_position():
    """Clearing should reset reading position for new data to be read."""
    buf = Buffer(b"abcdef")
    _ = buf.read(3)
    buf.clear()
    buf.write(b"012345")
    data = buf.read(3)
    assert data == b"012"


def test_clear_read_only():
    """Clearing should allow just removing the already read data."""
    buf = Buffer(b"0123456789")
    _ = buf.read(5)
    buf.clear(only_already_read=True)
    assert buf == bytearray(b"56789")


def test_flush():
    """Flushing should read all available data and clear out the buffer."""
    buf = Buffer(b"Foobar")
    data = buf.flush()
    assert data == b"Foobar"
    assert buf == bytearray()


def test_remainig():
    """Buffer should report correct amount of remaining bytes to be read."""
    buf = Buffer(b"012345")  # 6 bytes to be read
    assert buf.remaining == 6
    _ = buf.read(2)
    assert buf.remaining == 4
    buf.clear()
    assert buf.remaining == 0
