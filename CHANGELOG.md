## Version 0.2.0 (2022-12-30)

### Features

- [#14](https://github.com/py-mine/mcproto/issues/14): Add `__slots__` to most classes in the project
      - All connection classes are now slotted
      - Classes in `mcproto.utils.abc` are now slotted
- Separate packet interaction functions into `mcproto.packets.interactions`, (though they're reexported in
  `mcproto.packets`, so no breaking changes)

### Bugfixes

- [#14](https://github.com/py-mine/mcproto/issues/14): Add missing `__slots__` to `ServerBoundPacket` and `ClientBoundPacket` subclasses, which inherited from slotted
  `Packet`, but didn't themselves define `__slots__`, causing `__dict__` to be needlessly created.
- The error message produced by `RequiredParamsABCMixin` class when a required no MRO class variable isn't present now
  includes a previously missing space, making it more readable.

### Documentation Improvements

- [#7](https://github.com/py-mine/mcproto/issues/7): Add and start keeping a changelog, managed by towncrier.
- [#13](https://github.com/py-mine/mcproto/issues/13): Add a security policy.

### Internal Changes

- [#6](https://github.com/py-mine/mcproto/issues/6): Rework deprecation system
  - Drop support for date-based deprecations, versions work better
  - Provide `deprecation_warn` function, which emits warnings directly, no need for a decorator
  - Add a `SemanticVersion` class, supporting version comparisons
  - If the project's version is already higher than the specified deprecation removal version, raise a DeprecationWarning
    as a full exception (rather than just a warning).
- [#7](https://github.com/py-mine/mcproto/issues/7): Add towncrier for managing changelog
- [#14](https://github.com/py-mine/mcproto/issues/14): Add slotscheck, ensuring `__slots__` are defined properly everywhere.
- [#14](https://github.com/py-mine/mcproto/issues/14): Make `typing-extensions` a runtime dependency and use it directly, don't rely on `if typing.TYPE_CHECKING` blocks.
- [#15](https://github.com/py-mine/mcproto/issues/15): Add codespell tool, to automatically find spelling mistakes.
- Add README file into the `tests/` folder, explaining how we use unit-tests and some basics of testing.
- Add `CustomMockMixin` internal class, inheriting from `UnpropagatingMockMixin`, but also allowing to use `spec_set` as
  class variable, as it will automatically pass it into `__init__` of the mock class.
- Add several new flake8 extensions, and rework flake8 config file
- Add support for specifying what child mock type to propagate in `UnpropagatingMockMixin` class (for unit-tests).

---

*The changelog was added during development of 0.2.0, so nothing prior is documented here. Try checking the GitHub
releases, or git commit history directly.*
