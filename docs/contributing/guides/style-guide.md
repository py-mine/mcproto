!!! bug "Work In Progress"

    This page is still being written. The content below (if any) may change.

# Style Guide

???+ abstract

    This page describes how we use `ruff` to enforce a consistent code style in our project.

For clarity and readability, adhering to a consistent code style across the whole project is very important. It is not
unusual that style adjustments will be requested in pull requests.

It is always a good practice to review the style of the existing code-base before and to adhere to that established
style before adding something new. That applies even if it isn't the code style you generally prefer. (That said, if
you think a code style change of some kind would be justified, feel free to open an issue about it and tell us why.)

!!! quote

    A style guide is about consistency. Consistency with this style guide is important. Consistency within a project
    is more important. Consistency within one module or function is the most important.

    However, know when to be inconsistent -- sometimes style guide recommendations just aren't applicable. When in
    doubt, use your best judgment. Look at other examples and decide what looks best. And don't hesitate to ask!

    — [PEP 8, the general Style Guide for Python Code](https://peps.python.org/pep-0008/)

## Automatic linting

As there is a lot of various code style rules we adhere to in our code base, describing all of them here would take way
too long and it would be impossible to remember anyway. For that reason, we use automated tools to help us catch any
code style violations automatically.

Currently, we use [`ruff`](https://beta.ruff.rs/docs/) to enforce most of our code style requirements. That said, we do
have some other tools that check the correctness of the code, we will describe those later.

### Ruff linter & formatter

Ruff is an all-in-one linter & formatter solution, which aims to replace three previously very popular tools into a
single package:

- [`flake8`](https://flake8.pycqa.org/en/latest/) linter
- [`isort`](https://pycqa.github.io/isort/) import sorter
- [`black`](https://black.readthedocs.io/en/stable/) auto-formatter

??? question "Why pick ruff over the combination of these tools?"

    There were multiple reasons why we chose ruff instead of using the above tools individually, here's just some of
    them:

    - Ruff is faster (written in rust! :crab:)
    - A single tool is more convenient than 3 separate ones
    - Ruff includes a lot of flake8 plugins with some great lint rules
    - Ruff has a great community and is slowly managing to overtake these individual projects
    - If you're already used to flake8, you'll feel right at home with ruff, it even has the same error codes (mostly)!

You can check the ruff configuration we're using in `pyproject.toml` file, under the `[tool.ruff]` category (and it's
subcategories). You can find which linter rules are enabled and which we choose to exclude, some file-specific
overrides where the rules apply differently and a bunch of other configuration options.

#### Linter

To run ruff linter on the code, open the terminal in the project's root directory and run:

```bash
ruff check .
```

!!! note ""

    Don't forget to [activate](./setup.md#activating-the-environment) the poetry virtual environment before running
    ruff.

Ruff is really smart and it can often automatically fix some of the style violations it found. To make ruff do that,
you can add the `--fix` flag to the command:

```bash
ruff check --fix .
```

If you got a rule violation in your code and you don't understand what the rule's purpose is supposed to be / why we
enforce it, you can use Ruff to show you some details about that rule. The explanation that ruff will give you will
often even contain code examples. To achieve this, simply run:

```bash
ruff rule [rule-id]
```

With the `[rule-id]` being the rule you're interested in, for example `UP038`.

??? tip "Use glow to render the markdown syntax from ruff rule command"

    The `ruff rule` command will output the rule explanation in markdown, however, since you're running this comand
    in a terminal, there won't be any helpful syntax highlighting for that by default.

    That's why I'd recommend using a markdown render such as [`glow`](https://github.com/charmbracelet/glow). With
    it, you can pipe the output from ruff into it and have it produce a fancy colored output, that's much easier to
    read: `ruff rule UP038 | glow`.

Alternatively, you can also find the rules and their description in the [ruff
documentation](https://docs.astral.sh/ruff/rules/).

#### Formatter

On top of being an amazing linter, ruff is also an automatic code formatter. That means ruff can actually make your
code follow a proper and style automatically! It will just take your original unformatted (but valid) python code and
edit it to meet our configured code style for you.

To make ruff format your code, simply run:

```bash
ruff format .
```

## Other style guidelines

While `ruff` can do a lot, it can't do everything. There are still some guidelines that you will need to read over and
apply manually. You will find these guides on the next pages of this documentation.
