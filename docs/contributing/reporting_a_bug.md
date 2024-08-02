# Bug reports

Mcproto is an actively maintained project that we constantly strive to improve. With a project of this siez and
complexity, bugs may occur. If you think you have discovered a bug, you can help us by submitting an issue to our
public [issue tracker](https://github.com/py-mine/mcproto/issues), following this guide.

## Before creating an issue

Before opening a new issue with your bug report, please do the following things:

### Upgrade to latest version

Chances are that the bug you discovered was already fixed in a subsequent version. Thus, before reporting an issue,
ensure that you're running the [latest version](../changelog.md) of mcproto.

!!! warning "Bug fixes are not backported"

    Please understand that only bugs that occur in the latest version of mcproto will be addressed. Also, to reduce
    duplicate efforts, fixes cannot be backported to earlier versions.

### Search for existing issues

It's possible that the issue you're having was already reported. Please take some time and search the existing issues
in the GitHub repository for your problem. If you do find an existing issue that matches the problem you're having,
simply leave a :thumbsup: reaction instead (avoid commenting "I have this issue too" or similar, as that ultimately
just clutters the discussion in that issue, but if you do think that you have something meaningful to add, please do).

!!! note

    Make sure to also check the closed issues. By default, github issue search will start with: `is:issue is:open`,
    remove the `is:open` part to search all issues, not just the opened ones. It's possible that we seen this issue
    before, but closed the issue as something that we're unable to fix.

## Creating a new issue

At this point, when you still haven't found a solution to your problem, we encourage you to create an issue.
To do so, you can click [here][open-bug-issue].

[open-bug-issue]: https://github.com/py-mine/mcproto/issues/new?labels=type%3A+bug&template=bug_report.yml

## Writing good bug reports

We have a GitHub issue template set up, which will guide you towards telling us everything that we need to know.
However, for the best results, keep reading through this section. In here, we'll explain how a well formatted issue
should look like in general and what it should contain.

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
explains some of your claims, include it. Usually, this will be a <https://wiki.vg> link leading to the Minecraft
protocol documentation for something.

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

Sometimes, the bug can't be described in terms of code snippets, such as when reporting a mistake in the documentation,
in that case, provide a link to the documentation or whatever other relevant that will allows us to see the bug with
minimal effort.
