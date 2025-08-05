# Bug Reports & Feature Requests

Mcproto is an actively maintained project, and we welcome contributions in the form of both bug reports and feature
requests. This guide will help you understand how to effectively submit an issue, whether it's reporting a bug or
proposing a new feature.

## Before creating an issue

Before opening a new issue with your bug report, please do the following things:

### Upgrade to latest version

Chances are that the bug you discovered was already fixed in a subsequent version. Thus, before reporting an issue,
ensure that you're running the [latest version][changelog] of mcproto.

!!! warning "Bug fixes are not backported"

    Please understand that only bugs that occur in the latest version of mcproto will be addressed. Also, to reduce
    duplicate efforts, fixes cannot be backported to earlier versions.

    Please understand that only bugs that occur in the latest version will be addressed. Also, to reduce duplicate
    efforts, fixes cannot be backported to earlier versions, except as a hotfix to the latest version, diverging from
    the not yet finished features, even if already in the `main` branch.

    Due to the nature of our [versioning], that might mean that if you require an older version of minecraft protocol,
    you might be stuck with an older, buggy version of this library.

### Search for existing issues

It's possible that the issue you're having was already reported. Please take some time and search the [existing
issues][issue tracker] in the GitHub repository for your problem. If you do find an existing issue that matches the
problem you're having, simply leave a :thumbsup: reaction instead (avoid commenting "I have this issue too" or similar,
as that ultimately just clutters the discussion in that issue, but if you do think that you have something meaningful to
add, please do).

!!! note

    Make sure to also check the closed issues. By default, github issue search will start with: `is:issue is:open`,
    remove the `is:open` part to search all issues, not just the opened ones. It's possible that we seen this issue
    before, but closed the issue as something that we're unable to fix.

In case you found a relevant issue, however, it has already been closed as implemented (not as declined / not planned),
but the bug / proposed feature is still somehow relevant, don't be worried to drop a comment on this older issue, we
will get notifications for those too. That said, if you think there is sufficient new context now, it might also make
sense to open a new issue instead, but make sure to at least mention the old issue if you choose this route.

## Creating a new issue

At this point, when you still haven't found a solution to your problem, we encourage you to create an issue.

We have some issue-templates ready, to make sure that you include all of the necessary things we need to know:

- For a **bug report**, you can click [here][open bug issue].
- For a **feature request**, you can instead click [here][open feature issue].

If you prefer, you can also [open a blank issue][open blank issue]. This will allow you to avoid having to follow the
issue templates above. This might be useful if your issue doesn't cleanly fit into either of these two, or if you prefer
to use your own categories and structure for the issue. That said, make please still make sure to include all of the
relevant details when you do so.

## Writing good bug reports

Generally, the GitHub issue template should guide you towards telling us everything that we need to know. However, for
the best results, keep reading through this section. In here, we'll explain how a well formatted issue should look like
in general and what it should contain.

### Issue Title

A good title is short and descriptive. It should be a one-sentence executive summary of the issue, so the impact and
severity of the bug you want to report can be inferred right from the title.

| <!---->                                                    | Example                                                              |
| ---------------------------------------------------------- | -------------------------------------------------------------------- |
| :material-check:{ style="color: #4DB6AC" } **Clear**       | Ping packet has incorrect ID                                         |
| :material-close:{ style="color: #EF5350" } **Wordy**       | The Ping packet has an incorrect packet ID of 0, when it should be 1 |
| :material-close:{ style="color: #EF5350" } **Unclear**     | Ping packet is incorrect                                             |
| :material-close:{ style="color: #EF5350" } **Non-english** | El paquete ping tiene una identificación incorrecta                  |
| :material-close:{ style="color: #EF5350" } **Useless**     | Help                                                                 |

### Bug description

Now, to the bug you want to report. Provide a clear, focused, specific and concise summary of the bug you encountered.
Explain why you think this is a bug that should be reported to us. Adhere to the following principles:

1. **Explain the <u>what</u>, not the <u>how</u>** – don't explain [how to reproduce the bug](#reproduction) here,
   we're getting there. Focus on articulating the problem and its impact as clearly as possible.
2. **Keep it short and concise** - if the bug can be precisely explained in one or two sentences, perfect. Don't
   inflate it - maintainers and future users will be grateful for having to read less.
3. **Don't under-explain** - don't leave out important details just to keep things short. While keeping things short is
   important, if something is relevant, mention it. It is more important for us to have enough information to be able
   to understand the bug, even if it means slightly longer bug report.
