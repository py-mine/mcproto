---
hide:
    - navigation
---

# Installation

## PyPI (stable) version

Mcproto is available on [PyPI][mcproto-pypi] and can be installed like any other python library with:

=== ":simple-python: pip"

    ```bash
    pip install mcproto
    ```

    <div class="result" markdown>

    [pip] is the main package installer for Python.

    </div>

=== ":simple-poetry: poetry"

    ```bash
    poetry add mcproto
    ```

    <div class="result" markdown>

    [Poetry] is an all-in-one solution for Python project management.

    </div>

=== ":simple-rye: rye"

    ```bash
    rye add mcproto
    ```

    <div class="result" markdown>

    [Rye] is an all-in-one solution for Python project management, written in Rust.

    </div>

=== ":simple-ruff: uv"

    ```bash
    uv pip install mcproto
    ```

    <div class="result" markdown>

    [uv] is an ultra fast dependency resolver and package installer, written in Rust.

    </div>

=== ":simple-pdm: pdm"

    ```bash
    pdm add mcproto
    ```

    <div class="result" markdown>

    [PDM] is an all-in-one solution for Python project management.

    </div>

## Latest (git) version

Alternatively, you may want to install the latest available version, which is what you currently see in the `main` git
branch. Although this method will actually work for any branch with a pretty straightforward change.

This kind of installation should only be done if you wish to test some new unreleased features and it's likely that you
will encounter bugs.

That said, since mcproto is still in development, changes can often be made quickly and it can sometimes take a while
for these changes to carry over to PyPI. So if you really want to try out that latest feature, this is the method
you'll want.

To install the latest mcproto version directly from the `main` git branch, use:

=== ":simple-python: pip"

    ```bash
    pip install 'mcproto@git+https://github.com/py-mine/mcproto@main'
    ```

    <div class="result" markdown>

    [pip] is the main package installer for Python.

    </div>

=== ":simple-poetry: poetry"

    ```bash
    poetry add 'git+https://github.com/py-mine/mcproto#main'
    ```

    <div class="result" markdown>

    [Poetry] is an all-in-one solution for Python project management.

    </div>

=== ":simple-rye: rye"

    ```bash
    rye add mcproto --git='https://github.com/py-mine/mcproto' --branch main
    ```

    <div class="result" markdown>

    [Rye] is an all-in-one solution for Python project management, written in Rust.

    </div>

=== ":simple-ruff: uv"

    ```bash
    uv pip install 'mcproto@git+https://github.com/py-mine/mcproto@main'
    ```

    <div class="result" markdown>

    [uv] is an ultra fast dependency resolver and package installer, written in Rust.

    </div>

=== ":simple-pdm: pdm"

    ```bash
    pdm add "git+https://github.com/py-mine/mcproto@main"
    ```

    <div class="result" markdown>

    [PDM] is an all-in-one solution for Python project management.

    </div>

[mcproto-pypi]: https://pypi.org/project/mcproto
[pip]: https://pip.pypa.io/en/stable/
[Poetry]: https://python-poetry.org/
[Rye]: https://rye.astral.sh/
[uv]: https://github.com/astral-sh/uv
[PDM]: https://pdm-project.org/en/latest/
