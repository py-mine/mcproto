# Changelog fragments

???+ abstract

    This page describes our use of `towncrier` for the project's changelog. It explains the different changelog
    categories, the process of creating changelog fragment files and generating a changelog preview. Additionally, the
    page contains a guide on writing good changelog fragments.

Our project contains a changelog which tracks all notable changes for easy and quick reference to both users and our
contributors.

To maintain our changelog, we're using [`towncrier`][towncrier], which allows us to create **fragment files**, which
each contains a single changelog entry. Once a new release is created, all of these fragments will be used to create a
changelog for that new release.

We generally require every pull request to to include a new changelog fragment, summarizing what it does.

!!! note

    If you think your change shouldn't require a changelog entry (it's a small / simple change that isn't worth
    noting), ask us to add the `skip-fragment-check` label to your PR, which will disable the automated check that
    enforces a presence of the changelog fragment.

## Structure of a fragment file

The fragment files are stored in the `changes/` directory in our project. These files follow the following naming
format: `{pull_request_number}.{type}.md`.

Possible fragment types are:

- **`feature`**: New feature that affects the public API.
- **`bugfix`**: A bugfix, which was affecting the public API.
- **`docs`**: Change to the documentation, or updates to public facing docstrings
- **`breaking`**: Signifying a breaking change of some part of the project's public API, which could cause issues for
  end-users updating to this version. (Includes deprecation removals.)
- **`deprecation`**: Signifying a newly deprecated feature, scheduled for eventual removal.
- **`internal`** Fully internal change that doesn't affect the public API, but is significant enough to be mentioned,
  likely because it affects project contributors. (Such as a new linter rule, change in code style, significant change
  in internal API, ...)

## Create fragments with commands

While you can absolutely create these files manually, it's often a lot more convenient to use the `towncrier` CLI,
which can create the file for you in the proper place automatically. With it, you can simply run:

```bash
towncrier create {pull_request_number}.{type}.md
```

After you ran the command, a new file will appear in the `changes/` directory. You can now open it and describe your
change inside of it.

If the change is simple enough, you can even use the `-c` / `--content` flag to specify it directly, like:

```bash
towncrier create 12.feature.md -c "Add dinosaurs!"
```

!!! tip "Terminal editors"

    If you're used to terminal editors, there's also an `--edit` flag, which will open the file with your
    `$EDITOR`. (I would recommend `neovim`, but if you find it too complex, `nano` also works well)

    Alternatively, you should also be able to set `$EDITOR` to `code` and edit the fragment from vscode, or
    whatever other GUI editor, that said, a terminal editor is likely going to be more convenient here.

### Knowing the PR number

One problem that you'll very likely face is not knowing the PR number ahead of the time, as it's only assigned once you
actually open the PR and towncrier does require you to specify it as a part of the file name, which means you can only
create changelog fragments after opening the PR. (You can sometimes guess the number, as they are sequential, but you
risk someone opening an issue / another PR and taking it.)

If you're concerned about commit history, good new, we allow force pushing (especially soon after creation, but in
feature branches, even generally). This means you can simply open the PR, then add your changelog fragment, amend your
original commit and force-push. E.g.:

```bash
git checkout -b my-feature-branch
git add mcproto/file_i_changed.py
git commit -m "My cool change"
git push
gh pr create --title "My cool change" --body "This change will blow your mind"
gh pr view --json number -q .number  # get the PR number
towncrier create [number].feature.md -c "Add an incredible change"
git commit --amend --no-edit
git push --force
```

That said, it's also perfectly fine to just include it in a new commit, if you prefer that:

```bash
git checkout -b my-feature-branch
git add mcproto/file_i_changed.py
git commit -m "My cool change"
git push
gh pr create --title "My cool change" --body "This change will blow your mind"
gh pr view --json number -q .number  # get the PR number
towncrier create [number].feature.md -c "Add an incredible change"
git commit -m "Add changelog fragment for #[number]"
git push
```

!!! tip "Automate getting the PR number with poe task"

    In the example above, we obtained the PR number with an additional command. You could also have just looked at the
    GitHub interface and searched for your new PR, or extracted it from the link that `gh pr create` shows you. That
    said, all of these can be a bit too annoying, and for that reason, we actually have a `poe` task for convenience
    here, with which, you can simply do:

    ```bash
    poe changelog-this feature -- -c "My incredible change"
    ```

    This will automatically pick up the PR number (with the same GitHub CLI command used in the example) and run the
    `towncrier` command with it.

## Multiple fragments in a single PR

