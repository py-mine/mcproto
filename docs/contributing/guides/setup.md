!!! bug "Work In Progress"

    This page is missing a guide on configuring vscode to pick up poetry environment.

# Setting up the project

???+ abstract

    This guide describes the very basics of setting up our project.

    It explains how to use `poetry` to install the python dependencies for the project. After which it goes over using
    poetry (activating the virtual environment, keeping the dependencies up to date as we update them, adding /
    removing dependencies and poetry dependency group).

## Pre-requisites

A basic knowledge of [git and GitHub][git-and-github], alongside working within the terminal and running commands is a
requirement to work on this project.

This guide assumes you have already [forked][github-forking] our repository, [clonned it][git-cloning] to your
computer and created your own [git branch][git-branches] to work on.

If you wish to work from an already forked repository, make sure to check out the main branch and do a [`git
pull`][git-pull] to get your fork up to date. Now create your new branch.

[git-and-github]: https://docs.github.com/en/get-started/start-your-journey/about-github-and-git
[github-forking]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo
[git-cloning]: https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository
[git-branches]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-branches
[git-pull]: https://github.com/git-guides/git-pull

## Poetry

This project uses [`poetry`](https://python-poetry.org/docs/). Poetry is a tool for managing python dependencies in a
reproducible way, ensuring that everyone is using the same versions. It creates virtual environments for each project,
which ensures that your global dependencies won't clash with the project.

??? question "More about virtual environments"

    A python virtual environment is essentially a separate mini installation of python used purely for the project
    you're working on (as opposed to using your system-wide python installation for everything).

    The reason we do this is to avoid dependency conflicts. Consder this: Our project needs library "foo" at version
    2.5.2, however, you also have another unrelated project, that also needs the "foo" library, but this project didn't
    yet update this dependency, and requires an older version of this library: 1.2.0. This is a problem, because our
    project won't work with a version that old, we're using some of the new features of that library, similarly, your
    project won't work with a newer version though.

    With a virtual environment, both projects will have their own isolated python installation, that only contains the
    dependencies listed for that project, avoiding any conflicts completely.

    You can create virtual environments manually, with the built-in `venv` python module, but poetry makes this much
    simpler. If you want to find out more about virutal environments, check the [official python
    documentation][venv-docs].

[venv-docs]: https://docs.python.org/3/library/venv.html

This means you will need to have poetry installed on your system to run our project. To do so, just follow their
[official documentation](https://python-poetry.org/docs/#installation).

## Dependency installation

Once installed, you will want to create a new environment for our project, with all of our dependencies installed. Open
a terminal in the project's directory and run the following command:

```bash
poetry install
```

After running this command, the virtual environment will be populated with all of the dependencies that you will need
for running & developing the project.

## Activating the environment

The virtual environment that you just created will contain a bunch of executable programs, such as `ruff` (our linter).
One of those executable programs is also `python`, which is the python interpreter for this environment, capable of
using all of those dependencies installed in that environment.

By default, when you run the `python` command, your machine will use the system-wide python installation though and the
executables present in this environment will not be runnable at all. In order to make your terminal use the programs
from this environment, instead of the global ones, you will need to "activate" the environment.

Some IDEs/editors are capable of doing this automatically when you open the project, if your editor supports that, you
should configure it to do so.

??? question "Configuring VSCode to use the poetry environment"

    TODO

If your IDE doesn't have that option, or you just wish to work from the terminal, you can instead run:

```bash
poetry shell
```

Now you can start the IDE from your terminal, which should make it work within the poetry python environment.

!!! tip "Execute a single command inside the virtual environment"

    If you just want to urn a single command from the venv, without necessarily having to activate the environment
    (often useful in scripts), poetry provides a quick and simple way to do so. All you need to do is prefix any such
    command with `poetry run` (e.g. `poetry run ruff`).

## Keeping your dependencies up to date

We often update the dependencies of mcproto to keep them up to date. Whenever we make such an update, you will need to
update your virtual environment to prevent it from going out of date. An out of date environment could mean that you're
using older versions of some libraries and what will run on your machine might not match what will run on other
machines with the dependencies updated.

Thankfully, poetry makes updating the dependencies very easy as all you have to do is re-run the installation command:

```bash
poetry install
```

It can sometimes be hard to know when you need to run the install command, in most cases, even if we did update
something and you're still on an older version, nothing significant will actually happen, however, the moment you start
seeing some errors when you try to run the project, or inconsistencies with the continuous integration workflows from
your local runs, it's a good indication that your dependencies are probably out of date.

Ideally, you should run this command as often as possible, if there aren't any new changes, it will simply exit
instantly. You should be especially careful when switching git branches, as dependencies might have been changed (most
likely a new dependency was introduced, or an old one got removed), so consider running this command whenever you
switch to another branch, unless you know that branch didn't make any changes to the project dependencies.

## Poetry dependency groups

Poetry has a really cool way of splitting up the dependencies that projects need into multiple groups. For example, you
can have a group of dependencies for linting & autoformatting, another group for documentation support, unit-testing,
for releasing the project, etc.

To see which dependencies belong to which group, you can check the `pyproject.toml` file for the
`[tool.poetry.group.GROUP_NAME.dependencies]` sections.

By default, `poetry install` will install all non-optional dependency groups. That means all development
dependencies you should need will get installed.

The reason why we use groups is because in some of our automated workflows, we don't always need all of the project
dependencies and we can save time by only installing the group(s) that we need. It also provides a clean way to quickly
see which dependencies are being used for what.

The most important group is the `main` group. This group contains all runtime dependencies, which means without these
dependencies, the project wouldn't be runnable at all. It is these libraries that will become the dependencies of our
library when we make a release on PyPI.

## Installing dependencies

During the development, you may sometimes want to introduce a new library to the project, to do this, you will first
need to decide which dependency group it should belong to. To do this, identify whether this new dependency will be
required to run the project, or if it's just some tool / utility that's necessary only during the development.

If it's a runtime dependency, all you need to do is run:

```bash
poetry add [name-of-your-dependency]
```

This will add the dependency to the `main` group.

However, if you're working with a development dependency, you will want to go over the dependency groups we have (from
`pyproject.toml`) and decide where it should belong. Once you figured that out, you can run:

```bash
poetry add --group [group-name] [name-of-your-dependency]
```

!!! note

    Sometimes, it might make sense to include the same dependency in multiple groups. (Though this is usually quite
    rare.)

## Uninstalling dependencies

Similarly, we sometimes stop needing a certain dependency. Uninstalling is a very similar process to installation.
First, find which group you want to remove this dependency from and then run:

```bash
poetry remove --group [group-name] [name-of-your-dependency]
```
