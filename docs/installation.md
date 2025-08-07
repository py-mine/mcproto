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

## Test PyPI (latest main commit builds)

Mcproto publishes a new version to [Test PyPI][mcproto-testpypi] on **every commit to the `main` branch**, using a
version format like `0.6.0.postN.devX`. This is useful if you want the latest development changes but still prefer
installing from a trusted package index (e.g. one that provides [attestations] or reproducible builds), instead of
relying on VCS links.

Although these builds are technically considered "pre-releases", they are _not_ alpha or beta versions like `0.5.0a1`
(which would appear on PyPI too). They're regular post-development builds made continuously for easier testing and
access.

These builds are functionally identical to what you'd get from installing directly from Git (see [next
section](#latest-git-version)), but Test PyPI offers advantages like:

- Index-based installation with hashes and attestations
- Easier CI/CD and lockfile compatibility
- No need for Git to be installed

!!! warning

    Mcproto is still in active development, and changes can happen quickly. These builds may contain bugs or unfinished
    features. However, they're useful if you want to try out a fix or feature that hasn't yet been released on the main
    PyPI index, as it can sometimes take us a while to publish stable releases during this stage.

To install the latest version from Test PyPI:

=== ":simple-python: pip"

    ```bash
    pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple --pre mcproto
    ```

    <div class="result" markdown>

    [pip] is the main package installer for Python.

    ---

    Tell pip to prefer Test PyPI for new versions while falling back to PyPI for dependencies.

    </div>

=== ":simple-poetry: poetry"

    ```bash
    poetry source add --priority=supplemental testpypi https://test.pypi.org/simple
    poetry add --source testpypi mcproto
    ```

    <div class="result" markdown>

    [Poetry] is an all-in-one solution for Python project management.

    ---

    Add the testpypi index as an additional source and install mcproto using that source.

    </div>

=== ":simple-rye: rye"

    ```bash
    # N/A
    ```

    <div class="result" markdown>

    [Rye] is an all-in-one solution for Python project management, written in Rust.

    ---

    Rye does not have a clean way to specify per-package source, it is possible to add Test PyPI as a source and use it
    globally, however, this would also affect other packages, and even with this approach, Rye handles dependency
    resolution pretty poorly (if a packge is being installed from Test PyPI, all of it's dependencies must be from Test
    PyPI, or they must be installed manually).

    For this reason, we don't recommend using the Test PyPI index with Rye, instead, if you want the latest release,
    follow the git installation method.

    </div>

=== ":simple-ruff: uv"

    ```bash
    uv add --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple mcproto
    ```

    <div class="result" markdown>

    [uv] is an ultra fast dependency resolver and package installer, written in Rust.

    ---

    Uv supports custom indexes via matching pip flags.

    </div>

=== ":simple-pdm: pdm"

    ```bash
    # N/A
    ```

    <div class="result" markdown>

    [PDM] is an all-in-one solution for Python project management.

    ---

    With PDM, you will want to follow their [documentation][pdm-index-docs] for this type of installation, as it
    involves editing `pyproject.toml` manually and a deeper understanding of what you're doing is beneficial.

    Alternatively, you can just use the git installation instead.

    </div>

## Latest (git) version

Installing directly from Git gives you the exact same version as Test PyPI: the latest commit to `main`, but also allows
you to install from **any branch or commit**. This is useful if you're testing experimental branches or need a very
specific commit not yet published to Test PyPI, or you just don't want to use the Test PyPI index.

!!! warning

    This type of installation carries the same risks of bugs occuring as the Test PyPI installation. See the warning
    notice in that section.

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
[mcproto-testpypi]: https://test.pypi.org/project/mcproto/
[pip]: https://pip.pypa.io/en/stable/
[Poetry]: https://python-poetry.org/
[Rye]: https://rye.astral.sh/
[uv]: https://github.com/astral-sh/uv
[PDM]: https://pdm-project.org/en/latest/
[pdm-index-docs]: https://pdm-project.org/latest/usage/config/#specify-index-for-individual-packages
[attestations]: https://docs.pypi.org/attestations/
