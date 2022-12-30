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
multiple areas. For example for PR #13 that both introduces a feature, and changes the documentation, can add
2 fragment files: `13.feature.md` and `13.docs.md`.

Additionally, if a single PR is addressing multiple unrelated topics in the same category, and needs to make multiple
distinct changelog entries, an optional counter value can be added at the end of the file name (needs to be an
integer). So for example PR #25 which makes 2 distinct internal changes can add these fragment files:
`25.internal.1.md` and `25.internal.2.md`. (The numbers in this counter position will not be shown in the final
changelog and are merely here for separation of the individual fragments.)

However if the changes are related to some bigger overarching goal, you can also just use a single fragment file with
the following format:

```markdown
Update changelog
- Rename `documentation` category to shorter: `docs`
- Add `internal` category for changes unrelated to public API, but potentially relevant to contributors
- Add github workflow enforcing presence of a new changelog fragment file for each PR
    - For insignificant PRs which don't require any changelog entry, a maintainer can add `skip-fragment-check` label.
```

That said, if you end up making multiple distinct changelog fragments like this, it's a sign that your PR is probably
too big, and you should split it up into multiple PRs instead. Making huge PRs that address several unrelated topics at
once is generally a bad practice, and should be avoided. If you go overboard, your PR might even end up getting closed
for being too big, and you'll be required to split it up.

## Footnotes

For more info, check out the [documentation](https://towncrier.readthedocs.io/en/latest/tutorial.html) for the
`towncrier` project.
