from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Callable, Iterable, Iterator, Mapping
from itertools import chain
from types import ModuleType
from typing import Literal, NoReturn, Optional, TYPE_CHECKING, TypeVar, overload

from mcproto.packets.abc import ClientBoundPacket, GameState, Packet, PacketDirection, ServerBoundPacket

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    P = ParamSpec("P")
    R = TypeVar("R")

    # Typing-time signature fix for functools.cache, not propagating the function parameters
    # https://github.com/python/mypy/issues/5107
    def cache(__user_function: Callable[P, R], /) -> Callable[P, R]:
        ...

else:
    from functools import cache

__all__ = [
    "StatePacketMap",
    "get_full_packet_map",
    "get_packet_map",
]


# Fully qualified name to the package with the versioned packet implementations
# (This package should contain packages like 'v757', which then contain their corresponding
# modules with the packet classes.)
PACKETS_DIR_QUALNAME = "mcproto.packets"


class StatePacketMap:
    """Grouping of packets belonging to a single game state (like HANDSHAKING/LOGIN).

    :param GameState game_state: The game state this packet map is for
    :param Optional[dict[int, type[ServerBoundPacket]]] server_bound: Mapping of packet id to server-bound packets.
        If no value is given (or None is passed explicitly), a new empty dict will be made.
    :param Optional[dict[int, type[ClientBoundPacket]]] client_bound: Mapping of packet id to client-bound packets.
        If no value is given (or None is passed explicitly), a new empty dict will be made.
    """

    __slots__ = ("server_bound", "client_bound", "game_state")

    def __init__(
        self,
        game_state: GameState,
        server_bound: Optional[dict[int, type[ServerBoundPacket]]] = None,
        client_bound: Optional[dict[int, type[ClientBoundPacket]]] = None,
    ):
        if server_bound is None:
            server_bound = {}
        if client_bound is None:
            client_bound = {}

        for packet in chain(server_bound.values(), client_bound.values()):
            if not packet.GAME_STATE == game_state:
                raise ValueError(
                    f"Got invalid packet ({packet.__qualname__}), mismatched game state"
                    f" (expected: {game_state.name}, packet has: {packet.GAME_STATE.name})"
                )

        self.game_state = game_state
        self.server_bound = server_bound
        self.client_bound = client_bound

    def register(self, packet: type[Packet]) -> None:
        """Register a new packet to this state packet map."""
        if packet.GAME_STATE is not self.game_state:
            raise ValueError(
                f"Invalid packet ({packet.__qualname__}), mismatched game state"
                f" (expected: {self.game_state.name}, packet has: {packet.GAME_STATE.name})"
            )

        if issubclass(packet, ServerBoundPacket):
            if packet.PACKET_ID in self.server_bound:
                raise ValueError(
                    f"Server-bound packet with this id ({packet.PACKET_ID}) is already registered"
                    f" (registered class: {self.server_bound[packet.PACKET_ID].__qualname__})!"
                )
            self.server_bound[packet.PACKET_ID] = packet

        # We use another if here, as some packet classes may be both server and client bound
        if issubclass(packet, ClientBoundPacket):
            if packet.PACKET_ID in self.client_bound:
                raise ValueError(
                    f"Client-bound packet with this id ({packet.PACKET_ID}) is already registered"
                    f" (registered class: {self.client_bound[packet.PACKET_ID].__qualname__})!"
                )
            self.client_bound[packet.PACKET_ID] = packet

        # Sanity check
        if not issubclass(packet, (ClientBoundPacket, ServerBoundPacket)):
            raise TypeError(f"Invalid packet class ({packet}), expected ServerBoundPacket or ClientBoundPacket.")

    def __repr__(self) -> str:
        server_bound_s = ", ".join(f"{id_}: {packet.__qualname__}" for id_, packet in self.server_bound.items())
        client_bound_s = ", ".join(f"{id_}: {packet.__qualname__}" for id_, packet in self.client_bound.items())
        return f"<{self.__class__.__name__}(server_bound=[{server_bound_s}], client_bound=[{client_bound_s}])>"


def _walk_packets(module: ModuleType) -> Iterator[type[Packet]]:
    """Return all packet classes found from given module.

    Note that this only searches classes mentioned in __all__, rather than actually going
    over every variable defined in these modules. This is done to prevent returning the same
    packet more than once and to avoid needlessly checking too many variables.

    This does however mean that defining __all__ is now a requirement for the modules with
    the packet implementations, as otherwise the packet classes won't get picked up here.
    """
    # TODO: Create a README.md file in mcproto.packets, mentioning how our packets work
    # and also mention this __all__ requirement there.

    def on_error(name: str) -> NoReturn:
        raise ImportError(name=name)

    for module_info in pkgutil.walk_packages(module.__path__, f"{module.__name__}.", onerror=on_error):
        imported = importlib.import_module(module_info.name)

        if not hasattr(imported, "__all__"):
            continue
        member_names = imported.__all__

        if not isinstance(member_names, Iterable):
            raise TypeError(f"Module {module_info.name!r}'s __all__ isn't defined as an iterable.")

        for member_name in member_names:
            try:
                member = getattr(imported, member_name)
            except AttributeError as exc:
                raise TypeError(f"Member {member_name!r} of {module_info.name!r} module isn't defined.") from exc

            if not issubclass(member, Packet):
                continue

            yield member


# Holding the packet maps in memory in cache is ok as they're relatively small, and
# it's a much better option than recomputing it every time, as we need to call it with
# each read/write packet.
@cache
def get_full_packet_map(protocol_version: int) -> dict[GameState, StatePacketMap]:
    """Load all of the packet classes and build a packet map for given protocol version."""
    module_name = f"mcproto.packets.v{protocol_version}"

    try:
        module = importlib.import_module(str(module_name))
    except ModuleNotFoundError as exc:
        raise ValueError(f"Passed protocol version ({protocol_version}) isn't supported.") from exc

    packet_map: dict[GameState, StatePacketMap] = {}
    for packet in _walk_packets(module):
        state_map = packet_map.setdefault(packet.GAME_STATE, StatePacketMap(packet.GAME_STATE))
        try:
            state_map.register(packet)
        except ValueError as exc:
            raise ValueError(
                f"Failed to register {packet.GAME_STATE.name.lower()} state packet with id {packet.PACKET_ID}"
                f" ({packet.__qualname__}). Error: {exc}"
            ) from exc

    return packet_map


@overload
def get_packet_map(
    *,
    protocol_version: int,
    game_state: GameState,
    direction: Literal[PacketDirection.SERVERBOUND],
) -> Mapping[int, type[ServerBoundPacket]]:
    ...


@overload
def get_packet_map(
    *,
    protocol_version: int,
    game_state: GameState,
    direction: Literal[PacketDirection.CLIENTBOUND],
) -> Mapping[int, type[ClientBoundPacket]]:
    ...


def get_packet_map(
    *,
    protocol_version: int,
    game_state: GameState,
    direction: PacketDirection,
) -> Mapping[int, type[Packet]]:
    full_map = get_full_packet_map(protocol_version)
    state_map = full_map[game_state]

    if direction is PacketDirection.SERVERBOUND:
        return state_map.server_bound
    elif direction is PacketDirection.CLIENTBOUND:
        return state_map.client_bound
    else:
        raise ValueError("Invalid direction")
