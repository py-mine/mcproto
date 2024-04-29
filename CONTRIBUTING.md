# Contributing Guidelines

This project is fully open-sourced and new contributions are welcome!

However know that we value the quality of the code we maintain and distribute, and you will need to adhere to some code
quality standards which we define. Your PR may get rejected on the basis of a contributor failing to follow these
guidelines.

## The Golden Rules of Contributing

We recommend you adhere to most of these rules in pretty much every project, even if it doesn't require you to. These
rules can often make your life much easier, make debugging quicker and keep the commit history cleaner.

1. **Lint before you push.** We have multiple code linting rules, which define our general style of the code-base.
   These are generally enforced through certain tools, which you are expected to run before every push, and ideally
   before every commit. The specifics of our linting will be mentioned [later](#style-guide)
2. **Make great commits.** Great commits should be atomic (do one thing only and do it well), with a commit message
   explaining what was done, and why. More on this in [here](#making-great-commits).
3. **Make an issue before the PR.** If you think there's something that should be added to the project, or you
   found some issue or something which could be improved, consider making an issue before committing a lot of time to
   create a PR. This can help you save a lot of time in case we'd decide that the feature doesn't adhere to our vision
   of the project's future, or isn't something which we would be willing/able to maintain. Even though we won't
   actively enforce this rule, and for some small obvious features, or bug-fixes making an issue may be an overkill,
   for bigger changes, an issue can save you a lot of time implementing something which may not even be wanted in the
   project, and therefore won't get accepted.
4. **Don't open a pull request if you aren't assigned to the issue.** If you want to work on some existing GitHub
   issue, it is always better to ask a maintainer to assign you to this issue. If there's already someone assigned to
   an issue, consider offering to collaborate with that person, rather than ignoring his work and doing it on your own.
   This method can help avoid having multiple people working on the exact same thing at the same time, without knowing
   about each other, which will often lead to multiple approaches solving the same thing, only one of which can be
   accepted (usually from the person who was originally assigned).
5. **Use assets licensed for public use.** Whenever a static asset such as images/video files/audio or even code is
   added, they must have a compatible license with our projects.
6. **Use draft pull requests if you aren't done yet.** If your PR isn't ready to be reviewed yet, mark it as draft.
   This is further described in [this section](#work-in-progress-prs)
7. **Follow our [Code of Conduct](./CODE-OF-CONDUCT.md).**

## Project installation

This project uses [`poetry`](https://python-poetry.org/docs/). It's a tool for managing python virtual environments. If
you haven't heard of those, they're essentially a mini installation of python used purely for the project you're working
on (as opposed to using a single global python installation for everything, which is prone to conflicts, as different
projects might need different versions of the same package). Follow the linked documentation for installation
instructions.

Once installed, you will want to create a new environment for mcproto, with all of it's dependencies installed. To do
that, enter the clonned repository in your terminal, and run:

```bash
poetry install
```

Note that you will want to re-run this command each time our dependencies are updated, to stay in sync with the project.

After that, the environment will contain all of the dependencies, including various executable programs, such as
`pyright`. One of these executable programs is also `python`, which is the python interpreter for this environment,
capable of interacting with all of the installed libraries.

You will now need to make your terminal use the programs from this environment, rather than any global versions that you
may have installed, so that you can use the tools in it when working on the project. Some IDEs/editors are capable of
doing this for you automatically when you open the project. If yours isn't, you can run:

```bash
poetry shell
```

You can then start your IDE from the terminal, after you ran this command, and it should pick up the python environment
created by poetry.

You can also just prefix any command with `poetry run` (e.g. `poetry run python`) to use the executable from the
environment, without activating it, however you will almost always want to activate the environment instead.

For more info about poetry, make sure to check their amazing official documentation: `https://python-poetry.org/docs/`,
these include installation instructions, explain how to add new dependencies to the project, or how to remove some, and
everything else you'd need to know.

## Style Guide

For clarity and readability, adhering to a consistent code style across the whole project is very important. It is not
unusual that style adjustments will be requested in pull requests.

It is always a good practice to review the style of the existing code-base before adding something new, and adhere to
that established style. That applies even if it isn't the style you generally prefer, however if you think a code style
change of some kind would be justified, feel free to open an issue about it and tell us what exactly should be changed,
and why you think this change is important. If you want to, you can also ask to be assigned to the issue and work on
changing the style in the code-base in your own PR. (Hey you may even get to edit this section!)

> A style guide is about consistency. Consistency with this style guide is important. Consistency within a project is
> more important. Consistency within one module or function is the most important.
>
> However, know when to be inconsistent -- sometimes style guide recommendations just aren't applicable. When in doubt,
> use your best judgment. Look at other examples and decide what looks best. And don't hesitate to ask!
> — [PEP 8, the general Style Guide for Python Code](https://peps.python.org/pep-0008/)

### Automatic linting

As there is a lot of various styling rules we adhere to in our code base, and obviously, describing all of them in a
style guide here would just take way too long, and it would be impossible to remember anyway. For that reason, we use
automated tools to help us catch any style violation without manual review!

Currently, these are the tools we use for code style enforcement:

- [`ruff`](https://beta.ruff.rs/docs/): General python linter, formatter and import sorter
- [`slotscheck`](https://slotscheck.readthedocs.io/en/latest/): Enforces the presence of `__slots__` in classes

You can read more about them individually in the sections below. It is important that you familiarize yourself with
these tools, and their standalone usage, but it would of course be very annoying to have to run the commands to run
these tools manually, so while there will be instructions on how to do that, you should pretty much always prefer
direct IDE/editor integration, which is mentioned [here](#editor-integration), and make use of
[pre-commit](#pre-commit).

#### Ruff linter & Formatter

Ruff is an all-in-one linter & formatter solution, which aims to replace the previously very popular
[`flake8`](https://flake8.pycqa.org/en/latest/) linter, [`isort`](https://pycqa.github.io/isort/) import sorter and
[`black`](https://black.readthedocs.io/en/stable/) formatter. Ruff is faster (written in rust! 🦀) and includes most of
the popular flake8 extensions directly. It is almost 1:1 compatible with black, which means the way it formats code is
pretty much the same, with only some very subtle differences.

You can check the ruff configuration we're using in [`pyproject.toml`](./pyproject.toml) file, under the `[tool.ruff]`
category (and it's subcategories), you can find the enabled linter rules there, and some more specific configuration,
like line length, python version, individual ignored lint rules, and ignored files.

To run `ruff` **linter** on the code, you can use `ruff check .` command, while in the project's root directory (from
an activated poetry environment, alternatively `poetry run ruff .`). Ruff also supports some automatic fixes to many
violations it founds, to enable fixing, you can use `ruff check --fix`. This will also run the `isort` integration.

If you find a rule violation in your code somewhere, and you don't understand what that rule's purpose is, `ruff` evens
supports running `ruff rule [rule id]` (for example `ruff rule ANN401`). These explanations are in markdown, so I'd
recommend using a markdown renderer such as [`glow`](https://github.com/charmbracelet/glow) (on Arch linux, you can
install it with: `pacman -S glow`) and piping the output into it for a much nicer reading experience: `ruff rule ANN401
| glow`.

To run `ruff` **formatter** on the code, you can simply execute `ruff format .` command (also needs an activated poetry
environment). This will automatically format all files in the code-base.

#### Slotscheck

Slotscheck is a utility/linter that enforces the proper use of `__slots__` in our python classes. This is important for
memory-optimization reasons, and it also improves the general performance when accessing/working with attributes of
slotted classes.

If you're unsure how slots work / what they are, there is a very nice explanation of them in the official python wiki:
[here](https://wiki.python.org/moin/UsingSlots).

To run slotscheck, you can simply execute `slotscheck -m mcproto` from an activated poetry environment (or
`poetry run slotscheck -m mcproto`).

### Use of `__all__`

Consider a python module like the below:

```python
import foo
from bar import do_bar


def do_foobar():
    foo.do_foo()
    do_bar()
```

If someone were to import it with `from module_above import *`, they'd import `foo`, `do_bar` and `do_foobar`. However
that's kind of weird, in most cases, we don't actually want our imports to be included in a wildcard import like this.
For that reason, we can define a special variable called `__all__`, that specifies all of the things that should
actually be included with a wildcard import like this.

It is our convention to set this variable right below the imports, like this:

```python
import foo
from bar import do_bar

__all__ = ["do_foobar"]


def do_foobar():
    foo.do_foo()
    do_bar()
```

With that, we've explicitly specified what functions/classes should be considered a part of this file, and are expected
to be imported, with all of the rest being considered private and only used in this file internally. (Though it doesn't
mean that the unspecified objects actually can't be imported, it just means they won't be imported with a wildcard `*`
import. So running `from module_above import foo` would work, even though `from module_above import *` wouldn't include
`foo`.)

Note that generally, in vast majority of cases, wildcard imports shouldn't be used and instead we should be explicit so
that we know where our dependencies come from. The actual primary reason we specify `__all__` in our files is to
immediately show which parts of that file should be considered public, and which are internal to the file.

### Docstring formatting directive

We currently don't follow any exact convention telling us how to format our docstrings for something like an
auto-generated project documentation, however this is likely to change soon.

For now, we follow these general rules on specifying our docstrings:

```python
def donut(a: bool, b: str) -> None:
    """Short one-line description of the function."""

def apple(a: bool, b: str) -> None:
    """
    Longer one-line description of the function, which would take up way too much line space if done as shown above.
    """

def pineapple(a: bool, b: str) -> str:
    """One-line description of the function telling us what it's about.

    Detailed multiline description.
    This may include the full explanation of how this function should be used.

    We can also have multiple sections like this.
    For example to include further use instruction with some examples or perhaps
    with an explanation of how the function works, if it's relevant.
    """

def banana(a: bool, b: str) -> None:
    """My docstring"""
    print("I like bananas")  # No space between docstring and first line of code for functions/methods

class Orange:
    """My docstring"""

    def __init__(self):  # Extra newline between the class docstring and first method
      ...

class Tomato:
    """My other docstring"""

    X: ClassVar[int] = 5  # Extra newline even between docstrings and class variables
```

Another general rule of thumb when writing docstrings is to generally stick to using an imperative mood.

Imperative mood is a certain grammatical form of writing that expresses a clear command to do something.

**Use:** "Build a player object."
**Don't use:** "Returns a player object."

Present tense defines that the work being done is now, in the present, rather than in the past or future.

**Use:** "Build a player object."
**Don't use:** "Built a player object." or "Will build a player object."

## Type hinting

[PEP 484](https://www.python.org/dev/peps/pep-0484/) formally specifies type hints for Python. You can specify type
hints for a function, in addition to just parameter names, allowing you to quickly understand what kind of parameter
this is. Most IDEs/editors will even be able to recognize these type hints, and provide auto-completion based on them.
For example, if you type hint a parameter as `list`, an editor can suggest list methods like `join` or `append`. Many
editors will even show you the type hint on the argument in the function's signature, when you're trying to call it,
along with the parameter name making it really easy to understand what you're supposed to pass without even looking at
the docstring.

For example, an untyped function can look like this:

```python
def divide(a, b):
    """Divide the two given arguments."""
    return a / b
```

With type-annotations, the function looks like this:

```python
def divide(a: int, b: int) -> float:
    """Divide the two given arguments."""
    return a / b
```

Thankfully python type-hinting is fairly easy to understand, but if you do want to see some rather interesting
resources for a bit more advanced concepts such as type variables or some more complex types like `typing.Callable`,
we've compiled a quick list of really amazing resources about these type hinting practice.

- Python documentation from `typing` library: <https://docs.python.org/3/library/typing.html>
- MyPy documentation (very extensive but quite beginner friendly): <https://mypy.readthedocs.io/en/stable/>
- Decorator Factory blog about typing: <https://decorator-factory.github.io/typing-tips/>
- Typing Generics (advanced): <https://itsdrike.com/posts/typing-generics/>

### Enforcing type hints - Type checker

Even though the type hints can be pretty useful in knowing what the function variables are expected to be and they also
provide better auto-completion, if we're not careful, we could soon end up violating our own type specifications,
because by default python doesn't enforce these type-hints in any way. To python, they're not much more than comments.

To make sure that our code-base really is correct type-wise, we use a tool that looks at the code statically (similarly
to a linter), and analyzes the types, finding any inconsistencies. Using a type-checker can be very beneficial,
especially to bigger projects, as it can quickly catch mistakes we made based on purely the types, without even having
to run the code. So many times, you'll see issues before actually testing things out (with unit-tests, or manually). In
a lot of cases, type checkers can even uncover many things that our unit tests wouldn't find.

There are many python type-checkers available, the most notable ones being `mypy` and `pyright`. We decided to use
`pyright`, because it has great support for many newer typing features. Pyright can be used from the terminal as a
stand-alone linter-like checker, by simply running `pyright .` (from within an activated virtual environment). But just
like with linters, you should ideally just [include it into your editor directly](#editor-integration). We also run
pyright automatically, as a part of [pre-commit](#pre-commit).

## Pre-commit

Now that you've seen the linters, formatters, type-checkers and other tools that we use in the project, you might be
wondering whether you're really expected to run all of those commands manually, after each change. And of course, no,
you're not, that would be really annoying, and you'd probably also often just forget to do that.

So, instead of that, we use a tool called `pre-commit`, which creates a [git
hook](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks), that will automatically run before each commit you
make. That means each time when you make a commit, all of these tools will run over the code you updated, and if any of
these linters detects an issue, the commit will be aborted, and you will see which linter failed, and it's output
telling you why.

To install pre-commit as a git hook all you need to do is to run `pre-commit install` from an activated poetry
environment, installing it into the git repository as a hook running before every commit. That said, you can also run
pre-commit without having to install it (or without having to make a commit, even if installed). To do that, simply
execute: `pre-commit run --all-files`. Note that the installed hook will only run the linters on the files that were
updated in the commit, while using the command directly will run it on the whole project.

You can find pre-commit's configuration the [`.pre-commit-config.yaml`](./.pre-commit-config.yaml) file, where we
define which tools should be ran and how. Currently, pre-commit runs ruff linter, ruff formatter, slotscheck and
pyright, but also a checker for some issues in TOML/YAML files.

Even though in most cases enforcing linting before each commit is what we want, there are some situations where we need
to commit some code which doesn't pass these checks. This can happen for example after a merge, or as a result of
making a single purpose small commit without yet worrying about linters. In these cases, you can use the `--no-verify`
flag when making a commit, telling git to skip all of the pre-commit hooks and commit normally. You can also only skip
a specific hook(s), by setting `SKIP` environmental variable (e.g. `SKIP=pyright`, or
`SKIP=ruff-linter,ruff-formatter,slotscheck`), the names of the individual hooks are their ids, you can find those in
the configuration file for pre-commit.

However this kind of verification skipping should be used sparingly. We value a clean history which consistently follows
our linting guidelines, and making commits with linting issues only leads to more commits, fixing those issues later. If
you really do need to skip the linters though, you should then wait until you create another commit fixing the issues
before pushing the code to github, to avoid needlessly failing the automated workflows, which run pre-commit themselves
(amongst other things).

## Editor Integration

Even with pre-commit, it would still be very annoying to have to only run the linters during the commit, because with
the amount of rules we have, and especially if you're not used to following many of them, you will make a lot of
mistakes. Because of that, we heavily recommend that you integrate these tools into your IDE/editor directly. Most
editors will support integration will all of these tools, so you shouldn't have any trouble doing this.

If you're using neovim, I would recommend setting up LSP (Language Server Protocol), and installing Pyright, as it has
language server support built into it. Same thing goes with `ruff`, which has an LSP implementation
[`ruff-lsp`](https://github.com/astral-sh/ruff-lsp). As for slotscheck, there isn't currently any good way to integrate
it directly, so you will need to rely on pre-commit, or run it manually. However, slotscheck violations are fairly
rare.

On vscode, you can simply install the following extensions:

- [pylance (pyright)](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)
- [ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)

Note that with Pylance, you will also need to enable the type checking mode, by setting
`"python.analysis.typeCheckingMode": "basic"` in `settings.json`. You can use `.vscode/settings.json` for per-project
settings, to only enable type-checking for this project, or enable it globally in your user settings).

(Similarly to neovim, there is no extension available for slotscheck, however violations are fairly rare, and it should
be enough to have it run with pre-commit.)

## Making Great Commits

A well-structured git log is key to a project's maintainability; it provides insight into when and why things were done
for future maintainers of the project.

Commits should be as narrow in scope as possible. Commits that span hundreds of lines across multiple unrelated
functions and/or files are very hard for maintainers to follow. After about a week, they'll probably be hard for you to
follow too.

Please also avoid making a lot minor commits for fixing test failures or linting errors. Instead, run the linters before
you push, ideally with [pre-commit](#pre-commit).

We've compiled a few resources on making good commits:

- <https://itsdrike.com/posts/great-commits/>
- <https://chris.beams.io/posts/git-commit/>
- <https://dhwthompson.com/2019/my-favourite-git-commit>
- <https://thoughtbot.com/blog/5-useful-tips-for-a-better-commit-message>
- <https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html>

## Work in Progress PRs

Whenever you add a pull request that isn't yet ready to be reviewed and merged, you can mark it as a draft. This
provides both visual and functional indicator that the PR isn't yet ready to be reviewed and merged.

This feature should be utilized instead of the traditional method of prepending `[WIP]` to the PR title.

Methods of marking PR as a draft:

1. When creating it

   ![image](https://user-images.githubusercontent.com/20902250/94499351-bc736e80-01fc-11eb-8e99-a7863dd1428a.png)

2. After it was created

   ![image](https://user-images.githubusercontent.com/20902250/94499276-8930df80-01fc-11eb-9292-7f0c6101b995.png)

For more info, check the GitHub's documentation about this feature
[here](https://github.blog/2019-02-14-introducing-draft-pull-requests/)

## Don't reinvent the wheel

We're an open-sourced project, and like most other open-sourced projects, we depend on other projects that already
implemented many things which we need in our code. It doesn't make a lot of sense to try and implement everything from
the bottom, when there already are perfectly reasonable and working implementations made.

In most of the cases, this will mean using some libraries which can simply be added to our [project's
dependencies](./pyproject.toml) which is maintained with poetry, which you can read more about in [this
section](#project-installation).

Libraries aren't the only way to make use of the existing open-source code that's already out there. Another
thing which we can often do is simply directly copy open-source code into our project. However always make sure that
before even considering to paste someones code into ours, you have the right to do so given to you by the code's
author. This could be a directly given permission, but in most of cases, it will be an open-source license allowing
anyone to use the code it applies to as long as the conditions of that license are followed.

We all stand on the shoulders of giants even just by using the python language. There were some very smart people
behind implementing this language or the libraries that our project uses and they deserve the credit for their hard
work as their license specifies. To do this, we use the [`ATTRIBUTION.txt`](./ATTRIBUTION.txt) file.

This project is released under the LGPL v3 license and this means we can utilize the code of LGPL v3 libraries as well
as the permissive licenses (such as MIT, Apache or BSD licenses), it also means that when you contribute to our
project, you agree that your contributions may appear on other projects accordingly to the LGPL license (however you
may choose to later publish your code under any other license).

LGPL v3 is a "copy-left" license, which ensures that your code will always remain open-sourced and it will never be
relicensed (unless you give your permission as the copyright holder of your code). If for some reason you don't want to
contribute under a copy-left license but rather under MIT, or other permissive license, you are free to do so, just
mention whatever parts you added in the attribution file with your license's full-text with a copyright notice that
includes your name and a link to the original source (if you just made that code up, instead of a link to the original
source, you can just include a link to your GitHub profile, or just use your git email address.)

- How software licenses work: <https://itsdrike.com/posts/software-licenses/>
- GitHub's docs on licenses: <https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository>

## Changelog

It is important for the users to know what has changed in between the release versions, for that reason, we keep
a changelog, which is handled by a library called `towncrier`. Information about how this changelog works in detail is
described in it's own file at: [`./changes/README.md`](./changes/README.md).

Do make sure to read this file, as we generally require a changelog fragment file to be added with each pull request.
A PR without this file will NOT be accepted (unless there is a reason not to include a changelog - like for minor
fixes, or other exceptions).

## Unit-Tests

To ensure that our project will work correctly with any new changes made to it, we use automated unit-tests which test
the individual functions in our code with some sample inputs for correct outputs. Unit-testing is explained in better
detail in it's own file at [`./tests/README.md`](./tests/README.md).

## Deprecations

The removal or rename of anything that is a part of the public API must go through a deprecation process. This will
ensure that users won't be surprised when we eventually remove some features, and their code won't end up broken after
an update. Instead, a deprecated call should produce a warning about the deprecation, where the user is informed at
which version will the accessed object be removed. Until then, the object must have the same old behavior and shouldn't
break existing code-bases.

The project already contains some internal utilities that can help up mark something as deprecated easily, here's a few
quick examples of these utilities in practice:

```python
# Old version:
class Car:
    def __init__(self, engine_power: int, engine_type: str, fuel_tank_size: int):
        self.engine_power = engine_power
        self.engine_type = engine_type
        self.fuel_tank_size = fuel_tank_size

# New version, with deprecations preventing old code from breaking:
from mcproto.utils.deprecation import deprecated

class Car:
    def __init__(self, engine: Engine, fuel_tank_size: int):
        self.engine = engine
        self.fuel_tank_size = fuel_tank_size

    @deprecated(removal_version="2.0.0", replacement="engine.power")
    @property
    def engine_power(self) -> int:
        return self.engine.power

    @deprecated(removal_version="2.0.0", replacement="engine.type")
    @property
    def engine_power(self) -> int:
        return self.engine.type
```

```python
# Old version:
def print_value(value: str, add_version: bool) -> None:
    txt = "The value "
    if add_version:
        txt += f"for version {PROJECT_VERSION} "
    txt += f"is: {value}"
    print(txt)

# New version, with deprecation
from mcproto.utils.deprecation import deprecation_warn

def print_value(value: str, add_version: bool = False) -> None:
    txt = "The value "
    if add_version:
        deprecation_warn(obj_name="add_version argument", removal_version="4.0.0")
        txt += f"for version {PROJECT_VERSION} "
    txt += f"is: {value}"
    print(txt)

# New version, after version 4.0.0 (with deprecations removed):
def print_value(value: str) -> None:
    print(f"The value is: {value}")
```

## Changes to this Arrangement

We tried to design our specifications in a really easy and comprehensive way so that they're understandable to
everyone, but of course from a point of someone who already has some established standards, they'll usually always
think that their standards are the best standards, even though there may actually be a better way to do some things.
For this reason, we're always open to reconsidering these standards if there's a good enough reason for it.

After all every project will inevitably evolve over time, and these guidelines are no different. This document and the
standards it holds are open to pull requests and changes by the contributors, just make sure that this document is
always in sync with the codebase, which means that if you want to propose some syntactic change, you also change it
everywhere in the codebase so that the whole project will actually follow the newly proposed standards.

If you do believe that you have something valuable to add or change, please don't hesitate to do so in a PR (of course,
after you opened an issue, as with every proposed feature by a non-core developer).

## Footnotes

This could be a lot to remember at once, but you can use this document as a resource while writing the code for our
repository and cross-check that your styling is following our guidelines and that you're practicing the rules that
we've set here.

This document was inspired by
[Python Discord's CONTRIBUTING agreement.](https://github.com/python-discord/bot/blob/master/CONTRIBUTING.md).
