# Contributing Guidelines

This project is fully open-sourced and all new contributions are welcome.

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
   but for bigger changes, an issue can save you a lot of time implementing something which may not even get accepted.
4. **Don't open a pull request if you aren't assigned to the issue.** If you want to work on some existing GitHub
   issue, it is always better to ask a maintainer to assign you to this issue. If there's already someone assigned to
   an issue, consider offering to collaborate with that person, rather than ignoring his work and doing it on your own.
   This method can help avoid having multiple people working on the exact same thing at the same time, without knowing
   about each other, which will often lead to multiple approaches solving the same thing, only one of which can be
   accepted (usually from the person who was originally assigned).
4. **Use assets licensed for public use.** Whenever a static asset such as images/video files/audio or even code is
   added, they must have a compatible license with our projects.
5. **Use draft pull requests if you aren't done yet.** If your PR isn't ready to be reviewed yet, mark it as draft.
   This is further described in [this section](#work-in-progress-prs)
6. **Follow our [Code of Conduct](./CODE-OF-CONDUCT.md).**

## Making Great Commits

A well-structured git log is key to a project's maintainability; it provides insight into when and why things were done
for future maintainers of the project.

Commits should be as narrow in scope as possible. Commits that span hundreds of lines across multiple unrelated
functions and/or files are very hard for maintainers to follow. After about a week, they'll probably be hard for you to
follow too.

Please also avoid making a lot minor commits for fixing test failures or linting errors. Just lint before you push as
described in [this category](#linting-and-precommit).

We've compiled a few resources on making good commits:

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
2. After it was crated

   ![image](https://user-images.githubusercontent.com/20902250/94499276-8930df80-01fc-11eb-9292-7f0c6101b995.png)

For more info, check the GitHub's documentation about this feature
[here](https://github.blog/2019-02-14-introducing-draft-pull-requests/)

## Don't reinvent the wheel

We're an open-sourced project, and like most other open-sourced projects, we depend on other projects that already
implemented many things which we need in our code. It doesn't make a lot of sense to try and implement everything from
the bottom, when there already are perfectly reasonable and working implementations made.

In most of the cases, this will mean using some libraries which can simply be added to our [project's
dependencies](./pyproject.toml) which is maintained with poetry, which you can read more about in [this
section](#setting-up-the-virtual-environment).

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

## Setting up the virtual environment

When contributing to our project, we recommend working from a virtual python environment instead of installing all of
our dependencies onto your system-wide python. Virtual environment is essentially a completely isolated python version
just for a given project. You should ideally use a virtual environment for any project which requires some external
dependencies, because always using the system python will inevitably lead to dependency collisions (one project you're
working on requires a different version of some dependency than other project).

To manage the virtual environment, this project uses [`poetry`](https://python-poetry.org/) for dependency management
and virtual environment. Poetry is a very powerful tool for managing virtual environments for python. If you're already
used to similar tools such as pipenv, or even just pure venv, you'll probably find it quite easy to use.

To use poetry, you will need to install it. If you're on linux, you can usually do this through your package manager,
but generally just installing with system-wide `pip` will do the trick. SO generally, you can just run `pip install
poetry` from your terminal to install it. After that, you'll want to navigate into the project's directory from the
terminal and run `poetry install`. This will create a new virtual environment for you, along with automatically
installing all of our dependencies for the project without having to worry about anything. You should also re-run this
command each time new dependencies are added, to stay in sync with the project.

After that, to work from within this virtual environment, you'll want to use `poetry shell` command, activating this
environment and therefore overriding your default system version of python to instead use the virtual environment's
version. You will need to work from an activated environment to be able to run all further commands specified in the
sections below, as they usually rely on the dependencies installed in this environment. Alternatively, you could also
instead use `poetry run my_command` to only execute a single command from the virtual environment without having to
activate it, however this will likely soon become annoying and just working from within an activated environment should
be easier.

For more info about poetry, make sure to check their amazing official documentation: `https://python-poetry.org/docs/`,
these include installation instructions, explain how to add new dependencies to the project, or how to remove some, and
everything else you'd need to know.

## Style Guide

For clarity and readability, adhering to a consistent code style across the whole project is very important. It is not
unusual that style adjustments will be requested in pull requests.

It is always a good practice to review the style of the existing code-base before adding something new, and adhere to
that established style. If you think a code style change is should be made, open an issue about it and tell us what
exactly should be changed, describe why you think this change is important and if you want to, you can also ask to be
assigned to the issue and work on changing the style in the code-base in a standalone PR just for that. (Hey you may
even get to edit this section!)

> A style guide is about consistency. Consistency with this style guide is important. Consistency within a project is
> more important. Consistency within one module or function is the most important.
>
> However, know when to be inconsistent -- sometimes style guide recommendations just aren't applicable. When in doubt,
> use your best judgment. Look at other examples and decide what looks best. And don't hesitate to ask!
> — [PEP 8, the general Style Guide for Python Code](https://peps.python.org/pep-0008/)

### Automated linters

Every python code should adhere to "PEP-8" styling (not just in our code-base). This is a relatively simple set of
guidelines defining how python code should look like, to remain readable and well maintainable. If you aren't familiar
with this standard, you can check the official [PEP 8 Guidelines](https://www.python.org/dev/peps/pep-0008/).

To check that your code meets these guidelines, we use a tool (or "linter") called
[`flake8`](https://flake8.pycqa.org/en/latest/). Flake8 can run checks on every python file in our code-base, and
verify that it meets all of the rules it contains. These rules fully capture all of the PEP-8 guidelines, along with
some other extra rules which are more unique to flake8 directly. On top of these flake8 rules, we also have some
extensions to flake8, which add other specialized rules, such as for enforcing the presence of type annotations.

But flake8 isn't the only linter we use in the code-base. We're also utilizing `black`, which is not just a linter, but
also an auto-formatter, meaning running it can edit the source-code on it's own, and fix the issues it finds for you.
This can often save you a lot of time and means you don't need to deeply study all of the guidelines and styling rules,
and instead just let a simple tool handle it all for you.

The last linter, and also an auto-formatter tool which we're using is `isort`. We use isort for automatic sorting of
our import statements in alphabetical order, and into 3 general groups: standard library imports, external imports
(installed with pip) and internal/project imports.

Combining all of these tools makes up for a very clean code-base which is very easy to maintain. However running all of
these tools constantly can get very annoying. For that reason, we make use of `pre-commit`, which can run them for us
automatically before each commit. This will be later described in better detail in
[it's own section](#linting-and-precommit) below.

To make sure that everything works as it should and to save some time on reviewing issues in code formatting, we use an
automated [validation workflow](./.github/workflows/validation.yml). This workflow runs these checks automatically the
moment you push some code to GitHub. However it is important that you run the linters locally instead of just relying
on this workflow. Not only does this avoid making a lot of unnecessary fixing commits, it also saves you time, because
it takes a while for the workflow to run, and running the linters locally is way faster. But the biggest reason we ask
you not to rely on these workflows is that we have a limited amount of concurrent workflows, so please don't abuse
them.

### Linting and Precommit

Linting is the process of running some form of linter on the code-base. As mentioned above, we use several of these
linters to ensure that the codebase stays clean and maintainable. You can run these linters individually, by running
these commands from the terminal (from within an with activated virtual environment, and while in the root of the
repository):

- **Flake8**: `flake8 .`
- **Black**: `black .`
- **Isort**: `isort .`

It is important that we make sure to lint before pushing, because it can avoid needlessly making a lot of commits just
to fix the linting issues and pass the workflow checks or meet additional requested styling. However running all of
these commands before every commit can quickly get very annoying, and people also tend to forget to run them. To solve
this issue we use a tool called `pre-commit`.

Pre-commit is a tool utilizing the pre-commit [git hook](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks) that
runs before every commit you make, and is able to stop that commit if some linter reported a failure. To install
pre-commit hook all you need to do is to run `poetry run task precommit` which will add the git-hook and pre-commit
will now run before each new commit you make and will stop you from committing badly-linted code.

In our [`.pre-commit-config.yaml`](./.pre-commit-config.yaml), we define several checks to be ran before committing,
which are here to enforce our styling guidelines and correct typing. These include flake8, black and isort, but there
are some other things too, such as a linter for TOML/YAML files.

By default, once you make a commit, pre-commit will only run on the edited files. If you want to run `pre-commit` on
all files in the project, or if you just want to run it as a lint check without having to make a commit, you can do so
by running `poetry run task lint` command.

Even though in most cases enforcing linting before each commit is what we want, there are some situations where
we need to commit some code which doesn't pass these checks. This can happen for example after a merge, or as a result
of making a single purpose small commit without yet worrying about linters. In these cases, you can use the
`--no-verify` flag when making a commit, telling git to skip all of the pre-commit hooks and commit normally.

However this kind of verification skipping should only be used sparingly, as we do value a clean history which
consistently follows our linting guidelines, you should avoid from making too many commits skipping the linting, only
to then make one big commit fixing all of the linting issues. And when you do need to use it, you should wait until you
make another commit where linting is resolved until you push, to avoid needlessly failing the automated workflows on
GitHub which run pre-commit themselves (amongst other things).

### Type hinting

[PEP 484](https://www.python.org/dev/peps/pep-0484/) formally specifies type hints for Python functions, added to the
Python Standard Library in version 3.5. Type hints are recognized by most modern code editing tools and provide useful
insight into both the input and output types of a function, preventing the user from having to go through the codebase
to determine these types.

For example, a non-annotated function can look like this:

```python
def divide(a, b):
    """Divide the two given arguments."""
    return a / b
```

With annotation, the function looks like this:

```python
def divide(a: int, b: int) -> float:
    """Divide the two given arguments."""
    return a / b
```

Some great resources for learning about python type-hints:

Thankfully python type-hinting is fairly easy to understand, but if you do want to see some rather interesting
resources for a bit more advanced concepts such as type variables or some python specific types like `typing.Callable`,
we've compiled a quick list of really amazing resources about these type hinting practice.

- Python documentation from `typing` library: <https://docs.python.org/3/library/typing.html>
- MyPy documentation (very extensive but quite beginner friendly): <https://mypy.readthedocs.io/en/stable/>
- Decorator Factory blog about typing: <https://decorator-factory.github.io/typing-tips/>
- Typing Generics (advanced): <https://itsdrike.com/posts/typing-generics/>

### Enforcing type hints - Type checker

Even though the type hints can be pretty useful in knowing what the function variables are expected to be and they also
provide better auto-completion, if we're not careful, we could soon end up violating our own type specifications,
because by default python doesn't enforce these type-hints in any way.

To give ensure that our code-base is correct type-wise, we use a tool that goes through the code (similarly to a
linter), just to analyze the specified types and tell us if our current use of these types makes sense. Using a
type-checker is very beneficial to a code-base, because it can quickly catch mistakes we made based on purely the
types, without relying purely on unit-tests, which may not cover everything.

There are many python type-checkers available, the most notable ones being `mypy` and `pyright`. We decided to use
`pyright`, because it has great support for newer typing features and is quick to update and bug fixing. Pyright can be
used from the terminal as a stand-alone linter-like checker, by simply running `pyright .` (from within an activated
virtual environment), however we include it in our pre-commit checks, to ensure type-correctness before each commit.

Pyright is one of the fastest type-checkers out there (at least when it comes to type-checkers that also support a lot
of the newer features), however it still needs to perform some very complex logic for this type analysis and can take a
while to run (a few seconds). This isn't too long, but it may get a bit annoying to have to run it before each commit.
If you prefer to run pre-commit without pyright, you can specify `SKIP=pyrigt` environmental variable, which will skip
this check in pre-commit, however make sure to run it at least before you push your code to GitHub to avoid unnecessary
failures on our workflows.

Pyright can also be used as an extension to VSCode, as it is a part of Pylance (an extension installed by default with
the Python extension). However type-checking is disabled by default, so if you want to use it like that, you will need
to set `"python.languageServer": "Pylance"` and `"python.analysis.typeCheckingMode": "basic"` in settings. Pyright can
also be used as a base language server for almost any editor, you just need to figure out how to get your editor to
pick it up.

### Quotes

Preference is to use double-quotes (`"`) wherever possible. Single quotes should only be used for cases where it is
logical. Exceptions might include:

- Using a key string within an f-string: f"Today is {data['day']}".
- Using double quotes within a string: 'She said "oh dear" in response'

Docstrings/Multiline strings must always be wrapped in 3 double quotes (`"""my string"""`).

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
