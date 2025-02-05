!!! bug "Work In Progress"

    This page is still being written. The content below (if any) may change.

# API reference

???+ abstract

This page contains the guide on documenting the code that will appear in the API reference section of this
documentation. It goes over the technology and libraries that we use to generate this API reference docs, details the
docstring style we use, mentions how to add something into the API reference (like new modules) and details what
should and shouldn't be documented here.

As was already briefly mentioned in the [documentation](./documentation.md) section, we're using
[mkdocstrings](https://mkdocstrings.github.io/), which is an extension of `mkdocs` that is able to automatically
generate documentation from the source code.

Well, we're using `mkdocstrings`, but internally, the python handler for `mkdocstrings` is using
[`griffe`](https://mkdocstrings.github.io/griffe/), which is the tool responsible for actually analyzing the source
code and collecting all the details.

As you might imagine though, in order to allow `griffe` to automatically pick up information about our codebase, it's
necessary to actually include this information into the code, as you're writing it. It's also important to use a
consistent style, that `griffe` can understand.

In our case, we use the [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for
writing docstrings.

## Google Style docstrings formatting

While you should ideally just read over the [official
specification](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) (don't worry, it's actually
quite readable; well, other than the white theme), you can also take a quick glance through some of these examples
below, that quickly demonstrate the style.

```python
def deal_damage(entity: Entity, damage: int) -> None:
    """Deal damage to specified entity.

    Args:
        entity: The entity to deal damage to
        damage: The amount of damage to deal.

    Note:
        This might end up killing the entity. If this does occur
        a death message will be logged.
    """
    entity.hp -= damage
    if entity.hp <= 0:
        print(f"Entity {entity.name} died.")


def bake_cookie(flavor: str, temperature: int = 175) -> str:
    """Bake a delicious cookie.

    This function simulates the process of baking a cookie with the given flavor.

    Args:
        flavor: The type of cookie to bake. Must be a valid flavor.
        temperature: The baking temperature in Celsius.
            Defaults to 175.

    Returns:
        A string confirming that the cookie is ready.

    Raises:
        ValueError: If the flavor is unknown.
        RuntimeError: If the oven temperature is too high and the cookie burns.
    """
    valid_flavors = {"chocolate chip", "oatmeal", "peanut butter", "sugar"}
    if flavor not in valid_flavors:
        raise ValueError(f"Unknown flavor: {flavor}")

    if temperature > 500:
        raise RuntimeError("Oven overheated! Your cookie is now charcoal.")

    return f"Your {flavor} cookie is baked at {temperature}°F and ready to eat!"


class Cat:
    """A simple representation of a cat.

    Attributes:
        name: The name of the cat.
        age: The age of the cat in years.
        is_hungry: Whether the cat is hungry.
    """

    def __init__(self, name: str, age: int):
        """Initialize a cat with a name and age.

        Args:
            name: The name of the cat.
            age: The age of the cat in years.
        """
        self.name = name
        self.age = age
        self.is_hungry = True # a new cat is always hungry (duh!)

    def purr(self) -> str:
        """Make the cat purr."""
        return "Purr... Purr..."

    def meow(self) -> str:
        """Make the cat meow.

        Returns:
            A string representing the cat's meow.
        """
        return f"{self.name} says 'Meow!'"

    def feed(self) -> None:
        """Feed the cat.

        Once fed, the cat will no longer be hungry.
        """
        self.is_hungry = False

DEFAULT_HP = 500
"""This is the default value for the amount of health points that each entity will have."""
```

!!! tip "Further reading"

    - Like mentioned above, you can take a look over the [official Google style guide
      spec](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
    - Griffe also has a [docstring recommendations
      page](https://mkdocstrings.github.io/griffe/guide/users/recommendations/docstrings/), where you can find a bunch
      of examples that showcase the various places where you can use docstrings.
    - On top of the general docstring recommendations, griffe also has a bit more detailed [reference
      page](https://mkdocstrings.github.io/griffe/reference/docstrings/#google-style) that further demonstrates some of
      the things that will and won't work.

### Cross-References

If you need to refer to some object (function/class/attribute/...) from you docstring, you will need to follow the
[mkdocstrings cross-references syntax](https://mkdocstrings.github.io/usage/#cross-references). Generally, it will look
something like this:

```python title="mcproto/module_b.py"
from mcproto.module_a import custom_object

def bar(obj): ...

def foo():
    """Do the foo.

    This function does the foo by utilizing the [`bar`][mcproto.module_b.bar] method,
    to which the [`custom_object`][mcproto.module_a.custom_object] is passed.
    """
    bar(custom_object)
```

The references need to point to an object that is included in the docs (documented in API reference pages).

### Relative Cross-References

While relative cross-references are supported by mkdocstrings, they are [gated for sponsors
only](https://mkdocstrings.github.io/python/usage/configuration/docstrings/#relative_crossrefs), at least until a
funding goal is reached.

For that reason, we're using an alternative handler to `mkdocstrings-python`:
[`mkdocstrings-python-xref`](https://github.com/analog-garage/mkdocstrings-python-xref). This handler uses
`mkdocstrings-python` internally, while extending it to provide support for relative cross-references. It is expected
that once relative cross-refs come to mainline `mkdocstrings-python`, this alternative handler will be dropped.

To use relative cross-references, check the [mkdocstrings-python-xref
documentation](https://analog-garage.github.io/mkdocstrings-python-xref).

## Writing API Reference

On top of just learning about how to write docstrings, you will need to understand how to write the docs for the API
reference. Currently, most of our API reference docs work by simply recursively including the whole module, so you
likely won't need to touch it unless you're adding new modules (files). That said, sometimes, it might be useful to
document something from the docs directly, rather than just from docstrings.

Rather than rewriting what's already really well explained, we'll instead just point you towards the [mkdocstrings
documentation](https://mkdocstrings.github.io/usage/).

## What to document

Finally, before including something into the docs, make sure it makes sense as a part of your Public API. When deciding
this, you might find this [Griffe
guide](https://mkdocstrings.github.io/griffe/guide/users/recommendations/public-apis/) to be helpful.
