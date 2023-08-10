from __future__ import annotations

import json
from typing import Any

import pytest

from mcproto.buffer import Buffer
from mcproto.packets.status.status import StatusResponse


@pytest.mark.parametrize(
    ("data", "expected_bytes"),
    [
        (
            {
                "description": {"text": "A Minecraft Server"},
                "players": {"max": 20, "online": 0},
                "version": {"name": "1.18.1", "protocol": 757},
            },
            bytes.fromhex(
                "797b226465736372697074696f6e223a7b2274657874223a2241204d696e6"
                "5637261667420536572766572227d2c22706c6179657273223a7b226d6178"
                "223a32302c226f6e6c696e65223a20307d2c2276657273696f6e223a7b226"
                "e616d65223a22312e31382e31222c2270726f746f636f6c223a3735377d7d"
            ),
        ),
    ],
)
def test_serialize(data: dict[str, Any], expected_bytes: bytes):
    """Test serialization of StatusResponse packet."""
    expected_buffer = Buffer(expected_bytes)
    # Clear the length before the actual JSON data. JSON strings are encoded using UTF (StatusResponse uses
    # `write_utf`), so `write_utf` writes the length of the string as a varint before writing the string itself.
    expected_buffer.read_varint()
    expected_bytes = expected_buffer.flush()

    buffer = StatusResponse(data=data).serialize()
    buffer.read_varint()  # Ditto
    out = buffer.flush()

    assert json.loads(out) == json.loads(expected_bytes)


@pytest.mark.parametrize(
    ("read_bytes", "expected_data"),
    [
        (
            bytes.fromhex(
                "797b226465736372697074696f6e223a7b2274657874223a2241204d696e6"
                "5637261667420536572766572227d2c22706c6179657273223a7b226d6178"
                "223a32302c226f6e6c696e65223a20307d2c2276657273696f6e223a7b226"
                "e616d65223a22312e31382e31222c2270726f746f636f6c223a3735377d7d"
            ),
            {
                "description": {"text": "A Minecraft Server"},
                "players": {"max": 20, "online": 0},
                "version": {"name": "1.18.1", "protocol": 757},
            },
        ),
    ],
)
def test_deserialize(read_bytes: list[int], expected_data: dict[str, Any]):
    """Test deserialization of StatusResponse packet."""
    status = StatusResponse.deserialize(Buffer(read_bytes))

    assert expected_data == status.data