If necessary, multiple fragment files can be created per pull-request, with different change types, if the PR covers
multiple areas. For example for PR #13 that both introduces a feature, and changes the documentation, can add 2
fragment files: `13.feature.md` and `13.docs.md`.

Additionally, if a single PR is addressing multiple unrelated topics in the same category, and needs to make multiple
distinct changelog entries, an optional counter value can be added at the end of the file name (needs to be an
integer). So for example PR #25 which makes 2 distinct internal changes can add these fragment files:
`25.internal.1.md` and `25.internal.2.md`. (The numbers in this counter position will not be shown in the final
changelog and are merely here for separation of the individual fragments.)

However if the changes are related to some bigger overarching goal, you can also just use a single fragment file with
the following format:

```markdown title="changes/25.internal.md"
Update towncrier categories

    - Rename `documentation` category to shorter: `docs`
    - Add `internal` category for changes unrelated to public API, but potentially relevant to contributors
    - Add github workflow enforcing presence of a new changelog fragment file for each PR
        - For insignificant PRs which don't require any changelog entry, a maintainer can add `skip-fragment-check` label.
```

!!! warning

    While possible, if you end up making multiple distinct changelog fragments like this, it's a sign that your PR
    might be too big, and you should split it up into multiple PRs instead. Making huge PRs that address several
    unrelated topics at once is generally a bad practice, and should be avoided. If you go overboard, your PR might
    even end up getting closed for being too big, and you'll be required to split it up.

## Preview changelog

To preview the latest changelog, run `towncrier build --draft --version latest`.

??? note "Meaning of the version value"

    The `--version` attribute usually takes the version number of the project, to which these changes apply. However,
    since we just want to preview the changes, it doesn't really matter for us, so we can just pass `latest` or
    whatever else you wish.

    For actual builds, the version is automatically obtained and this command is executed in our release CI workflow.

    This version will be used in the first line of the changelog (the header).

??? note "Meaning of --draft flag"

    The `--draft` flag will make sure that towncrier will only show you the contents of the next changelog version
    entry, but won't actually add that generated content to our `CHANGELOG.md` file, while consuming (removing) the
    changelog fragments.

    You will never need to run `towncrier` without the `--draft` flag, as our CI workflows for project releasing handle
    that automatically.

To make this a bit easier, there is a poe command running the command above, so you can just use `poe changelog-preview`
to see the changelog, if you don't like remembering new commands.

## Writing good changelog fragments

Fragment files follow the same markdown syntax as our documentation.

The contents of a fragment file should describe the change that you've made in a quick and general way. That said, the
change descriptions can be a bit more verbose than just the PR title, but only if it's necessary. Keep in mind that
these changes will be shown to the end users of the library, so try to explain your change in a way that a
non-contributor would understand.

!!! tip

    If your change needs some more in-depth explanations, perhaps with code examples and reasoning for why such a
    change was made, use the PR body (description) for this purpose. Each changelog entry will contain a link to the
    corresponding pull request, so if someone is interested in any additional details about a change, they can always
    look there.

### Examples of good changlog fragment files

:material-check:{ style="color: #4DB6AC" } **Clear and descriptive**

```markdown title="changes/171.feature.md"
Add `Account.check` function, to verify that the access token in use is valid, and the data the Account instance has matches the data minecraft API has.
```

```markdown title="changes/179.docs.md"
Enforce presence of docstrings everywhere with pydocstyle. This also adds docstring to all functions and classes that didn't already have one. Minor improvements for consistency were also made to some existing docstrings.
```

:material-check:{ style="color: #4DB6AC" } **Slightly on the longer side, but it's justified** (Sometimes, it's
important to explain the issue that this fixes, so that users know that it was there)

```markdown title="changes/330.bugfix.md"
Fix behavior of the `mcproto.utils.deprecation` module, which was incorrectly always using a fallback version, assuming mcproto is at version 0.0.0. This then could've meant that using a deprecated feature that is past the specified deprecation (removal) version still only resulted in a deprecation warning, as opposed to a full runtime error.
```

