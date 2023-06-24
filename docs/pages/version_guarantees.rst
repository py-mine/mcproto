Version Guarantees
==================

.. attention::
   Mcproto is currently in the pre-release phase (pre v1.0.0). During this phase, these guarantees will NOT be
   followed! This means that **breaking changes can occur in minor version bumps**, though micro version bumps are
   still strictly for bugfixes, and will not include any features or breaking changes.

This library follows `semantic versioning model <https:semver.org>`_, which means the major version is updated every
time there is an incompatible (breaking) change made to the public API. However due to the fairly dynamic nature of
Python, it can be hard to discern what can be considered a breaking change, and what isn't.

First thing to keep in mind is that breaking changes only apply to **publicly documented functions and classes**. If
it's not listed in the documentation here, it's an internal feature, that isn't considered a part of the public API,
and thus is bound to change. This includes documented attributes that start with an underscore.

.. note::
   The examples below are non-exhaustive.

Examples of Breaking Changes
----------------------------

* Changing the default parameter value of a function to something else.
* Renaming (or removing) a function without an alias to the old function.
* Adding or removing parameters of a function.
* Removing deprecated alias to a renamed function

Examples of Non-Breaking Changes
--------------------------------

* Changing function's name, while providing a deprecated alias.
* Renaming (or removing) private underscored attributes.
* Adding an element into `__slots__` of a data class.
* Changing the behavior of a function to fix a bug.
* Changes in the typing behavior of the library.
* Changes in the documentation.
* Modifying the internal protocol connection handling.
* Updating the dependencies to a newer version, major or otherwise.
