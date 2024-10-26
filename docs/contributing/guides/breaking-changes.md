# Breaking changes & Deprecations

???+ abstract

    This page describes how we handle breaking changes and deprecations in the project. It clarifies what is a breaking
    change, what is a deprecation, how to mark something as deprecated and explains when a function should be
    deprecated. Finally, it mentions how to properly communicate breaking chagnges and deprecations to end users.

!!! note "Pre-Requisites"

    Before reading this page, make sure to familiarize yourself with our [versioning
    model](../../installation/versioning-model.md)


## What is a breaking change

A breaking change is a modification that requires developers to adjust their code due to alterations that break
previously working functionality. This includes changes such as altering method signatures, changing return types, or
removing classes or functions without prior warning.

We follow [semantic versioning](https://semver.org) to manage breaking changes. That means, **major** version
increments (e.g., from `3.x.x` to `4.0.0`) indicate breaking changes. It’s essential that users can rely on **minor** and
**patch** versions (e.g., `3.1.0` or `3.0.1`) being backwards-compatible with the first major release (`3.0.0`).

When introducing changes, aim to implement them in a non-breaking way. Breaking changes should be **avoided** whenever
possible. If a breaking change is absolutely necessary, strive to transition gradually through **deprecations**.

Refer to the [versioning model page](../../installation/versioning-model.md#examples-of-breaking-changes) for some
examples of what constitutes a breaking change.

## What is a deprecation

A deprecation signals that a particular part of the code (commonly a function, class, or argument) should no longer be
used because it is outdated, inefficient, or replaced by better alternatives. Deprecations are a **temporary** measure
to guide developers toward **transitioning** to newer practices, while giving them time to adjust their code without
causing immediate disruptions.

Deprecations act as a soft warning: they indicate that the deprecated feature will eventually be removed, but for now,
it remains usable with a runtime deprecation warning. This gives developers enough time to adapt before the removal
takes place in a future major release.

It’s essential to understand that deprecations are not permanent — every deprecated feature has a defined removal
version, beyond which it will no longer exist. Typically, the removal happens in the next major version after the
deprecation was announced. For example, if a feature is deprecated in version `3.x`, it will usually be removed in
version `4.0.0`.

!!! info "Recap"

    Deprecations help to avoid **immediate breaking changes** by offering a **grace period** for users to update their
    code before the feature is entirely removed in the next major release.

Deprecations are primarily used for:

- **Phasing out old functions, classes, or methods** in favor of improved alternatives.
- **Renaming functions, arguments, or classes** to align with better conventions.
- **Adjusting method signatures**, such as adding required arguments or removing old ones.
- **Changing behaviors** that can’t be applied retroactively without introducing errors.

!!! important "Deprecating protocol changes"

    Deprecations are **not used for protocol-related changes**, as the Minecraft protocol evolves independently of
    mcproto’s internal development. For these types of changes, mcproto will introduce a major version bump and require
    users to update.

    *That said, these changes are still considered as breaking, and will need to be documented as such.*

!!! note

    Sometimes, it isn't possible/feasible to deprecate something, as the new change is so different from the original
    that a breaking change is the only option. That said, this should be a rare case and you should always first do
    your best to think about how to deprecate something before deciding on just marking your change as breaking.

## How to deprecate

We have two custom function to mark something as deprecated, both of these live in the `mcproto.utils.deprecation`
module:

- `deprecation_warn`: This function triggers a deprecation warning immediately after it is called, alerting developers
    to the pending removal.
- `deprecated`: This decorator function marks a function as deprecated. It triggers a deprecation warning each time the
    decorated function is called. Internally, this ultimately just calls `deprecation_warn`.

### Removal version

These functions take a removal version as an argument, which should be specified as a [semantic
version](https://semver.org/) string. Generally, you'll just want to put the next major version of the library here (so
if you're currently on `3.5.2` you'll want to specify the removal version as `4.0.0`; You always want to bump the first
/ major version number.)

The `deprecation_warn` function will usually just show a warning, however, if the current version of the library
surpasses the removal version, it will instead throw a runtime error, making it unusable. In most cases, people
shouldn't ever face this, as once the new major version is released, all deprecations with that removal version should
be removed, but it's a nice way to ensure the proper behavior, just in case we'd forget, allowing us to remove them
later on in a patch version without breaking the semantic versioning model.

!!! note

    The removal version is a **required** argument, as we want to make sure that deprecated code doesn't stay in our
    codebase forever. Deprecations should always be a temporary step toward the eventual removal of a feature.

    If there is a valid reason to extend the deprecation period, you can push back the removal version, keeping the old
    or compatibility code longer and incrementing the major version number in the argument accordingly.

    However, we should **never** shorten the deprecation period, as that would defeat the purpose of giving developers
    enough time to adapt to the change. Reducing the deprecation time could result in unexpected breakage for users
    relying on the deprecated feature.

### Examples

#### Function rename

```python
from mcproto.utils.deprecation import deprecated


@deprecated(removal_version="4.0.0", replacement="new_function")
def old_function(x: int, y: int) -> int:
  ...


def new_function(x: int, y: int) -> int:
  ...
```

#### Class removal

```python
@deprecated(removal_version="4.0.0", extra_msg="Optional extra message")
class MyClass:
  ...
```

#### Argument removal

```python
from mcproto.utils.deprecation import deprecation_warn

def old_function(x: int, y: int, z: int) -> int:
  ...

def new_function(x: int, y: int, z: int | None = None) -> int:
  if z is not None:
    deprecation_warn(
      obj_name="z (new_function argument)",
      removal_version="4.0.0",
      replacement=None,
      extra_msg="Optional extra message, like a reason for removal"
    )

  ...  # this logic should still support working with z, just like it did in the old impl
```

## Communicating breaking changes

**Breaking changes necessitate clear communication**, as they directly impact users by forcing updates to their
codebases. It’s essential to ensure that users are well-informed about any breaking changes introduced in the project.
This is achieved through the project’s changelog.

**Every breaking change must be documented using a 'breaking' type changelog fragment.** When writing the fragment,
adhere to the following guidelines:

- Specify **what** was deprecated with a fully qualified name (e.g. `module.submodule.MyClass.deprecated_method`).
- Suggest an **alternative**, if applicable, and explain any necessary **migration steps**.
- Briefly document **why** the deprecation was made (without going into excessive detail).
- Prioritize **clarity and good wording**

These entries are critical, as they are likely to be read by end-users of our library (programmers but
non-contributors). Keep this in mind when crafting breaking change fragments.

!!! warning "Every breaking change needs its own entry"

    If your pull request introduces multiple breaking changes across different components, you must create individual
    changelog entries for each change.

!!! example "Example of a good breaking changelog fragment"

    Suppose a library changes the return type of a function from a list to a set. This type change would be difficult
    to deprecate because the change affects existing code that relies on the specific return type.

    ```markdown title="changes/521.breaking.md"
    Change return type of `mcproto.utils.get_items` from `list[str]` to `set[str]`.

        This change was made to improve performance and ensure unique item retrieval.
        The previous behavior of returning duplicates in a list has been removed,
        which may impact existing code that relies on the previous return type.
        Users should adjust their code to handle the new return type accordingly.
    ```

    Even though it’s technically feasible to implement this as a non-breaking change - such as by creating a new
    function or adding a boolean flag to control the return type, these approaches may not suit our use case. For
    instance, if we were to introduce a boolean flag, we would need to set it to `False` by default and show
    deprecation warnings to users unless they explicitly set the flag to `True`.

    Eventually, when the deprecation period is over, the flag becomes pointless, but removing support for it would
    necessitate yet another round of deprecation for the flag itself, forcing users to revert to using the function
    without it. This approach could frustrate users and create unnecessary complexity.

    When considering non-breaking changes, it’s crucial to evaluate potential complications like these. If you opt for
    a breaking change, be sure to include similar reasoning in your pull request description to help convey the
    rationale behind the decision.

!!! note "Removing deprecations"

    We consider deprecation removals as a breaking change, which means that these removals also need to be documented.
    That said, it is sufficient for these removals to be documented in a single changelog fragment. These removals
    alongside with writing the fragment will be performed by the project maintainers at the time of the release.

## Communicating deprecations

Even though a deprecation doesn’t immediately break code, it signals an upcoming change and it's essential to communicate
this clearly to the users of our project. We achieve this through the project's changelog.

???+ tip "Benefits of tracking deprecations in changelog"

    While runtime deprecation warnings provide immediate feedback upon updating the library, it can often be beneficial
    to give users a chance to plan ahead before updating the library, especially for projects that perform automatic
    dependency updates through CI, which may not check for warnings, leading to deprecation warnings reaching
    production.

    Additionally, it's often easy for people to miss/overlook the warnings if they're not looking for them in the CLI
    output, or if their project already produces some other warnings, making ours blend in.

    By clearly documenting deprecations, we enable users to identify deprecated features before upgrading, allowing
    them to address issues proactively or at least prepare for changes.

    A changelog entry serves as a permanent, versioned record of changes, providing detailed explanations of why a
    feature is deprecated, what the recommended replacements are. It's a place where people may look for clarification
    on why something was removed, or in search of migration steps after seeing the deprecation warning.

**Every deprecation must be documented using a 'deprecation' type changelog fragment.** When writing the fragment,
similar guidelines to writing breaking changelog fragments apply:

<div class="annotate" markdown>

- Provide the **removal version** i.e. version in which the deprecated feature will be removed (e.g. `4.0.0`). (1)
- Specify **what** was deprecated with a fully qualified name (e.g. `module.submodule.MyClass.deprecated_method`).
- Suggest an **alternative**, if applicable, and explain any necessary **migration steps**.
- Briefly document **why** the deprecation was made (without going into excessive detail).
- Prioritize **clarity and good wording**

</div>

1. This point is specific to deprecations, it's the only additional point in comparison to the breaking changes
   guidelines.

These entries form the second most important part of the changelog, likely to be read by end-users. Keep this in mind
when crafting deprecation fragments.

!!! warning "Every deprecated component needs it's own entry"

    Just like with breaking changes, if your're deprecating multiple different components, you
    must make multiple changelog entries, one for each deprecation.

!!! example "Example of a good deprecation changelog fragment"

    Suppose we used a simple string configuration parameter but introduced a more flexible configuration object to
    allow for future extensions and better validation. This would be a good candidate for deprecation rather than an
    immediate breaking change.

    ```markdown title="changes/521.deprecation.md"
    Deprecate string-based `mcproto.utils.connect` configuration attribute in favor of `mcproto.utils.ConnectionConfig`.

        The new `ConnectionConfig` object offers more flexibility by allowing users to specify multiple options (like
        timeouts, retries, etc.) in a structured way, instead of relying on a string. Users are encouraged to migrate
        to this object when calling `mcproto.utils.connect` to take full advantage of future improvements and
        additional connection parameters.

        - The string-based configuration support will be removed in version `4.0.0`.
    ```