:material-check:{ style="color: #4DB6AC" } **With an extra note about the breaking change** (Adding some extra
description isn't always bad, especially for explaining how a breaking change affects existing code)

```markdown title="changes/130.breaking.md"
Renamed "shared_key" field to "shared_secret" in `LoginEncryptionPacket`, following the official terminology.

    This is a breaking change as `LoginEncryptionPacket`'s `__init__` method now uses "shared_secret" keyword only
    argument, not "shared_key". Every initialization call to this packet needs to be updated.
```

:material-check:{ style="color: #4DB6AC" } **With a list of subchanges that were made** (Be careful with this one
though, make sure you don't over-do it)

```markdown title="changes/129.feature.md"
Added a system for handling Minecraft authentication

    - Yggdrasil system for unmigrated i.e. non-Microsoft accounts (supportng Minecraft accounts, and the really old
      Mojang accounts)
    - Microsoft OAuth2 system (Xbox live) for migrated i.e. Microsoft accounts
```

### Examples of bad changelog fragment files

:material-close:{ style="color: #EF5350" } **Unclear** (But what does this class do?)

```markdown title="changes/123.feature.md"
Update `Buffer` class.
```

:material-close:{ style="color: #EF5350" } **Bad category** (This is a feature, not a bugfix)

```markdown title="changes/161.bugfix.md"
Add support for encryption. Connection classes now have `enable_encryption` method, and some encryption related functions were added into a new mcproto.encryption module.
```

:material-close:{ style="color: #EF5350" } **Starts with dash** (Sometimes, it can feel natural to start your changelog
entry with a `-`, as it is a list item in the final changelog, however, this dash will already be added automatically)

```markdown title="changes/171.feature.md"
- Add `Account.check` function, to verify that the access token in use is valid, and the data the Account instance has matches the data minecraft API has.
```

:material-close:{ style="color: #EF5350" } **Wrapped first line** (Splitting up the first line into multiple lines is
something we often do in markdown, because it should still be rendered as a single line, however, because of how
towncrier merges these fragments, using multiple lines will cause issues and the changelog won't be formatter
correctly! Further blocks can have wrapped lines.)

```markdown title="changes/330.bugfix.md"
Fix behavior of the `mcproto.utils.deprecation` module, which was incorrectly always using a fallback version, assuming
mcproto is at version 0.0.0. This then could've meant that using a deprecated feature that is past the specified
deprecation (removal) version still only resulted in a deprecation warning, as opposed to a full runtime error.
```

:material-close:{ style="color: #EF5350" } **No indent in description** (Sometimes, we want to add additional
description to our changelog entry. When doing so, we need to make sure that the description block is indented with 4
spaces and there is a blank line after the first / title line.)

```markdown title="changes/330.breaking.md"
Renamed "shared_key" field to "shared_secret" in `LoginEncryptionPacket`, following the official terminology.

This is a breaking change as `LoginEncryptionPacket`'s `__init__` method now uses "shared_secret" keyword only
argument, not "shared_key". Every initialization call to this packet needs to be updated.
```

:material-close:{ style="color: #EF5350" } **Way too long** (This should've been the PR description)

```markdown title="changes/161.feature.md"
Introduce support for encryption handling.

    Most servers (even offline ones) usually send an EncryptionRequest packet during the LOGIN state, with a public
    (RSA) key that the client is expected to use to encrypt a randomly generated shared secret, to send back to the
    server in EncryptionResponse packet. After that, all further communication is encrypted with this shared secret.

    The encryption used is a AES/CFB8 stream cipher. That means the encrypted ciphertext will have the same amount
    of bytes as the original plaintext, allowing us to still trust our reader/writer methods that rely on reading
    specific amounts of bytes, even if their content don't make sense.

    This directly uses the base connection classes and adds enable_encryption method to them, which after getting
    called will automatically encrypt/decrypt any incomming/outcomming data.

    This additionally also changes the LoginEncryptionRequest packet class, and makes the public key attribute
    actually hold an RSA public key (from the cryptography library), instead of just the received bytes. This is
    then much more useful to work with later on. This is a breaking change.
```

!!! tip "Verify if your changelog works"

    Our CI will automatically build the documentation for your PR and post a link to it as a comment in the pull
    request. This documentation will include a preview of the changelog with all unreleased changes in the [changelog]
    page. You can take a look there to make sure that your change fragment(s) resulted in the proper output.

!!! note "Internal changes"

    We're a bit more forgiving when it comes to describing your change if your change is in the `internal` category, as
    end users don't need to read those. Changes in this category can be a bit less descriptive.

## Footnotes

- See <https://keepachangelog.com> for more info about why and how to properly maintain a changelog
- For more info about `towncrier`, check out it's [documentation][towncrier-tutorial]

[towncrier]: https://towncrier.readthedocs.io/en/stable/
[towncrier-tutorial]: https://towncrier.readthedocs.io/en/stable/tutorial.html
[changelog]: ../../meta/changelog.md
