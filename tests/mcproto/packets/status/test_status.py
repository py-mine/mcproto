from __future__ import annotations

from typing import Any, Dict

from mcproto.packets.status.status import StatusResponse
from tests.helpers import gen_serializable_test

gen_serializable_test(
    context=globals(),
    cls=StatusResponse,
    fields=[("data", Dict[str, Any])],
    test_data=[
        (
            (
                {
                    "description": {"text": "A Minecraft Server"},
                    "players": {"max": 20, "online": 0},
                    "version": {"name": "1.18.1", "protocol": 757},
                },
            ),
            bytes.fromhex(
                "84017b226465736372697074696f6e223a207b2274657874223a202241204"
                "d696e65637261667420536572766572227d2c2022706c6179657273223a20"
                "7b226d6178223a2032302c20226f6e6c696e65223a20307d2c20227665727"
                "3696f6e223a207b226e616d65223a2022312e31382e31222c202270726f74"
                "6f636f6c223a203735377d7d"
                # Contains spaces that are not present in the expected bytes.
                # "5637261667420536572766572227d2c22706c6179657273223a7b226d6178"
                # "223a32302c226f6e6c696e65223a20307d2c2276657273696f6e223a7b226"
                # "e616d65223a22312e31382e31222c2270726f746f636f6c223a3735377d7d"
            ),
        ),
        # Unserializable data for JSON
        (({"data": object()},), ValueError),
    ],
)
