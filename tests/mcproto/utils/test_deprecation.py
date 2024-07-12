from __future__ import annotations

import importlib.metadata
import warnings
from functools import wraps

import pytest

from mcproto.utils.deprecation import deprecated, deprecation_warn


def _patch_project_version(monkeypatch: pytest.MonkeyPatch, version: str | None):
    """Patch the project version reported by importlib.metadata.version.

    This is used to simulate different project versions for testing purposes.
    If ``version`` is ``None``, a :exc:`~importlib.metadata.PackageNotFoundError` will be raised
    when trying to get the project version.
    """
    orig_version_func = importlib.metadata.version

    @wraps(orig_version_func)
    def patched_version_func(distribution_name: str) -> str:
        if distribution_name == "mcproto":
            if version is None:
                raise importlib.metadata.PackageNotFoundError
            return version
        return orig_version_func(distribution_name)

    monkeypatch.setattr(importlib.metadata, "version", patched_version_func)


def test_deprecation_warn_produces_error(monkeypatch: pytest.MonkeyPatch):
    """Test deprecation_warn with older removal_version than current version produces exception."""
    _patch_project_version(monkeypatch, "1.0.0")

    with pytest.raises(DeprecationWarning, match="test"):
        deprecation_warn(obj_name="test", removal_version="0.9.0")


def test_deprecation_warn_produces_warning(monkeypatch: pytest.MonkeyPatch):
    """Test deprecation_warn with newer removal_version than current version produces warning."""
    _patch_project_version(monkeypatch, "1.0.0")

    with warnings.catch_warnings(record=True) as w:
        deprecation_warn(obj_name="test", removal_version="1.0.1")

    assert len(w) == 1
    assert issubclass(w[0].category, DeprecationWarning)
    assert "test" in str(w[0].message)


def test_deprecation_warn_unknown_version(monkeypatch: pytest.MonkeyPatch):
    """Test deprecation_warn with unknown mcproto version.

    This could occur if mcproto wasn't installed as a package. (e.g. when running directly from source,
    like via a git submodule.)
    """
    _patch_project_version(monkeypatch, None)

    with warnings.catch_warnings(record=True) as w:
        deprecation_warn(obj_name="test", removal_version="1.0.0")

    assert len(w) == 2
    assert issubclass(w[0].category, RuntimeWarning)
    assert "Failed to get mcproto project version" in str(w[0].message)
    assert issubclass(w[1].category, DeprecationWarning)
    assert "test" in str(w[1].message)


def test_deprecation_decorator(monkeypatch: pytest.MonkeyPatch):
    """Check deprecated decorator with newer removal_version than current version produces warning."""
    _patch_project_version(monkeypatch, "1.0.0")

    @deprecated(removal_version="1.0.1")
    def func(x: object) -> object:
        return x

    with warnings.catch_warnings(record=True) as w:
        assert func(5) == 5

    assert len(w) == 1
    assert issubclass(w[0].category, DeprecationWarning)
    assert "func" in str(w[0].message)
