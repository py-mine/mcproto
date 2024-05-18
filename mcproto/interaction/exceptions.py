from __future__ import annotations

from mcproto.packets.packet import GameState, Packet


class InvalidGameStateError(Exception):
    """Exception raised when the current game state didn't match the expected game state.

    Many of the minecraft communication flows, such as login, or status requesting requires
    to start from a specific game state. For example login can't be performed again, if we're
    already in the play game state.
    """

    def __init__(
        self,
        reason: str | None = None,
        /,
        *,
        expected: GameState | None | tuple[GameState | None, ...],
        found: GameState | None,
    ) -> None:
        if not isinstance(expected, tuple):
            expected = (expected,)

        self.reason = reason
        self.expected_state = expected
        self.found_state = found
        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        """Produce a message for this error."""
        if len(self.expected_state) == 1:
            state = self.expected_state[0]
            msg = "Expected initial (no) game state" if state is None else f"Expected {state.name} game state"
        else:
            states = ", ".join(state.name if state is not None else "None" for state in self.expected_state)
            msg = f"Expected one of: {states} game states"

        if self.found_state is None:
            msg += ", but found initial (no) game state"
        else:
            msg += f", but found {self.found_state.name} game state"

        if self.reason:
            msg += f": {self.reason}"
        return msg

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.msg!r})"


class UnexpectedPacketError(Exception):
    """Exception produced when the obtained packet wasn't the packet we expected.

    In many minecraft communication flows, such as login, there are only a few (or just one)
    specific packet types that we expect to be sent next. If a different packet is received,
    this exception will be raised.
    """

    def __init__(
        self,
        reason: str | None = None,
        /,
        *,
        expected: type[Packet] | tuple[type[Packet], ...],
        found: Packet,
    ) -> None:
        if not isinstance(expected, tuple):
            expected = (expected,)

        self.reason = reason
        self.expected_packet_types = expected
        self.found_packet = found
        super().__init__(self.reason)

    @property
    def msg(self) -> str:
        """Produce a message for this error."""
        if len(self.expected_packet_types) == 1:
            expected_packet = self.expected_packet_types[0].__name__
            msg = f"Expected a {expected_packet} packet"
        else:
            expected_packets = ", ".join(packet.__name__ for packet in self.expected_packet_types)
            msg = f"Expected one of {expected_packets} packets"

        msg += f", but found {self.found_packet!r}"

        if self.reason:
            msg += f": {self.reason}"

        return msg

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.msg!r})"


class InvalidVerifyTokenError(Exception):
    """Exception produced when the verify_token from client doesn't match the one sent by the server.

    The verify_token is sent by the server in `~mcproto.packets.login.login.LoginEncryptionRequest`, then
    encrypted by the client and sent back in `~mcproto.packets.login.login.LoginEncryptionResponse`.
    """

    def __init__(self, original_token: bytes, received_decrypted_token: bytes) -> None:
        self.original_token = original_token
        self.received_decrypted_token = received_decrypted_token
        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        """Produce a message for this error."""
        return (
            "Client sent mismatched verify token:"
            f" original: {self.original_token!r},"
            f" received: {self.received_decrypted_token!r}"
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.msg!r})"