4. **One bug at a time** - if you encounter several unrelated bugs, please create separate issues for them. Don't
   report them in the same issue, as this makes it difficult for others when they're searching for existing issues and
   also for us, since we can't mark such an issue as complete if only one of the bugs was fixed.

---

:material-run-fast: **Stretch goal** – if you have a link to an existing page that describes the issue, or otherwise
explains some of your claims, include it. Usually, this will be a <https://minecraft.wiki> link leading to the
Minecraft protocol documentation for something.

:material-run-fast: **Stretch goal \#2** – if you found a workaround or a way to fix
the bug, you can help other users temporarily mitigate the problem before
we maintainers can fix the bug in our code base.

### Reproduction

A minimal reproducible example is at the heart of every well-written bug report, as it allows us maintainers to
instantly recreate the necessary conditions to inspect the bug and quickly find its root cause from there. It's a
proven fact that issues with concise and small reproductions can be fixed much faster.

Focus on creating a simple and small code snippet that we can run to see the bug. Do your best to avoid giving us large
snippets or whole files just for the purpose of the reproducible example, do your best to reduce the amount of code as
much as you can and try to avoid using external dependencies in the snippet (except for mcproto of course).

??? tip "How to include code-snippets (markdown)"

    In case you're not yet familiar with the syntax, GitHub issues use `markdown` format, which means you can use some
    nice custom formatting to make the text appear distinct. One of these formatting options is a source-code block /
    code snippet. To include one, you will want to use the following syntax:

    ````markdown
    ```language
    your code
    it can be multiline
    ```
    ````

    Note that the symbols used here aren't single quotes (`'`), they're backticks: `` ` ``.
    On an english keyboard, you can type these using the key right below escape (also used for tildes: `~`).

    The `language` controls how the code will be highlighted. For python, you can use `python`, for yaml, `yaml`, etc.

Sometimes, the bug can't be described in terms of code snippets, such as when reporting a mistake in the documentation.
In that case, provide a link to the documentation or whatever other relevant things that will allows us to see the bug
with minimal effort. In certain cases, it might even be fine to leave the reproduction steps section empty.

## Next steps

Once the issue is submitted, you have 2 options:

### Wait for us to address it

We will try to review your issue as soon as possible. Please be patient though, as this is an open-source project
maintained by volunteers, who work on it simply for the fun of it. This means that we may sometimes have other
priorities in life or we just want to work on some more interesting tasks first. It might therefore take a while for us
to get to your issue, but we try and do our best to respond reasonably quickly, when we can. Even when things are
slower, we kindly ask you to avoid posting comments like "Any progress on this?" as they are not helpful and only create
unnecessary clutter in the discussion.

When we do address your issue, we might need further information from you. GitHub has a notification system, so once we
respond, you will be notified there. Note that, by default, these notifications might not be forwarded to your email or
elsewhere, so please check GitHub periodically for updates.

Finally, when we address your issue, we will mark the issue as closed (GitHub will notify you of this too). Once that
happens, your bug should be fixed / feature implemented, but we appreciate it if you take the time to verify that
everything is working correctly. If something is still wrong, you can reopen the issue and let us know.

!!! warning "Issues are fixed on the main branch"

      Do note that when we close an issue, it means that we have fixed your bug in the `main` branch of the repository.
      That doesn't necessarily mean the fix has been released on PyPI yet, so you might still need to wait for the next
      release. Alternatively, you can also try the [git installation] to get the project right from that latest `main`
      branch.

### Attempt to solve it yourself

!!! quote

      The fastest way to get something done is to avoid waiting on others.

If you wish to try and tackle the bug yourself, let us know by commenting on the issue with something like "I'd like to
work on this". This helps us avoid duplicate efforts and ensures that we don't work on something you're already
addressing.

Once a maintainer sees your comment, they will assign the issue to you. Being assigned is a soft approval from us,
giving you the green light to start working.

Of course, you are welcome to start working on the issue even before being officially assigned. However, please be
aware that sometimes we choose not to fix certain bugs for specific reasons. In such cases, your work might not end up
being used.

Before starting your work though, make sure to also read our [pull request guide].

[changelog]: ../meta/changelog.md
[versioning]: ../meta/versioning.md
[issue tracker]: https://github.com/py-mine/mcproto/issues
[open bug issue]: https://github.com/py-mine/mcproto/issues/new?labels=type%3A+bug&template=bug_report.yml
[open feature issue]: https://github.com/py-mine/mcproto/issues/new?labels
[open blank issue]: https://github.com/py-mine/mcproto/issues/new?template=Blank+issue
[git installation]: ../installation.md#latest-git-version
[pull request guide]: ./making-a-pr.md
