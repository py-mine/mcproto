from __future__ import annotations

import importlib.metadata
import warnings

import pytest

from mcproto.utils.deprecation import deprecated, deprecation_warn


def test_deprecation_warn_produces_error(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(importlib.metadata, "version", lambda pkg: "1.0.0")
    with pytest.raises(DeprecationWarning, match="test"):
        deprecation_warn(obj_name="test", removal_version="0.9.0")


def test_deprecation_warn_produces_warning(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(importlib.metadata, "version", lambda pkg: "1.0.0")
    with warnings.catch_warnings(record=True) as w:
        deprecation_warn(obj_name="test", removal_version="1.0.1")
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "test" in str(w[-1].message)


def test_deprecation_decorator(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(importlib.metadata, "version", lambda pkg: "1.0.0")

    @deprecated(removal_version="1.0.1")
    def func(x):
        return x

    with warnings.catch_warnings(record=True) as w:
        assert func(5) == 5
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "func" in str(w[-1].message)
