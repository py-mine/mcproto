# Type Hints

???+ abstract

    This article explains what python type-hints are, how they can be enforced with the use of type checkers and the
    type checker of our choice: **basedpyright** and it's editor integration.

Most people only know python as a dynamically typed language, that doesn't offer any kind of type safety. In the very
days of python, this was true, however today, things are a bit different. Even though Python on it's own is still a
dynamically typed language, it does actually support specifying "type hints" which can even be enforced by external
tools called "type checkers". With those, we can achieve a (mostly) type safe experience while using Python.

## Regular python

In regular python, as most people know it, you might end up writing a function like this:

```python
def add(x, y):
  return x + y
```

In this code, you have no idea what the type of `x` and `y` arguments should be. So, even though you may have intended
for this function to only work with numbers (ints), it's actually entirely possible to use it with something else. For
example, running `add("hello", "world)` will return `"helloworld"` because the `+` operator works on strings too.

The point is, there's nothing telling you what the type of these parameters should be, and that could lead to
misunderstandings. Even though in some cases, you can figure out what the type should these variables have purely based
on their name alongside the name of the function, in most cases, it's not that easy. It often requires looking through
the docs, or going over the actual source code of such function.

Annoyingly, python won't even prevent you from passing in types that are definitely incorrect, like: `add(1, "hi")`.
Running this would cause a `TypeError`, but unless you have unit-tests that actually run that code, you won't find out
about this bug until it actually causes an issue and at that point, it might already be too late, since your code has
crashed a production app.

Clearly then, this isn't ideal.

## Type-Hints

While python doesn't require it, there is in fact a way to add a "**hint**" that indicates what **type** should a given
variable have. So, when we take the function from above, adding type-hints to it would result in something like this:

```python
def add(x: int, y: int) -> int:
  return x + y
```

We've now made the types very explicit to the programmer, which means they'll no longer need to spend a bunch of time
looking through the implementation of that function, or going through the documentation just to know how to use this
function. Instead, the type hints will tell just you.

This is incredibly useful, because most editors will be able to pick up these type hints, and show them to you while
calling the function, so you know what to pass right away, without even having to look at the function definition where
the type-hints are defined.

Not only that, specifying a type-hint will greatly improve the development experience in your editor / IDE, because
you'll get much better auto-completion. The thing is, if you have a parameter like `x`, but your editor doesn't know
what type it should have, it can't really help you if you start typing `x.remove`, looking for the `removeprefix`
function. However, if you tell your editor that `x` is a string (`x: str`), it will now be able to go through all of
the methods that strings have, and show you those that start with `remove` (being `removeprefix` and `removesuffix`).

This makes type-hints great at saving you time while developing, even though you have to do some additional work when
specifying them.

## Runtime behavior

Even though type-hints are a part of the Python language, the interpreter doesn't actually care about them. That means
that the interpreter doesn't do any optimizations or checking when you're running your code, even if you have a
function like `add` that we have added type-hints to, code like `add(1, "hi")` will not cause any immediate errors.

Most editors are configured very loosely when it comes to type-hints. That means they will show you these hints when
you're working with the function, but they won't produce warnings when you pass in the wrong thing. That's why they're
called "type hints", they're only hints that can help you out, but they aren't actually enforced.

## Enforcing type hints - Type Checkers

Even though python on it's own indeed doesn't enforce the type-hints you specify, there are tools that can run "static"
checks against your code. A static check is a check that works with your code in it's textual form. It will read the
contents of your python files without actually running that file and analyze it purely based on that text content.

Using these tools will allow you to analyze your code for typing mistakes before you ever even run your program. That
means having a function call like `add(1, "hi")` anywhere in your code would be detected and reported as an issue.

There is a bunch of these tools available for python, but the most common ones are
[`pyright`](https://github.com/microsoft/pyright) and [`mypy`](https://mypy.readthedocs.io/en/stable/).

## BasedPyright

The type checker that we use in our code-base is [**basedpyright**](https://docs.basedpyright.com/). It's a fork of
pyright which adds some extra checks and features and focuses more on the open-source community, than the
official Microsoft owned Pyright.

### Running BasedPyright

To run BasedPyright on the code-base, you can use the following command:

```bash
basedpyright .
```

!!! note ""

    You will need to run this from an [activated](./setup.md#activating-the-environment) poetry environment while
    in the project's root directory.

### Editor Integration

=== "VSCode"

    On vscode, you can simply install the [BasedPyright extension][basedpyright-vscode-ext] from the marketplace.

    Note that this extension does collide with the commonly used **Pylance** extension, which is installed
    automatically alongside the **Python** extension and provide intellisense for Python. The reason BasedPyright
    collides with this extension is that Pylance actually uses pyright as a language server in the background, and as
    we mentioned, basedpyright is an alternative, so using both would cause duplicate errors. This means that you will
    need to disable Pylance, at least within our codebase.

=== "Neovim"

    If you're using Neovim, I would recommend setting up LSP (Language Server Protocol) and installing basedpyright, as
    it has language server support built into it. You can achieve this with the [`lspconfig`][neovim-lspconfig] plugin.
    You can then use [`mason-lspconfig`][neovim-mason-lspconfig-plugin] to install `basedpyright`, or manually
    configure `lspconfig` and use your system-wide `basedpyright` executable.

[basedpyright-vscode-ext]: https://marketplace.visualstudio.com/items?itemName=detachhead.basedpyright
[neovim-lspconfig]: https://github.com/neovim/nvim-lspconfig
[neovim-mason-lspconfig-plugin]: https://github.com/williamboman/mason-lspconfig.nvim

## Great resources

While type hinting might seem very simple from the examples shown above, there is actually a fair bit to it, and if you
never worked within a type checked code-base, you should definitely check out some of these resources, which go over
the basics.

- [Getting started with type hints in Python](https://dev.to/decorator_factory/type-hints-in-python-tutorial-3pel) - a
  blog post / tutorial by decorator-factory.
- [Basics of static typing](https://docs.basedpyright.com/#/type-concepts) - part of the BasedPyright documentation
- [Mypy documentation](https://mypy.readthedocs.io/en/stable/) - very extensive documentation on various typing
  concepts. (Some things are mypy focused, but most things will cary over to basedpyright too)
- [Python documentation for the `typing` module](https://docs.python.org/3/library/typing.html) - Python's standard
  library contains a `typing` module, which holds a bunch of useful structures that we often use while working with
  type-hints.
- [PEP 484](https://www.python.org/dev/peps/pep-0484/) - formal specification of type hints for the Python langauge
