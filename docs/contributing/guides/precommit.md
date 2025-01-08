# Pre-commit

???+ abstract

    This guide explains what is pre-commit and how to set it up as a git hook that will run automatically before your
    commits. It also describes how to run pre-commit manually from the CLI, how to skip some or all of the individual
    checks it performs, what happens when hooks edit files and where it's configuration file is.

Now that you've seen the linters, formatters, type-checkers and other tools that we use in the project, you might be
wondering whether you're really expected to run all of those commands manually, after each change. And of course, no,
you're not, that would be really annoying, and you'd probably also often just forget to do that.

So, instead of that, we use a tool called [`pre-commit`](https://pre-commit.com/), which creates a [git
hook](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks), that will automatically run before each commit you
make. That means each time when you make a commit, all of these tools will run over the code you updated, and if any of
these linters detects an issue, the commit will be aborted, and you will see which linter failed, and it's output
telling you why.

## Installing pre-commit

To install pre-commit as a git hook all you need to do is to run:

```bash
pre-commit install
```

This will install pre-commit as a git hook into your git repository, which will mean it will run automatically before
every new commit you make.

!!! warning

    Pre-commit itself will be installed via poetry, which means you will need to have an
    [activated](./setup.md#activating-the-environment) poetry environment whenever you make a new commit, otherwise,
    the pre-commit git hook will fail with command not found.

## Hooks that modify files

Sometimes, hooks can end up modifying your files, for example the ruff format hook may do so if your file wasn't
already formatted by ruff. When this happens, the hook itself will fail, which will make git abort the commit. At this
point, you will be left with the original changes still staged, but some files may have been modified, which means
you'll want to `git add` those again, staging these automatic modifications and then make the commit again.

Note that in case you were only committing a [partial change](./great-commits.md#partial-adds), which means you still
had some parts of the file unstaged, pre-commit will not modify the files for you. Instead, the hook will just fail,
leaving the rest up to you. You should now run the formatter yourself and perform another partial add, updating the
staged changes to be compliant.

## Running manually

Even though in most cases, it will be more than enough to have pre-commit run automatically as a git hook,
sometimes, you may want to run it manually without making a commit.

!!! tip

    You can run this command without having pre-commit installed as a git hook at all. This makes it possible to avoid
    installing pre-commit and instead running all checks manually each time. That said, we heavily recommend that you
    instead install pre-commit properly, as it's very easy to forget to run these checks.

To run pre-commit manually you can use the following command:

```bash
pre-commit run --all-files
```

Using this command will make pre-commit run on all files within the project, rather than just running against the
git staged ones, which is the behavior of the automatically ran hook.

## Skipping pre-commit

!!! info "Automatic skipping"

    Pre-commit is pretty smart and will skip running certain tools depending on which files you modified. For example
    some hooks only check the validity of Python code, so if you haven't modified any Python files, there is no need to
    run those hooks.

Even though in most cases enforcing linting before each commit is what we want, there are some situations where we need
to commit some code which doesn't pass these checks. This can happen for example after a merge, or as a result of
making a single purpose small commit without yet worrying about linters. In these cases, you can use the `--no-verify`
flag when making a commit, telling git to skip the pre-commit hooks and commit normally. When making a commit, this
would look like:

```bash
git commit -m "My unchecked commit" --no-verify
```

You can also only skip a specific hook, by setting `SKIP` environmental variable (e.g. `SKIP=basedpyright`) or even
multiple hooks (`SKIP=ruff-linter,ruff-formatter,slotscheck`). When making a commit, this would look like:

```bash
SKIP="check-toml,slotscheck,basedpyright" git commit -m "My partially checked commit"
```

!!! note ""

    The names of the individual hooks are their ids, you can find those in the [configuration file](#configuration) for
    pre-commit.

!!! warning

    This kind of verification skipping should be used sparingly. We value a clean history which consistently follows
    our linting guidelines, and making commits with linting issues only leads to more commits, fixing those issues later.

## Configuration

You can find pre-commit's configuration the `.pre-commit-config.yaml` file, where we define which tools should be ran
and how. Currently, pre-commit runs ruff linter, ruff formatter, slotscheck and basedpyright, but also a checker for
some issues in TOML/YAML files.
