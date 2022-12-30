# Changelog fragments

This folder holds fragments of the changelog to be used in the next release, when the final changelog will be
generated.

For every pull request made to this project, the contributor is responsible for creating a file (fragment), with
a short description of what that PR changes.

These fragment files use the following format: `{pull_request_number}.{type}.md`,

Possible types are:
- **`feature`**: New feature that affects the public API.
- **`bugfix`**: A bugfix, which was affecting the public API.
- **`docs`**: Change to the documentation, or updates to public facing docstrings
- **`breaking`**: Signifying a breaking change of some part of the project's public API, which could cause issues for
  end-users updating to this version. (Includes deprecation removals.)
- **`deprecation`**: Signifying a newly deprecated feature, scheduled for eventual removal.
- **`internal`** Fully internal change that doesn't affect the public API, but is significant enough to be mentioned,
  likely because it affects project contributors. (Such as a new linter rule, change in code style, significant change
  in internal API, ...)

For changes that do not fall under any of the above cases, please specify the lack of the changelog in the pull request
description, so that a maintainer can skip the job that checks for presence of this fragment file.

## Create fragments with commands

While you absolutely can simply create these files manually, it's a much better idea to use the `towncrier` library,
which can create the file for you in the proper place. With it, you can simply run `towncrier create
{pull_request}.{type}.md` after creating the pull request, edit the created file and commit the changes.

If the change is simple enough, you can even use the `-c`/`--content` flag and specify it directly, like: `towncrier
create 12.feature.md -c "Add dinosaurs!"`, or if you're used to terminal editors, there's also the `--edit` flag, which
opens the file with your `$EDITOR`.

## Preview changelog

To preview the latest changelog, run `towncrier build --draft --version [version number]`. (For version number, you can
pretty much enter anything as this is just for a draft version. For true builds, this would be the next version number,
so for example, if the current version is 1.0.2, next one will be one either 1.0.3, or 1.1.0, or 2.0.0. But for drafts,
you can also just enter something like `next` for the version, as it's just for your own private preview.)

To make this a bit easier, there is a taskipy task running the command above, so you can just use `poetry run task
changelog-preview` to see the changelog, if you don't like remembering new commands.

## Multiple fragments in single PR

If necessary, multiple fragment files can be created per pull-request, with different change types, if the PR covers
multiple areas (for example a PR that both introduces a feature, and changes the documentation).

Additionally, if a single PR is addressing multiple unrelated topics in the same category, and needs to make multiple
distinct changelog entries, you can do so by adding an optional counter value to the fragment file name, which needs to
be an integer, for example: `25.internal.1.md` and `25.internal.2.md`. This counter value will not be shown in the
final changelog and is merely here for separation of the individual fragments.

That said, if you end up making multiple distinct changelog fragments like this is a good sign that your PR is probably
too big, and you should split it up into multiple PRs. Making huge PRs that address several unrelated topics at once
are generally a bad practice, and should be avoided.

## Footnotes

For more info, check out the [documentation](https://towncrier.readthedocs.io/en/latest/tutorial.html) for the
`towncrier` project.
