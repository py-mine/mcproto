# Installation

## PyPI (stable) version

Mcproto is available on [PyPI](https://pypi.org/project/mcproto) and can be installed like any other python library with:

=== "pip"

    ```bash
    pip install mcproto
    ```

=== "poetry"

    ```bash
    poetry add mcproto
    ```

=== "rye"

    ```bash
    rye add mcproto
    ```

## Latest (git) version

Alternatively, you may want to install the latest available version, which is what you currently see in the `main` git
branch. Although this method will actually work for any branch with a pretty straightforward change.

This kind of installation should only be done if you wish to test some new unreleased features and it's likely that you
will encounter bugs.

That said, since mcproto is still in development, changes can often be made quickly and it can sometimes take a while
for these changes to carry over to PyPI. So if you really want to try out that latest feature, this is the method
you'll want.

To install the latest mcproto version directly from the `main` git branch, use:

=== "pip"

    ```bash
    pip install 'mcproto@git+https://github.com/py-mine/mcproto@main'
    ```

=== "poetry"

    ```bash
    poetry add 'git+https://github.com/py-mine/mcproto#main'
    ```

=== "rye"

    ```bash
    rye add mcproto --git='https://github.com/py-mine/mcproto' --branch main
    ```