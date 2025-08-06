## Version 0.6.0 (2025-08-06)

### Breaking Changes

- [#421](https://github.com/py-mine/mcproto/issues/421): Drop support for Python 3.8 ([EOL since 2024-09-06](https://peps.python.org/pep-0569/))

### Features

- [#209](https://github.com/py-mine/mcproto/issues/209): Added `InvalidPacketContentError` exception, raised when deserializing of a specific packet fails. This error inherits from `IOError`, making it backwards compatible with the original implementation.
- [#257](https://github.com/py-mine/mcproto/issues/257): Added the `NBTag` to deal with NBT data
    - The `NBTag` class is the base class for all NBT tags and provides the basic functionality to serialize and deserialize NBT data from and to a `Buffer` object.
    - The classes `EndNBT`, `ByteNBT`, `ShortNBT`, `IntNBT`, `LongNBT`, `FloatNBT`, `DoubleNBT`, `ByteArrayNBT`, `StringNBT`, `ListNBT`, `CompoundNBT`, `IntArrayNBT`and `LongArrayNBT` were added and correspond to the NBT types described in the [NBT specification](https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/NBT).
    - NBT tags can be created using the `NBTag.from_object()` method and a schema that describes the NBT tag structure.
      Compound tags are represented as dictionaries, list tags as lists, and primitive tags as their respective Python types.
      The implementation allows to add custom classes to the schema to handle custom NBT tags if they inherit the `:class: NBTagConvertible` class.
    - The `NBTag.to_object()` method can be used to convert an NBT tag back to a Python object. Use include_schema=True to include the schema in the output, and `include_name=True` to include the name of the tag in the output. In that case the output will be a dictionary with a single key that is the name of the tag and the value is the object representation of the tag.
    - The `NBTag.serialize()` can be used to serialize an NBT tag to a new `Buffer` object.
    - The `NBTag.deserialize(buffer)` can be used to deserialize an NBT tag from a `Buffer` object.
    - If the buffer already exists, the `NBTag.write_to(buffer, with_type=True, with_name=True)` method can be used to write the NBT tag to the buffer (and in that case with the type and name in the right format).
    - The `NBTag.read_from(buffer, with_type=True, with_name=True)` method can be used to read an NBT tag from the buffer (and in that case with the type and name in the right format).
    - The `NBTag.value` property can be used to get the value of the NBT tag as a Python object.
- [#476](https://github.com/py-mine/mcproto/issues/476): Added `LoginAcknowledged` packet implementation
- Added further encryption related fucntions used by servers.
- Update `LoginStart` packet to latest protocol version (`uuid` no longer optional)

### Bugfixes

- [#330](https://github.com/py-mine/mcproto/issues/330): Fix behavior of the `mcproto.utils.deprecation` module, which was incorrectly always using a fallback version, assuming mcproto is at version 0.0.0. This then could've meant that using a deprecated feature that is past the specified deprecation (removal) version still only resulted in a deprecation warning, as opposed to a full runtime error.
- [#427](https://github.com/py-mine/mcproto/issues/427): Fix version comparisons in deprecated functions for PEP440, non-semver compatible versions

### Documentation Improvements

- [#179](https://github.com/py-mine/mcproto/issues/179): Enforce presence of docstrings everywhere with pydocstyle. This also adds docstring to all functions and classes that didn't already have one. Minor improvements for consistency were also made to some existing docstrings.
- [#346](https://github.com/py-mine/mcproto/issues/346): Complete documentation rewrite
- Add protocol and protocol pages (API reference docs)

### Internal Changes

- [#131](https://github.com/py-mine/mcproto/issues/131): Any overridden methods in any classes now have to explicitly use the `typing.override` decorator (see [PEP 698](https://peps.python.org/pep-0698/))
- [#258](https://github.com/py-mine/mcproto/issues/258): Fix readthedocs CI
- [#259](https://github.com/py-mine/mcproto/issues/259): Merge dependabot PRs automatically, if they pass all CI checks.
- [#274](https://github.com/py-mine/mcproto/issues/274): Update ruff
    - Update ruff version (the version we used was very outdated)
    - Drop isort in favor of ruff's built-in isort module in the linter
    - Drop black in favor of ruff's new built-in formatter
    - Update ruff settings, including adding/enabling some new rule-sets
- [#285](https://github.com/py-mine/mcproto/issues/285): Add `gen_serializable_test` function to generate tests for serializable classes, covering serialization, deserialization, validation, and error handling.
- [#285](https://github.com/py-mine/mcproto/issues/285): Rework the `Serializable` class
- [#286](https://github.com/py-mine/mcproto/issues/286): Update the docstring formatting directive in CONTRIBUTING.md to reflect the formatting practices currently in place.
- [#300](https://github.com/py-mine/mcproto/issues/300): Update CI
    - Fix CI not running unit tests on python 3.8 (only 3.11)
    - Update to use python 3.12 (in validation and as one of the matrix versions in unit-tests workflow)
    - Trigger and run lint and unit-tests workflows form a single main CI workflow.
    - Only send status embed after the main CI workflow finishes (not for both unit-tests and validation)
    - Use `--output-format=github` for `ruff check` in the validation workflow
    - Fix the status-embed workflow
- [#323](https://github.com/py-mine/mcproto/issues/323): Enable various other ruff rules as a part of switching to blacklist model, where we explicitly disable the rules we don't want, rather than enabling dozens of rule groups individually.
- [#329](https://github.com/py-mine/mcproto/issues/329): - Change the type-checker from `pyright` to `basedpyright`
    - BasedPyright is a fork of pyright, which provides some additional typing features and re-implements various proprietary features from the closed-source Pylance vscode extension.
    - Overall, it is very similar to pyright with some bonus stuff on top. However, it does mean all contributors who want proper editor support for the project will need to update their editor settings and add basedpyright. The instructions on how to do this are described in the updated `CONTRIBUTING.md`.
- [#331](https://github.com/py-mine/mcproto/issues/331): Add `.editorconfig` file, defining some basic configuration for the project, which editors can automatically pick up on (i.e. indent size).
- [#332](https://github.com/py-mine/mcproto/issues/332): Enable various other (based)pyright rules (in fact, switch to a black-list, having all rules enabled except those explicitly disabled). This introduces a much stricter type checking behavior into the code-base.
- [#347](https://github.com/py-mine/mcproto/issues/347): Fix towncrier after an update (template file isn't ignored by default, so ignore it manually)
- [#379](https://github.com/py-mine/mcproto/issues/379): Remove codeclimate
- [#395](https://github.com/py-mine/mcproto/issues/395): Add CI workflow for marking inactive issues (>60 days) with the stale label
- [#421](https://github.com/py-mine/mcproto/issues/421): Add support for python 3.13, moving the CI to test against it.
- [#493](https://github.com/py-mine/mcproto/issues/493): Change our primary dependency management tool from `poetry` to `uv`
- [#497](https://github.com/py-mine/mcproto/issues/497): Add changelog-this poe task
- [#498](https://github.com/py-mine/mcproto/issues/498): Drop [repo-sync/pull-request](https://github.com/repo-sync/pull-request) action in favor of GitHub CLI

---

## Version 0.5.0 (2023-08-10)

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

_The changelog was added during development of 0.2.0, so nothing prior is documented here. Try checking the GitHub
releases, or git commit history directly._
