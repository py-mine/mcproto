# Slotscheck

???+ abstract

    This page explains how we enforce the proper use of `__slots__` on our classes with `slotscheck` tool. We go over
    what slotted classes, what slotscheck enforces, how to run slotscheck and how to configure it.

On top of the tools you already saw (ruff & basedpyright), we also have one more tool that performs static analysis on
our code: [**slotscheck**](https://slotscheck.readthedocs.io/en/latest/).

## What is slotscheck

Slotscheck is a tool that focuses on enforcing proper use of `__slots__` on classes.

???+ question "What are slotted classes"

    If you aren't familiar with slotted classes, you should check the [official
    documentation](https://wiki.python.org/moin/UsingSlots). That said, if you just want a quick overview:

    - Slots allow you to explicitly declare all member attributes of a class (e.g. declaring `__slots__ = ("a", "b")`
      will make the class instances only contain variables `a` and `b`, trying to set any other attribute will result
      in an `AttributeError`).
    - The reason we like using slots is the efficiency they come with. Slotted classes use up less RAM and offer
      a faster attribute access.

    Example of a slotted class:

    ```python
    class FooBar:
        __slots__ = ("foo", "bar")

        def __init__(self, foo: str, bar: str) -> None:
            self.foo = foo
            self.bar = bar

    x = FooBar("a", "b")
    print(x.a, x.b)
    x.c = 5  # AttributeError
    ```

With a low level project like mcproto, efficiency is important and `__slots__` offer such efficiency at a very low cost
(of simply defining them).

The purpose of `slotscheck` is to check that our slotted classes are using `__slots__` properly, as sometimes, it is
easy to make mistakes, which result in losing a lot of the efficiency that slots provide. Issues that slotscheck
detects:

- Detect broken slots inheritance
- Detect overlapping slots
- Detect duplicate slots

## How to use slotscheck

To run slotscheck on the codebase, you can use the following command:

```bash
slotscheck -m mcproto
```

!!! note ""

    Make you have an [activated](./setup.md#activating-the-environment) poetry virtual environment and you're in
    the project's root directory.

## Configuring slotscheck

Sometimes, you may want to ignore certain files from being checked. To do so,
you can modify the [slotscheck configuration][slotscheck-config] in
`pyproject.toml`, under the `[tool.slotscheck]` option. That said, doing so
should be very rare and you should have a very good reason to ignore your file
instead of fixing the underlying issue.

[slotscheck-config]: https://slotscheck.readthedocs.io/en/latest/configuration.html
