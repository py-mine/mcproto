## Version 0.4.0 (2023-08-10)

### Breaking Changes

- [#130](https://github.com/py-mine/mcproto/issues/130): Renamed "shared_key" field to "shared_secret" in `LoginEncryptionPacket`, following the official terminology.

  - This is a breaking change, `LoginEncryptionPacket`'s `__init__` method now uses "shared_secret" keyword only argument, not "shared_key".
- [#130](https://github.com/py-mine/mcproto/issues/130): The `LoginStart` packet now contains a (required) UUID field (which can be explicitly set to `None`).
  - For some reason, this field was not added when the login packets were introduced initially, and while the UUID field can indeed be omitted in some cases (it is an optional filed), in vast majority of cases, it will be present, and we should absolutely support it.
  - As this is a new required field, the `__init__` function of `LoginStart` now also expects this `uuid` keyword argument to be present, making this a breaking change.
- [#159](https://github.com/py-mine/mcproto/issues/159): Fix packet compression handling in the interaction methods.

  This fixes a bug that didn't allow for specifying an exact compression threshold that the server specified in `LoginSetCompression` packet, and instead only allowing to toggle between compression on/off, which doesn't really work as server doesn't expect compression for packets below that threshold.

  - `sync_write_packet`, `async_write_pakcet`, `sync_read_packet` and `async_read_packet` functions now take `compression_threshold` instead of `compressed` bool flag
- [#161](https://github.com/py-mine/mcproto/issues/161): `LoginEncryptionRequest` now uses `cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey` to hold the public key, instead of just pure `bytes`. Encoding and decoding of this key happens automatically during serialize/deserialize. This is a breaking change for anyone relying on the `public_key` field from this packet being `bytes`, and for anyone initializing this packet directly with `__init__`, which now expects `RSAPublicKey` instance instead.

### Features

- [#129](https://github.com/py-mine/mcproto/issues/129): Added a system for handling Minecraft authentication
  - Yggdrasil system for unmigrated i.e. non-Microsoft accounts (supportng Minecraft accounts, and the really old Mojang accounts)
  - Microsoft OAuth2 system (Xbox live) for migrated i.e. Microsoft accounts
- [#160](https://github.com/py-mine/mcproto/issues/160): Re-export the packet classes (or any other objects) from the gamestate modules (`mcproto.packets.handshaking`/`mcproto.packets.login`/...) directly. Allowing simpler imports (`from mcproto.packets.login import LoginStart` instead of `from mcproto.packets.login.login import LoginStart`)
- [#161](https://github.com/py-mine/mcproto/issues/161): Add support for encryption. Connection classes now have `enable_encryption` method, and some encryption related functions were added into a new `mcproto.encryption` module.
- [#168](https://github.com/py-mine/mcproto/issues/168): Add multiplayer related functionalities for requesting and checking joins for original (bought) minecraft accounts. This allows us to join online servers.
- [#171](https://github.com/py-mine/mcproto/issues/171): Add `Account.check` function, to verify that the access token in use is valid, and the data the Account instance has matches the data minecraft API has.

### Bugfixes

- [#130](https://github.com/py-mine/mcproto/issues/130): `LoginEncryptionResponse` now includes the `server_id` field. This field was previously hard-coded to 20 spaces (blank value), which is what all minecraft clients on minecraft 1.7.x or higher do, however with older versions, this field is set to 20 random characters, which we should respect.
  - This is not a breaking change, as `server_id` will default to `None` in `LoginEncryptionResponse`'s `__init__`, meaning any existing code utilizing this packet will still work. It is purely an additional option.
- [#167](https://github.com/py-mine/mcproto/issues/167): Fix packet reading/writing when compression is enabled (use zlib as expected, instead of gzip which we were using before)
- [#170](https://github.com/py-mine/mcproto/issues/170): Preserve the call parameters and overloads in the typing signature of `mcproto.packets.packet_map.generate_packet_map` function. (This wasn't the case before, since `functools.lru_cache` doesn't preserve this data). Note that this loses on the typing information about the cache itself, as now it will appear to be a regular uncached function to the type-checker. We deemed this approach better to the alternative of no typing info for call arguments or overloads, but preserving cache info.

### Documentation Improvements

- [#129](https://github.com/py-mine/mcproto/issues/129): Mention lack of synchronous alternatives for certain functions (see issue #128)
- [#139](https://github.com/py-mine/mcproto/issues/139): Add a warning in version guarantees page, explaining pre-release guarantees (breaking changes in minor versions allowed)
- [#141](https://github.com/py-mine/mcproto/issues/141): Move installation instructions from README to Installation docs page
- [#144](https://github.com/py-mine/mcproto/issues/144): Add attributetable internal sphinx extension for showing all attributes and methods for specified classes.

  - This adds `attributetable` sphinx directive, which can be used before autodoc directive. This will create the attribute table, which will get dynamically moved right below the class definition from autodoc (using javascript).
  - This extension was implemented by [discord.py](https://github.com/Rapptz/discord.py/blob/2fdbe59376d736483cd1226e674e609433877af4/docs/extensions/attributetable.py), this is just re-using that code, with some modifications to fit our code style and to fit the documentation design (furo theme).
- Updated contributing guidelines (restructure and rewrite some categories, to make it more readable)

### Internal Changes

- [#133](https://github.com/py-mine/mcproto/issues/133): Enable enforcement of some optional pyright rules
- [#153](https://github.com/py-mine/mcproto/issues/153): Replace flake8 linter with ruff (mostly equivalent, but much faster and configurable from pyproject.toml)
- [#154](https://github.com/py-mine/mcproto/issues/154): Enforce various new ruff linter rules:

  - **PGH:** pygrep-hooks (replaces pre-commit version)
  - **PL:** pylint (bunch of typing related linter rules)
  - **UP:** pyupgrade (forces use of the newest possible standards, depending on target version)
  - **RET:** flake8-return (various linter rules related to function returns)
  - **Q:** flake8-quotes (always use double quotes)
  - **ASYNC:** flake8-async (report blocking operations in async functions)
  - **INT:** flake-gettext (gettext related linting rules)
  - **PTH:** flake8-use-pathlib (always prefer pathlib alternatives to the os ones)
  - **RUF:** ruff custom rules (various additional rules created by the ruff linter team)

---


## Version 0.4.0 (2023-06-11)

### Breaking Changes

- [#41](https://github.com/py-mine/mcproto/issues/41): Rename `mcproto.packets.abc` to `mcproto.packets.packet`
- [#116](https://github.com/py-mine/mcproto/issues/116): Restructure the project, moving to a single protocol version model
  - This change does NOT have a deprecation period, and will very likely break most existing code-bases. However this change is necessary, as multi-version support was unsustainable (see issue #45 for more details)
  - Any packets and types will no longer be present in versioned folders (mcproto.packets.v757.xxx), but rather be directly in the parent directory (mcproto.packets.xxx).
  - This change doesn't affect manual communication with the server, connection, and basic IO writers/readers remain the same.

---


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
