from __future__ import annotations

import importlib
import pkgutil
import warnings
from abc import ABC, abstractmethod
from collections.abc import Hashable, Iterator, Sequence
from types import ModuleType
from typing import Any, ClassVar, Generic, NamedTuple, NoReturn, TYPE_CHECKING, TypeVar

from mcproto.utils.abc import RequiredParamsABCMixin

if TYPE_CHECKING:
    from typing_extensions import TypeGuard

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")

__all__ = ["VersionMap", "WalkableModuleData"]


class WalkableModuleData(NamedTuple):
    module: ModuleType
    info: pkgutil.ModuleInfo
    member_names: Sequence[str]


class VersionMap(ABC, RequiredParamsABCMixin, Generic[K, V]):
    """Base class for map classes that allow obtaining versioned implementations for same components.

    Some components (classes) need to be versioned as they might change between different protocol
    versions. VersionMap classes are responsible for finding the implementation for given component
    that matches the requested version for.

    If the exact requested version is not found, the closest older/lesser version will be used instead,
    however as this might cause issues, a user warning will be produced alongside this happening.

    NOTE: If you need typed implementations, you are advised to instead import the versioned class
    directly, as due to the dynamic nature of this map, and the changing nature of the versioned
    implementations, no type information can be provided here.

    WARNING: You are not expected to initialize these mapping classes! That should be left for the
    library to handle and provide a map for each individual versioned components.
    """

    # TODO: Describe the obtain key, lazy loading and preload_all in init

    # TODO: Look into generating stubs somehow to preserve the type information even with how
    # dynamic this class is. (Could require making this class generic over a literal int, being
    # the version).

    _REQUIRED_CLASS_VARS: ClassVar[Sequence[str]] = [
        "SUPPORTED_VERSIONS",
        "_SEARCH_DIR_QUALNAME",
        "COMPATIBLE_FALLBACK_VERSIONS",
    ]

    SUPPORTED_VERSIONS: ClassVar[set[int]]
    COMPATIBLE_FALLBACK_VERSIONS: ClassVar[set[int]]
    _SEARCH_DIR_QUALNAME: ClassVar[str]

    __slots__ = ("_version_map",)

    def __init__(self, preload_all: bool = False):
        self._version_map: dict[int, dict[K, V]] = {}

        if preload_all:
            for version in self.SUPPORTED_VERSIONS:
                self.load_version(version)

    def load_version(self, protocol_version: int) -> None:
        """Load all components for given protocol version."""
        for key, member in self._walk_valid_components(protocol_version):
            dct = self._version_map.setdefault(protocol_version, {})

            if key in dct:
                raise ValueError(f"Value {member} already registered (key collision: {key})")

            dct[key] = member

    def obtain(self, protocol_version: int, key: K) -> V:
        """Obtain component for given protocol version, that matches the obtain key."""
        protocol_version = self._get_supported_protocol_version(protocol_version)

        # Lazy loading: if this protocol version isn't in the version map, it wasn't yet loaded, do so now.
        if protocol_version not in self._version_map:
            self.load_version(protocol_version)

        return self._version_map[protocol_version][key]

    def make_version_map(self, protocol_version: int) -> dict[K, V]:
        """Construct a dictionary mapping (obtain key -> value) for values of given protocol version."""
        protocol_version = self._get_supported_protocol_version(protocol_version)

        # Lazy loading: if this protocol version isn't in the version map, it wasn't yet loaded, do so now.
        if protocol_version not in self._version_map:
            self.load_version(protocol_version)

        return self._version_map[protocol_version].copy()

    @abstractmethod
    def _check_obj(
        self, obj: Any, module_data: WalkableModuleData, protocol_version: int  # noqa: ANN401
    ) -> TypeGuard[V]:
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
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _make_obtain_key(cls, obj: V, module_data: WalkableModuleData, protocol_version: int) -> K:
        """Construct a unique obtain key for given object under given protocol version.


        Note: While the protocol version might be beneficial to know when constructing
        the obtain key, it shouldn't be used directly as a part of the key, as the items
        will already be split by their protocol versions, and this version will be known
        at obtaining time.
        """
        raise NotImplementedError

    @classmethod
    def _get_package_module(cls, protocol_version: int) -> ModuleType:
        """Obtain the package module containing all components specific to given protocol version.

        This relies on the _SEARCH_DIR_QUALNAME and naming scheme of v{protocol_version} for the modules.
        """
        module_name = f"{cls._SEARCH_DIR_QUALNAME}.v{protocol_version}"
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            raise ValueError(
                f"Protocol version ({protocol_version}) isn't supported, yet it was listed as supported. Report this!"
            ) from exc

        return module

    @classmethod
    def _walk_submodules(cls, module: ModuleType) -> Iterator[WalkableModuleData]:
        """Go over all submodules of given module, that properly specify __all__.

        The yielded modules are expected to contain the versioned component items.

        If a submodule that doesn't define __all__ is present, it will be skipped, as we don't
        consider it walkable. (Walking over all variables defined in this module isn't viable,
        since it would include imports etc. making defining __all__ a requirement.)
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

    @classmethod
    def _walk_members(cls, module_data: WalkableModuleData) -> Iterator[object]:
        """Go over all members specified in __all__ of given walkable (sub)module.

        Yields all
        """
        for member_name in module_data.member_names:
            try:
                member = getattr(module_data.module, member_name)
            except AttributeError as exc:
                module_name = module_data.info.name
                raise TypeError(f"Member {member_name!r} of {module_name!r} module isn't defined.") from exc

            yield member

    def _walk_valid_components(self, protocol_version: int) -> Iterator[tuple[K, V]]:
        """Go over all components/members belonging to given protocol version."""
        version_module = self._get_package_module(protocol_version)
        for module_data in self._walk_submodules(version_module):
            for member in self._walk_members(module_data):
                if self._check_obj(member, module_data, protocol_version):
                    key = self._make_obtain_key(member, module_data, protocol_version)
                    yield key, member

    def _get_supported_protocol_version(self, protocol_version: int) -> int:
        """Given a protocol version, return closest older supported version, or the version itself.

        - If given protocol version is one of supported versions, this function will simply return it.
        - Otherwise, search for the closest older version to the requested version
            - If there is no older version in the supported version, ValueError is raised
            - If the requested version is in COMPATIBLE_FALLBACK_VERSIONS, this fallback will be
              considered safe, and no errors/warnings will be produced.
            - Otherwise, the closest version will still be returned, but a UserWarning will be emitted
              mentioning that this fallback occurred and that the version might not be fully compatible.
        """

        if protocol_version in self.SUPPORTED_VERSIONS:
            return protocol_version

        # Pick the most recent, but older version to the one that was requested
        older_versions = filter(lambda version: version < protocol_version, self.SUPPORTED_VERSIONS)
        try:
            protocol_version_closest = max(older_versions)
        except ValueError as exc:  # No older protocol version found
            raise ValueError(
                f"Requested protocol version ({protocol_version}) isn't supported"
                ", and no older version to fall back to was found."
            ) from exc

        # Since using an older/lesser version to the one that was requested is a fallback behavior and
        # could easily cause issues, emit a warning here, unless the version was explicitly marked compatible.
        if protocol_version not in self.COMPATIBLE_FALLBACK_VERSIONS:
            warnings.warn(
                f"Falling back to older protocol version {protocol_version_closest}, "
                f"as the requested version ({protocol_version}) isn't supported.",
                category=UserWarning,
            )

        return protocol_version_closest
