from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Iterator, Mapping, Sequence
from functools import lru_cache
from types import ModuleType
from typing import Literal, NamedTuple, NoReturn, overload

from mcproto.packets.packet import ClientBoundPacket, GameState, Packet, PacketDirection, ServerBoundPacket

__all__ = ["generate_packet_map"]

MODULE_PATHS = {
    GameState.HANDSHAKING: "mcproto.packets.handshaking",
    GameState.STATUS: "mcproto.packets.status",
    GameState.LOGIN: "mcproto.packets.login",
    GameState.PLAY: "mcproto.packets.play",
}


class WalkableModuleData(NamedTuple):
    module: ModuleType
    info: pkgutil.ModuleInfo
    member_names: Sequence[str]


def _walk_submodules(module: ModuleType) -> Iterator[WalkableModuleData]:
    """Find all submodules of given module, that specify ``__all__``.

    If a submodule that doesn't define ``__all__`` is found, it will be skipped, as we don't
    consider it walkable. (This is important, as we'll later need to go over all variables in
    these modules, and without ``__all__`` we wouldn't know what to go over. Simply using all
    defined variables isn't viable, as that would also include imported things, potentially
    causing the same object to appear more than once. This makes ``__all__`` a requirement.)
    """

    def on_error(name: str) -> NoReturn:
        raise ImportError(name=name)

    for module_info in pkgutil.walk_packages(module.__path__, f"{module.__name__}.", onerror=on_error):
        imported_module = importlib.import_module(module_info.name)

        if not hasattr(imported_module, "__all__"):
            continue
        member_names = imported_module.__all__

        if not isinstance(member_names, Sequence):
            raise TypeError(f"Module {module_info.name!r}'s __all__ isn't defined as a sequence.")

        for member_name in member_names:
            if not isinstance(member_name, str):
                raise TypeError(f"Module {module_info.name!r}'s __all__ contains non-string item.")

        yield WalkableModuleData(imported_module, module_info, member_names)


def _walk_module_packets(module_data: WalkableModuleData) -> Iterator[type[Packet]]:
    """Find all packet classes specified in module's ``__all__``.

    :return:
        Iterator yielding every packet class defined in ``__all__`` of given module.
        These objects are obtained directly using ``getattr`` from the imported module.

    :raises TypeError:
        Raised when an attribute defined in ``__all__`` can't be obtained using ``getattr``.
        This would suggest the module has incorrectly defined ``__all__``, as it includes values
        that aren't actually defined in the module.
    """
    for member_name in module_data.member_names:
        try:
            member = getattr(module_data.module, member_name)
        except AttributeError as exc:
            module_name = module_data.info.name
            raise TypeError(f"Member {member_name!r} of {module_name!r} module isn't defined.") from exc

        if issubclass(member, Packet):
            yield member


@overload
def generate_packet_map(
    direction: Literal[PacketDirection.SERVERBOUND],
    state: GameState,
) -> Mapping[int, type[ServerBoundPacket]]:
    ...


@overload
def generate_packet_map(
    direction: Literal[PacketDirection.CLIENTBOUND],
    state: GameState,
) -> Mapping[int, type[ClientBoundPacket]]:
    ...


@lru_cache()
def generate_packet_map(direction: PacketDirection, state: GameState) -> Mapping[int, type[Packet]]:
    """Dynamically generated a packet map for given ``direction`` and ``state``.

    This generation is done by dynamically importing all of the modules containing these packets,
    filtering them to only contain those pacekts with the specified parameters, and storing those
    into a dictionary, using the packet id as key, and the packet class itself being the value.

    As this fucntion is likely to be called quite often, and it uses dynamic importing to obtain
    the packet classes, this function is cached, which means the logic only actually runs once,
    after which, for the same arguments, the same dict will be returned.

    ..warning: As this function is cached, make sure to avoid modifying the returned dictionary,
        as that will directly modify the stored version in the cache, leading to future calls
        with the same arguments returning a wrong (modified) version of this dictionary.
    """
    module = importlib.import_module(MODULE_PATHS[state])

    if direction is PacketDirection.SERVERBOUND:
        direction_class = ServerBoundPacket
    elif direction is PacketDirection.CLIENTBOUND:
        direction_class = ClientBoundPacket
    else:
        raise ValueError("Unrecognized packet direction")

    packet_map: dict[int, type[Packet]] = {}

    for submodule in _walk_submodules(module):
        for packet_class in _walk_module_packets(submodule):
            if issubclass(packet_class, direction_class):
                packet_map[packet_class.PACKET_ID] = packet_class

    return packet_map
