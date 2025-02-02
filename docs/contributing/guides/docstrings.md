!!! bug "Work In Progress"

    This page is still being written. The content below (if any) may change.

# Docstring formatting directive

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

## Google Style docstrings

While you should ideally just read over the [official
specification](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) (don't worry, it's actually
quite readable; well, other than the white theme)

That said, you can also take a quick glance through some of these examples below, that quickly demonstrate the style.

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
```
