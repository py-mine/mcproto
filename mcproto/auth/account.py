from __future__ import annotations

from mcproto.types.uuid import UUID as McUUID  # noqa: N811

__all__ = ["Account"]


class Account:
    __slots__ = ("username", "uuid", "access_token")

    def __init__(self, username: str, uuid: McUUID, access_token: str) -> None:
        self.username = username
        self.uuid = uuid
        self.access_token = access_token
