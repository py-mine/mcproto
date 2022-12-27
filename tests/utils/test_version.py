from __future__ import annotations

import operator as op
from collections.abc import Callable
from typing import NamedTuple, Optional

import pytest

from mcproto.utils.version import SemanticVersion


class VersionTuple(NamedTuple):
    major: int
    minor: int
    patch: int
    prerelease: Optional[tuple[str, ...]]
    build_metadata: Optional[tuple[str, ...]]


@pytest.mark.parametrize(
    "version_string,version_result",
    (
        ("0.0.1", VersionTuple(0, 0, 1, None, None)),
        ("1.0.0", VersionTuple(1, 0, 0, None, None)),
        ("2.8.6", VersionTuple(2, 8, 6, None, None)),
        ("1.0.0-alpha.1", VersionTuple(1, 0, 0, ("alpha", "1"), None)),
        ("1.0.0-0.1.2", VersionTuple(1, 0, 0, ("0", "1", "2"), None)),
        ("1.0.0+001", VersionTuple(1, 0, 0, None, ("001",))),
        ("1.0.0+exp.sha.51182", VersionTuple(1, 0, 0, None, ("exp", "sha", "51182"))),
        ("1.0.0-alpha.2+sha.ab511", VersionTuple(1, 0, 0, ("alpha", "2"), ("sha", "ab511"))),
    ),
)
def test_version_parsing(version_string: str, version_result: VersionTuple):
    ver = SemanticVersion.from_string(version_string)
    assert ver.major == version_result.major
    assert ver.minor == version_result.minor
    assert ver.patch == version_result.patch
    assert ver.prerelease == version_result.prerelease
    assert ver.build_metadata == version_result.build_metadata


@pytest.mark.parametrize(
    "version_string",
    ("v1.0.1", "abc", "hello there", "I'm invalid!"),
)
def test_invalid_version_parsing(version_string: str):
    with pytest.raises(ValueError):
        SemanticVersion.from_string(version_string)


@pytest.mark.parametrize(
    "version1,version2,operator",
    (
        # Major, Minor, Patch precedenced
        ("1.0.0", "2.0.0", op.lt),
        ("2.0.0", "2.1.0", op.lt),
        ("2.1.0", "2.1.1", op.lt),
        ("2.0.1", "10.0.0", op.lt),
        # pre release of next version has higher precedence to previous version,
        # however pre-release of same version has lower precedence to full version.
        ("2.1.1", "2.1.2-alpha", op.lt),
        ("2.1.2-alpha", "2.1.2", op.lt),
        # With same major, minor and patch version, pre-releases comparisons are done based on these rules:
        #  - Identifiers consisting of only digits are compared numerically.
        #  - Identifiers with letters or hyphens are compared lexically in ASCII sort order.
        #  - Numeric identifiers always have lower precedence than non-numeric identifiers.
        #  - A larger set of pre-release fields has a higher precedence than a smaller set,
        #    if all of the preceding identifiers are equal
        ("3.0.0-1", "3.0.0-2", op.lt),
        ("3.0.0-2", "3.0.0-10", op.lt),
        ("3.0.0-a", "3.0.0-b", op.lt),
        ("3.0.0-aa", "3.0.0-ab", op.lt),
        ("3.0.0-9", "3.0.0-a", op.lt),
        ("3.0.0-1", "3.0.0-1.0", op.lt),
        # Build numbers are ignored in comparisons and versions are treated equally
        ("4.0.0+sha.636fc3455", "4.0.0", op.eq),
        ("4.0.0+sha.636fc3455", "4.0.0+sha.636fc3455", op.eq),
        ("4.0.0+sha.636fc3455", "4.0.0+sha.480a8de90", op.eq),
        ("4.0.0+sha.636fc3455", "4.0.0+dev.1", op.eq),
        ("4.0.0-alpha.1+sha.636fc3455", "4.0.0-alpha.1+dev.1", op.eq),
        # Comparing equal versions
        ("1.0.0", "1.0.0", op.eq),
        ("1.2.1", "1.2.1", op.eq),
        ("2.0.1-alpha.1", "2.0.1-alpha.1", op.eq),
        ("2.1.1-a.b.10.c", "2.1.1-a.b.10.c", op.eq),
    ),
)
def test_version_comparison(version1: str, version2: str, operator: Callable[[object, object], bool]):
    ver1 = SemanticVersion.from_string(version1)
    ver2 = SemanticVersion.from_string(version2)
    assert operator(ver1, ver2)

    # Make sure that greater than also works (reversed lt)
    if operator is op.lt:
        assert op.gt(ver2, ver1)

    # Vice-versa
    if operator is op.gt:
        assert op.lt(ver2, ver1)

    # If versions are different (less that/greater than), equality can't pass
    if operator is op.lt or operator is op.gt:
        assert not op.eq(ver1, ver2)
        assert op.ne(ver1, ver2)

    # If versions are equal, less than/greater than/not equal can't pass
    if operator is op.eq:
        assert not op.lt(ver1, ver2)
        assert not op.gt(ver1, ver2)
        assert not op.ne(ver1, ver2)

    # >= must pass if operator was eq or gt
    if operator is op.eq or operator is op.gt:
        assert op.ge(ver1, ver2)

    # <= must pass if operator was eq or lt
    if operator is op.eq or operator is op.lt:
        assert op.le(ver1, ver2)
