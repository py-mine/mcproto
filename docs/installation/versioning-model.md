# Versioning Practices & Guarantees

!!! bug "Work In Progress"

    This page is missing an explanation on how to figure out which minecraft version a given mcproto version is for.
    This is because we currenly don't have any way to do so, once this will be decided on, it should be documented
    here.

!!! danger "Pre-release phase"

    Mcproto is currently in the pre-release phase (pre v1.0.0). During this phase, these guarantees will NOT be
    followed! This means that **breaking changes can occur in minor version bumps**. That said, micro version bumps are
    still strictly for bugfixes, and will not include any features or breaking changes.

This library follows [semantic versioning model](https://semver.org), which means the major version is updated every time
there is an incompatible (breaking) change made to the public API. In addition to semantic versioning, mcproto has
unique versioning practices related to new Minecraft releases.

## Versioning Model for Minecraft Releases

Mcproto aims to always be compatible with the **latest Minecraft protocol implementation**, updating the library as
soon as possible after each **full Minecraft release** (snapshots are not supported).

Typically, a new Minecraft release will result in a major version bump for mcproto, since protocol changes are often
breaking in nature. That said, it is not impossible for a new Minecraft release not to include breaking changes, in
this case, we will not perform this version bump.

However, there may be cases where we release a major version that does not correspond to a Minecraft update, depending
on the changes made in the library itself.

!!! info "Recap"

    - **Minecraft Updates**: When a new version of Minecraft is released and introduces breaking changes to the
        protocol, mcproto will increment its major version (e.g., from `1.x.x` to `2.0.0`).
    - **Non-breaking Protocol Changes**: If a Minecraft update introduces new features or protocol adjustments that do
        not break the existing public API, we may opt to release a minor version (e.g., from `1.0.x` to `1.1.0`).
    - **Non-protocol Major Releases**: Major releases may also happen due to significant internal changes or
        improvements in the library that are independent of Minecraft protocol updates.

!!! warning

    While mcproto strives to stay updated with Minecraft releases, this project is maintained by unpaid volunteers. We do
    our best to release updates in a timely manner after a new Minecraft version, but delays may occur.

## Examples of Breaking Changes

First thing to keep in mind is that breaking changes only apply to **publicly documented API**. Internal features,
including any attributes that start with an underscore or those explicitly mentioned as internal are not a part of the
public API and are subject to change without warning.

Here are examples of what constitutes a breaking change:

- Changing the default parameter value of a function to something else.
- Renaming (or removing) a function without deprecation
- Adding or removing parameters of a function.
- Removing deprecated alias to a renamed function.
- Protocol changes that affect how public methods or classes behave.

!!! note

    The examples above are non-exhaustive.

## Examples of Non-Breaking Changes

The following changes are considered non-breaking under mcproto’s versioning model:

<div class="annotate" markdown>

- Changing function's name, while providing a deprecated alias.
- Renaming (or removing) internal attributes or methods, such as those prefixed with an underscore.
- Adding new functionality that doesn’t interfere with existing function signatures or behavior.
- Changing the behavior of a function to fix a bug. (1)
- Changes in the typing definitions of the public API.
- Changes in the documentation.
- Modifying the internal protocol connection handling.
- Adding an element into `__slots__` of a data class.
- Updating the dependencies to a newer version, major or otherwise.

</div>

1. This only includes changes that don't affect users in a breaking way, unless you're relying on the bug—in which
   case, that's on you, and it's probably time to rethink your life choices.

## Special Considerations

Given that mcproto is tied closely to the evolving Minecraft protocol, we may have to make breaking changes more
frequently than a typical Python library.

While we aim to provide deprecation warnings for changes, particularly in **protocol-independent core library
features**, there are certain limitations due to the nature of Minecraft protocol updates. When a major update is
released as a result of a Minecraft protocol change, **we will not provide deprecations for affected features**, as the
protocol itself has changed in a way that necessitates immediate adaptation.

However, for **internal major updates** that are independent of Minecraft protocol changes, **we will make every effort
to deprecate old behavior**, giving users time to transition smoothly before removing legacy functionality.

Specifically, the protocol dependant code includes code in `mcproto.packets` and `mcproto.types` packages. Lower level
protocol abstractions present in `mcproto.protocol`, `mcproto.buffer`, `mcproto.connection`, `mcproto.encryption`,
`mcproto.multiplayer` and `mcproto.auth` will go through proper deprecations. This should allow you to safely use these
lower level features to communicate to servers at any protocol version.

## Communicating deprecations & breaking changes

When a breaking change occurs, you will always find it listed at the top of the changelog. Here, will also find
detailed notes about any migration instructions and a brief reason for the change.

When a feature is deprecated, we will notify users through:

- **Warnings in the code** (via `DeprecationWarning`): These warnings will contain details about what was deprecated,
  including a replacement option (if there is one) and a version number for when this deprecation will be removed.
- **Entries in the changelog**: This includes any migration instructions and a brief reason for deprecation.
