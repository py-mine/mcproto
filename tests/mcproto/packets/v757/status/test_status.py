from __future__ import annotations

from typing import Any

import pytest

from mcproto.packets.v757.status.status import StatusResponse


@pytest.mark.parametrize(
    ("data"),
    [
        (
            {
                "description": {"text": "A Minecraft Server"},
                "players": {"max": 20, "online": 0},
                "version": {"name": "1.18.1", "protocol": 757},
            }
        ),
    ],
)
def test_serialize_deserialize(data: dict[str, Any]):
    # I had to combine the methods, because Minecraft returns a JSON with no spaces,
    # but Python adds spaces after commas and colons.
    status = StatusResponse(data=data)
    assert StatusResponse.deserialize(status.serialize()).data == data
