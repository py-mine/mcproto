from __future__ import annotations


from mcproto.packets.status.status import StatusResponse
from tests.helpers import gen_serializable_test

gen_serializable_test(
    context=globals(),
    cls=StatusResponse,
    fields=[("data", "dict[str, Any]")],
    serialize_deserialize=[
        (
            (
                {
                    "description": {"text": "A Minecraft Server"},
                    "players": {"max": 20, "online": 0},
                    "version": {"name": "1.18.1", "protocol": 757},
                },
            ),
            bytes.fromhex(
                "787b226465736372697074696f6e223a7b2274657874223a2241204d696e6"
                "5637261667420536572766572227d2c22706c6179657273223a7b226d6178"
                "223a32302c226f6e6c696e65223a307d2c2276657273696f6e223a7b226e6"
                "16d65223a22312e31382e31222c2270726f746f636f6c223a3735377d7d"
            ),
        ),
    ],
    validation_fail=[
        # Unserializable data for JSON
        (({"data": object()},), ValueError),
    ],
)
