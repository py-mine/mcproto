from __future__ import annotations

import importlib
import pkgutil
import warnings
from abc import ABC, abstractmethod
from collections.abc import Hashable, Iterator, Sequence
from types import ModuleType
from typing import Any, ClassVar, Generic, NamedTuple, NoReturn, TypeVar

from typing_extensions import TypeGuard

from mcproto.utils.abc import RequiredParamsABCMixin

__all__ = ["VersionMap", "WalkableModuleData"]

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


class WalkableModuleData(NamedTuple):
    module: ModuleType
    info: pkgutil.ModuleInfo
    member_names: Sequence[str]


class VersionMap(ABC, RequiredParamsABCMixin, Generic[K, V]):
    """Base class for map classes that allow obtaining versioned implementations for same components.

    Some components (classes, functions, constants, ...) need to be versioned as they might change
    between different protocol versions. :class:`.VersionMap` classes are responsible for finding the
    implementation for given component that matches the requested version for.

    If the exact requested version is not found, the closest older/lesser version will be used instead,
    however as this might cause issues, a user warning will be produced alongside this happening.

    .. note:
        If you need typed implementations, you should import the versioned components directly, as due
        to the dynamic nature of this map, and the changing nature of the versioned implementations,
        no type information can be provided here.

    .. warning:
        You are not expected to initialize these mapping classes yourself! That should be left for
        the library to handle and provide a map for each individual versioned components.
    """

    # TODO: Look into generating stubs somehow to preserve the type information even with how
    # dynamic this class is. (Could require making this class generic over a literal int, being
    # the version).

    _REQUIRED_CLASS_VARS: ClassVar[Sequence[str]] = [
        "SUPPORTED_VERSIONS",
        "_SEARCH_DIR_QUALNAME",
        "COMPATIBLE_FALLBACK_VERSIONS",
    ]

    #: Set of all versions that have complete implementations, with package for the version
    SUPPORTED_VERSIONS: ClassVar[set[int]]
    #: Set of all versions that are fully compatible with an older supported version that they safely fall back to
    COMPATIBLE_FALLBACK_VERSIONS: ClassVar[set[int]]
    #: Fully qualified name of the package, containing individual versioned packages
    _SEARCH_DIR_QUALNAME: ClassVar[str]

    __slots__ = ("_version_map",)

    def __init__(self, preload_all: bool = False):
        """
        :param preload_all:
            By default, the individual versioned components are loaded lazily, once requested.
            However if this is set to ``True``, the components from all :attr:`.SUPPORTED_VERSIONS`
            will all get loaded on initialization.
        """
        self._version_map: dict[int, dict[K, V]] = {}

        if preload_all:
            for version in self.SUPPORTED_VERSIONS:
                self.load_version(version)

    def load_version(self, protocol_version: int) -> None:
        """Load all components for given protocol version.

        Go through all versioned components found for the requested version (from all submodules in the
        package for given version.) and store them into an internal version map. Each component is stored
        under it's corresponding obtain key.

        :raises ValueError:
            Raised if a key collision occurs (obtain key of multiple distinct versioned components is the same).
        """
        for key, member in self._walk_valid_components(protocol_version):
            dct = self._version_map.setdefault(protocol_version, {})

            if key in dct:
                raise ValueError(f"Value {member} already registered (key collision: {key})")

            dct[key] = member

    def obtain(self, protocol_version: int, key: K) -> V:
        """Obtain component for given protocol version, that matches the obtain key.

        This function works lazily, and only loads the required components for given ``protocol_version``
        if they're not already loaded. If loading does occr, the requested version is stored internally
        and will simply be accessed next time this function is called with the same ``protocol_version``.

        Once loaded, a versioned component that matches the given obtain ``key`` is returned.

        .. note:
            If given ``protocol_version`` isn't supported, a fallback version is picked
            (see: :meth:`._get_supported_protocol_version`).
        """
        protocol_version = self._get_supported_protocol_version(protocol_version)

        # Lazy loading: if this protocol version isn't in the version map, it wasn't yet loaded, do so now.
        if protocol_version not in self._version_map:
            self.load_version(protocol_version)

        return self._version_map[protocol_version][key]

    def make_version_map(self, protocol_version: int) -> dict[K, V]:
        """Obtain a dictionary mapping of obtain key -> versioned component, with all components for given version.

        This function works lazily, and only loads the required components for given ``protocol_version``
        if they're not already loaded. If loading does occur, the requested version is stored internally and
        will simply be accessed next time this function is called with the same ``protocol_version``.

        The returned dictionary is a copy of the internal one, as we don't want the user to be able to modify it.

        .. note:
            If given ``protocol_version`` isn't supported, a fallback version is picked
            (see: :meth:`._get_supported_protocol_version`).
        """
        protocol_version = self._get_supported_protocol_version(protocol_version)

        # Lazy loading: if this protocol version isn't in the version map, it wasn't yet loaded, do so now.
        if protocol_version not in self._version_map:
            self.load_version(protocol_version)

        return self._version_map[protocol_version].copy()

    @abstractmethod
    def _check_obj(
        self,
        obj: Any,  # noqa: ANN401
        module_data: WalkableModuleData,
        protocol_version: int,
    ) -> TypeGuard[V]:
        """Determine whether a member object should be considered as a valid component for given protocol version.

        When versioned components are obtained, all of the members listed in any module's ``__all__`` are
        considered. This function serves as a filter, identifying whether a potential member object should be
        considered as one of the versioned components.

        .. note:
            This function shouldn't include any checks on whether an object is already registered in the version
            map (key collisions), these are handled during the collection in :meth:`.load_version`, all this
            function is responsible for is checking whether this object is a valid component, components with
            conflicting keys are still considered valid here, as they're handled elsewhere.

            However if there is some additional data that needs to be unique for a component to be valid, which
            wouldn't be caught as a key collision, this function can raise a :exc:`ValueError`.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _make_obtain_key(cls, obj: V, module_data: WalkableModuleData, protocol_version: int) -> K:
        """Construct a unique obtain key for given versioned component (``obj``) under given ``protocol_version``.

        .. note:
            While the protocol version might be beneficial to know when constructing
            the obtain key, it shouldn't be used directly as a part of the key, as the items
            will already be split by their protocol versions, and this version will be known
            at obtaining time.
        """
        raise NotImplementedError

    @classmethod
    def _get_package_module(cls, protocol_version: int) -> ModuleType:
        """Obtain the package module containing all components specific to given protocol version.

        This relies on the :attr:`._SEARCH_DIR_QUALNAME` class variable, and naming scheme of
        v{protocol_version} for the modules contained in this directory.
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
        """Go over all submodules of given module, that specify ``__all__``.

        The yielded modules are expected to contain the versioned component items.

        If a submodule that doesn't define ``__all__`` is present, it will be skipped, as we don't
        consider it walkable. (Walking over all variables defined in this module isn't viable,
        since it would include imports etc. making defining ``__all__`` a requirement.)
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
        """Go over all members specified in ``__all__`` of given walkable (sub)module.

        :return:
            Iterator yielding every object defined in ``__all__`` of given module. These objects
            are obtained directly using ``getattr`` from the imported module.

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

            yield member

    def _walk_valid_components(self, protocol_version: int) -> Iterator[tuple[K, V]]:
        """Go over all components/members belonging to given protocol version.

        This method walks over all submodules in the versioned module (see: :meth:`._get_package_module`),
        in which we go over all members present in ``__all__`` of this submodule (see :meth:`._walk_submodules`),
        after which a :meth:`_check_obj` check is performed, ensuring the obtained member/component is one that
        should be versioned.

        :return:
            A tuple containing the obtain key (see: :meth:`._make_obtain_key`), and the versioned component/member.
        """
        version_module = self._get_package_module(protocol_version)
        for module_data in self._walk_submodules(version_module):
            for member in self._walk_members(module_data):
                if self._check_obj(member, module_data, protocol_version):
                    key = self._make_obtain_key(member, module_data, protocol_version)
                    yield key, member

    def _get_supported_protocol_version(self, protocol_version: int) -> int:
        """Given a ``protocol_version``, return closest older supported version, or the version itself.

        * If given ``protocol_version`` is one of :attr:`.SUPPORTED_VERSIONS`, return it.
        * Otherwise, search for the closest older supported version to the provided ``protocol_version``.
            * If there is no older version in the supported version, :exc:`ValueError` is raised
            * If the requested version is in :attr:`.COMPATIBLE_FALLBACK_VERSIONS`, this fallback will be
              considered safe, and no errors/warnings will be produced.
            * Otherwise, the closest version will still be returned, but a :exc:`UserWarning` will be emitted
              mentioning that this fallback occurred and that the version might not be fully compatible.

        :raises ValueError:
            The requested version isn't supported, and there is no supported older version to fallback to.
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
                stacklevel=3,
            )

        return protocol_version_closest
