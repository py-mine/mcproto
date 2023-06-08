## Version 0.3.0 (2023-06-08)

### Features

- [#54](https://github.com/py-mine/mcproto/issues/54): Add support for LOGIN state packets
  - `LoginStart`
  - `LoginEncryptionRequest`
  - `LoginEncryptionResponse`
  - `LoginSuccess`
  - `LoginDisconnect`
  - `LoginPluginRequest`
  - `LoginPluginResponse`
  - `LoginSetCompression`

### Bugfixes

- [#75](https://github.com/py-mine/mcproto/issues/75): Increase the stack level of warnings shown on protocol version fallbacks
- [#113](https://github.com/py-mine/mcproto/issues/113): TCP connections now properly shut down the connection gracefully (TCP FIN)

### Documentation Improvements

- [#2](https://github.com/py-mine/mcproto/issues/2): Add Sphinx and basic docs layout
- [#18](https://github.com/py-mine/mcproto/issues/18): Rewrite all docstrings into proper Sphinx format, instead of using markdown.
- [#27](https://github.com/py-mine/mcproto/issues/27): Add changelog page to docs, linking `CHANGELOG.md`, including unreleased changes from fragments.
- [#28](https://github.com/py-mine/mcproto/issues/28): Use furo theme for the documentation
- [#34](https://github.com/py-mine/mcproto/issues/34): Add version guarantees page
- [#40](https://github.com/py-mine/mcproto/issues/40): Move code of conduct to the docs.
- Improve readability of the changelog readme (changes/README.md)
   - Mention taskipy `changelog-preview` shorthand command
   - Add category headers splitting things up, for better readability
   - Explain how to express multiple changes related to a single goal in a changelog fragment.
- Include `CHANGELOG.md` file in project's distribution files.

### Internal Changes

- [#12](https://github.com/py-mine/mcproto/issues/12): Replace HassanAbouelela setup-python action with ItsDrike/setup-python in CI workflows
- [#17](https://github.com/py-mine/mcproto/issues/17): Start using codeclimate to monitor code coverage and it's changes
- [#35](https://github.com/py-mine/mcproto/issues/35): Add more tests
- [#38](https://github.com/py-mine/mcproto/issues/38): Replace our implementation of `SemanticVersion` with a community-maintained `semantic-version` package.
- [#53](https://github.com/py-mine/mcproto/issues/53): Mark all packet classes as `typing.final`, making the type-checker enforce existence of concrete implementations for all abstract methods.
- [#112](https://github.com/py-mine/mcproto/issues/112): Removed `codespell` linter. This proved too annoying, especially when we already have a lot of linters here. Spelling mistakes can simply be caught in the review process.
- [#114](https://github.com/py-mine/mcproto/issues/114): Use latest poetry version in CI workflows (remove version lock - at 1.3.1)
- The `documentation` category of changelog was renamed to shorter `docs`

---


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
