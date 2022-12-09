from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar, Literal, TYPE_CHECKING, overload

from mcproto.packets.abc import ClientBoundPacket, GameState, Packet, PacketDirection, ServerBoundPacket
from mcproto.utils.version_map import VersionMap, WalkableModuleData

if TYPE_CHECKING:
    from typing_extensions import TypeGuard

__all__ = ["PacketMap"]


class PacketMap(VersionMap[tuple[PacketDirection, GameState, int], type[Packet]]):
    SUPPORTED_VERSIONS: ClassVar[set[int]] = {757}
    COMPATIBLE_FALLBACK_VERSIONS: ClassVar[set[int]] = set()
    _SEARCH_DIR_QUALNAME: ClassVar[str] = "mcproto.packets"

    __slots__ = tuple()

    @overload
    def make_id_map(
        self,
        protocol_version: int,
        direction: Literal[PacketDirection.CLIENTBOUND],
        game_state: GameState,
    ) -> dict[int, type[ClientBoundPacket]]:
        ...

    @overload
    def make_id_map(
        self,
        protocol_version: int,
        direction: Literal[PacketDirection.SERVERBOUND],
        game_state: GameState,
    ) -> dict[int, type[ClientBoundPacket]]:
        ...

    def make_id_map(
        self,
        protocol_version: int,
        direction: PacketDirection,
        game_state: GameState,
    ) -> Mapping[int, type[Packet]]:
        """Construct a dictionary mapping (packet ID -> packet class) for values matching given attributes."""
        res = {}
        for (k_direction, k_game_state, k_packet_id), v in self.make_version_map(protocol_version).items():
            if k_direction is direction and k_game_state is game_state:
                res[k_packet_id] = v
        return res

    def _check_obj(
        self,
        obj: Any,  # noqa: ANN401
        module_data: WalkableModuleData,
        protocol_version: int,
    ) -> TypeGuard[type[Packet]]:
        """Determine whether a member object should be considered as a valid component for given protocol version.

        This method will be called for each potential member object (found when walking over all members of
        __all__ from all submodules of the package for given protocol version).

        This function shouldn't include any checks on whether an object is already registered in the version map
        (key collisions), these are handled during the collection in load_version, all this function is responsible
        for is checking whether this object is a valid component, components with conflicting keys are still
        considered valid here, as they're handled elsewhere.

        Although if there is some additional data that needs to be unique for a component to be valid, which wouldn't
        be caught as a key collision, this function can raise a ValueError.
        """
        return issubclass(obj, Packet)

    @classmethod
    def _make_obtain_key(
        cls,
        obj: type[Packet],
        module_data: WalkableModuleData,
        protocol_version: int,
    ) -> tuple[PacketDirection, GameState, int]:
        """Construct a unique obtain key for given object under given protocol version.

        Note: While the protocol version might be beneficial to know when constructing
        the obtain key, it shouldn't be used directly as a part of the key, as the items
        will already be split by their protocol versions, and this version will be known
        at obtaining time.
        """
        if issubclass(obj, ClientBoundPacket):
            direction = PacketDirection.CLIENTBOUND
        elif issubclass(obj, ServerBoundPacket):
            direction = PacketDirection.SERVERBOUND
        else:
            raise ValueError("Invalid packet class: Neither server-bound not client-bound.")

        return direction, obj.GAME_STATE, obj.PACKET_ID
