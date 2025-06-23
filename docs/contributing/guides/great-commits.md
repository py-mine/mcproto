# Great Commits

???+ abstract

    This guide describes how to make good commits that are helpful to maintainers, debuggable and readable when going
    over the `git log`, or `git blame`.

    It explains the purpose of a commit message and it's structure, goes over the importance of making commits
    "atomic" and the practice of partial staging. Additionally, it also mentions why and how to avoid making a lot of
    fixing commits, describes the practice of force pushing, alongside it's downsides and finally, it explains why
    these practices are worth following and how they make the developer's life easier.

A well-structured git log is crucial for a project's maintainability, providing insight into changes as a reference for
future maintainers (or old forgetful ones, _like me_). Here, we outline the best practices for making good commits in
our project.

## Commit Message Guidelines

### Purpose

Every commit should represent a change in the source code. The commit message should not only describe **what** was
changed but also **why** it was necessary and what it achieves.

### More than just the first line

Many developers are uesd to commiting changes with a simple `git commit -m "My message"`, and while this is enough and
it's perfectly fine in many cases, sometimes you just need more space to describe what a change truly achieves.

Surprisingly, many people don't even know that they can make a commit that has more in it's message than just the
title/first line. That then leads to poorly documented changes, because single line sometimes just isn't enough.

To create a commit with a bigger commit message, you can simply run the `git commit` command without the `-m` argument.
This should open a temporary file in your text editor (`$EDITOR`), in which you can write out your commit message in
full.

??? tip "Use git commit by default"

    I’d actually recommend making the simple `git commit` the default way you make new commits, since it invites you to
    write more about it, by just seeing that you have that space available. We usually don’t even know what exactly
    we’ll write in our new commit message before getting to typing it out, and knowing you have that extra space if you
    need it will naturally lead to using it, even if you didn’t know you needed it ahead of time.

!!! note

    That said, not every commit requires both a subject and a body. Sometimes, a change may be so simple, that no
    further context is necessary. With those changes, including a body would just be a waste of the readers time. For
    example:

    ```markdown
    Fix typo in README
    ```

    This message doesn't need anything extra. Some people like to include what the typo was, but if you want to know
    that, you can just look at the actual changes that commit made. There's a whole bunch of ways to do that with git,
    like `git show`, `git diff` or `git log --patch`. So while in some cases, having extra context can be very
    valuable, you also shouldn't overdo it.

### Structure

Git commits should be written in a very specific way. There’s a few rules to follow:

1. **Subject Line:**
    - **Limit to 50 characters** (This isn't a hard limit, but try not to go much longer. This limit ensures
      readability and forces the author to think about the most concise way to explain what's going on. Hint: If you're
      having trouble summarizing, you might be committing too much at once)
    - **A single sentence** (The summary should be a single sentence, multiple probably wouldn't fit into the character
      limit anyways)
    - **Capitalize the first letter**
    - **Don't end with a period** (A period will only waste one of your precious 50 characters for the summary and
      it's not very useful context wise)
    - **Use imperative mood** (Imperative mood means “written as if giving a command/instruction” i.e.: “Add support
      for X”, not “I added support for X” or “Support for X was added”, as a rule of thumb, a subject message should be
      able to complete the sentence: “If implemented, this commit will …”)
2. **Body:**
    - **Separate the body from the subject line with a blank line** (Not doing so would make git think your summary
      spans across multiple lines, rather than it being a body)
    - **Wrap at 72 characters** (Commits are often printed into the terminal with the `git log` command. If the output
      isn't wrapped, going over the terminals width can cause a pretty messy output. The recommended maximum width for
      terminal text output is 80 characters, but git tools can often add indents, so 72 characters is a sensible maximum)
    - **Avoid implementation details** (The diff shows the "how", focus on the "what" and "why")

Git commits can use markdown, most other programs will understand it and it's a great way to bring in some more
style, improving the readability. In fact, if you view the commit from a site like GitHub, it will automatically
render any markdown in the commit for you.

???+ example "Example commit"

    ```markdown
    Summarize changes in around 50 characters or less

    More detailed explanatory text, if necessary. Wrap it to about 72
    characters or so. In some contexts, the first line is treated as the
    subject of the commit and the rest of the text as the body. The
    blank line separating the summary from the body is critical (unless
    you omit the body entirely); various tools like `log`, `shortlog`
    and `rebase` can get confused if you run the two together.

    Explain the problem that this commit is solving. Focus on why you
    are making this change as opposed to how (the code explains that).
    Are there side effects or other unintuitive consequences of this
    change? Here's the place to explain them.

    Further paragraphs come after blank lines.

    - Bullet points are okay too
    - They're very useful for listing something
    ```

:material-run-fast: **Stretch goal** – Include relevant **keywords** to make your commits easily searchable (e.g. the
name of the class/function you modified).

:material-run-fast: **Stretch goal \#2** – Keep it **engaging**! Provide some interesting context or debug processes to
make the commit history both more informative and fun to read.

## Make "atomic" commits

!!! quote "Definition"

    *Atomic: of or forming a single irreducible unit or component in a larger system.*

The term “atomic commit” means that the commit is only representing a single change, that can’t be further reduced into
multiple commits, i.e. this commit only handles a single change. Ideally, it should be possible to sum up the changes
that a good commit makes in a single sentence.

That said, the irreducibility should only apply to the change itself, obviously, making a commit for every line of code
wouldn’t be very clean. Having a commit only change a small amount of code isn’t what makes it atomic. While the commit
certainly can be small, it can just as well be a commit that’s changing thousands of lines. (That said, you should have
some really good justification for it if you’re actually making commits that big.)

The important thing is that the commit is only responsible for addressing a single change. A counter-example would be a
commit that adds a new feature, but also fixes a bug you found while implementing this feature, and also improves the
formatting of some other function, that you encountered along the way. With atomic commits, all of these actions would
get their own standalone commits, as they’re unrelated to each other, and describe several different changes.

Note that making atomic commits isn't just about splitting thins up to only represent single changes, indeed, while
they should only represent the smallest possible change, it should also be a “complete” change. This means that a
commit responsible for changing how some function works in order to improve performance should ideally also update the
documentation, make the necessary adjustments to unit-tests so they still pass, and update all of the references to
this updated function to work properly after this change.

!!! abstract "Summary"

    So, an atomic commit is a commit representing a single (ideally an irreducible) change, that’s fully implemented
    and integrates well with the rest of the codebase.

### Partial adds

Many people tend to always simply use `git add -A` (or `git add .`), to stage all of the changes they made, and then
create a commit with it all. Sometimes, you might not even stage the changes and choose to use `git commit -a`, to
quickly commit everything.

In an ideal world, where you only made the changes you needed to make for this single atomic commit, this would work
pretty well, and while sometimes this is the case, in many cases, you might've also fixed a bug or a typo that you
noticed while working on your changes, or already implemented something else, that doesn't fit into your single atomic
commit that you now wish to make.

In this case, it can be very useful to know that you can instead make a "partial" add, only staging those changes that
belong to the commit.

In some cases, it will be sufficient to simpy stage specific files, which you can do with:

```bash
git add path/to/some/file path/to/other/file
```

That said, in most cases, you're left with a single file that contains multiple unrelated changes. When this happens,
you can use the `-p`/`--patch` flag:

```bash
git add -p path/to/file
```

Git will then let you interactively go over every "hunk" (a chunk of code, with changes close to each other) and let
you decide whether to accept it (hence staging that single hunk), split it into more chunks, skip it (avoids staging
this hunk) or even modify it in your editor, allowing you to remove the intertwined code from multiple changes, so that
your commit will really only perform a single change.

!!! tip "Use --patch more often"

    This git feature has slowly became one of my favorite tools, and I use it almost every time I need to commit
    something, even if I don't need to change or skip things, since it also allows me to quickly review the changes
    I'm making, before they make it into a commit.

## Avoid fixing commits

A very common occurrence I see in a ton of different projects is people making sequences of commits that go like:

- Fix bug X
- Actually fix bug X
- Fix typo in variable name
- Sort imports
- Follow lint rules
- Run auto-formatter

While people can obviously mess up sometimes, and just not get something right on the first try, a fixing commit is
rarely a good way to solve that.

Instead of making a new commit, you can actually just amend the original. To do this, we can use the `git commit
--amned`, which will add your staged changes into the previous commit, even allowing you to change the message of that
old commit.

Not only that, if you've already made another commit, but now found something that needs changing in the commit before
that, you can use interactive rebase with `git rebase -i HEAD~3`, allowing you to change the last 3 commits, or even
completely remove some of those commits.

For more on history rewriting, I'd recommend checking the [official git
documentation][git-history-rewriting].

### Force pushing

Changing history is a great tool to clean up after yourself, but it works best with local changes, i.e. with changes
you haven't yet pushed.

If you're changing git history after you've already pushed, you will find that pushing again will not work, giving you
a message like "updates were rejected because the remote contains work that you do not have locally".

To resolve this issue, it is possible to make a "force push" with `git push --force` command. Running this will push
your branch to the remote (to GitHub) regardless of what was in the remote already, hence overriding it.

!!! warning

    Force pushing becomes risky if others have already pulled the branch you are working on. If you overwrite the
    branch with a force push, it can lead to several issues:

    - **Lost work:** Collaborators may have pushed to your branch already, following it's existing git history.
      However, after your force-push, their changes would be ereased from the remote. **Make sure you pull / rebase
      from the remote before you make a force-push.**
    - **Complex conflicts:** If someone else has pulled your branch and did some changes that they didn't yet push
      before you force-pushed, suddenly, their git history is now no longer in sync. Resolving conflicts like that is
      possible, but it can be very annoying.
    - **Harder reviews:** When reviewing your code, we sometimes like going over the individual commits to understand
      your individual (atomic) changes better. It's often a lot easier to look at and review 10 different atomic
      changes individually, that together form a PR than it would be to look at all of them at once. By force-pushing,
      you're changing the commit history, making the changes to the code that we already reviewed. This is partially
      GitHub's fault though, for not providing an easier way of showing these changes across force-pushes.

#### Force pushing on PR feature branches

In our project, we do allow force pushing on your individual feature branches that you use for your PR. This
flexibility enables you to clean up your commit history and refine your changes before they are merged into the main
branch. However, it's important to note that many other projects may not permit force pushing due to the risks
involved. Always check the contributing guidelines of the project you are working on.

!!! tip "Best practices"

    To mitigate the risks associated with force pushing, consider following these best practices:

    - **Push less often:** Try to limit of othen you push changes to the remote repository in general. Aim to push only
      when you are satisfied with the set of changes you have. This reduces the likelihood of needing to force-push a
      lot.
    - **Force push quickly:** If you do need to force-push, try to do so as quickly as possible. The more time that has
      passed since your normal push, the more likely it is that someone have already clonned/pulled your changes. If a
      force push was made within just a few seconds of the original push (and it only overwrites the changes from that
      last push), it's not very likely that someone will have those changes pulled already, so you probably won't break
      anyone's local version.
    - **Pull before changing history:** Make absolutely certain that you don't override anyone's changes with your
      force-push. Sometimes, maintainers can create new commits in your branch, other times, that can even be you by
      modifying something from GitHub, or clicking on the apply suggestion button from a code-review. By pulling before
      you start changing history, you can make sure that you won't erease these changes and they'll remain a part of
      your modified history.

## Benefits

Now that you've seen some of the best practices to follow when making new commits, let's talk a bit about why we follow
these practices and what benefits we can gain from them.

### A generally improved development workflow

Speaking from my personal experience, I can confidently say that learning how to make good git commits, specifically
the practice of making atomic commits will make you a better programmer overall. That might sound surprising, but it's
really true.

The reason is that it forces you to only tackle one issue at a time. This naturally helps you to think about how to
split your problem into several smaller (atomic) subproblems and make commits addressing those single parts. This is
actually one of very well known approaches to problem-solving, called the "divide and conquer" method, where you split
your problem into really small, trivially simple chunks that you solve one by one.

### Easier bug hunting

Bugs in code are pretty much inevitable, even for the most experienced of developers. Sometimes, we just don't realise
how certain part of the code-base will interact with another part, or we're just careless as we try and build something
fast.

The most annoying bugs are those that aren't discovered immediately during development. These bugs can require a lot of
work to track down. With a good git log, filled with a lot of small commits, where each commit leaves the code-base in
a usable state, you can make this process a lot simpler!

Git has a command specifically for this: `git bisect`. It will first make you mark 2 commits, a good one and a bad one,
after which it will perform a binary search, checking out the commits in between these two as you try and replicate the
bug on each. This will quickly lead you to the specific commit that introduced this bug, without having to do any code
debugging at all.

The great advantage here is that users reporting bugs can often perform git bisects too, even without having to know
much about development and the structure of our code-base and if the identified commit is small enough, the issue is
often apparent just from looking at the diff. Even for bigger commits though, they can be often reverted to quickly fix
the issue and give developers time to focus on actually resolving it, while using it's diff as a reference.

### Enhanced git blame

Clear commit messages can be very useful for understanding certain parts of the code. Git provides a tool called `git
blame`, which can show you which commit is responsible for adding a specific line into the code-base. From there, you
can then take a look at that commit specifically and see it's title & description to further understand that change,
along with the rest of the diff to give you proper context for how that line worked with the rest of the code.

This can often be a great tool when refactoring, as sometimes it can be quite unclear why something is done the way it
is and commits can sometimes help explain that.

### Efficient cherry picking

In some cases, it can be useful to carry over certain change (commit) from one place to another. This process is called
cherry-picking (`git cherry-pick`), which will copy a commit and apply it's diff elsewhere. With atomic commits, this
will often work without any further adjustments, since each commit should itself leave you with a functioning project.

### Streamlined pull request reviews

Reviewers can often better understand and verify changes by examining your well-structured commits, improving the
review process.

## Footnotes

This guide took **heavy** inspiration from this article: <https://itsdrike.com/posts/great-commits/>.

!!! quote

    P.S. It's not plagiarism if the original was written by me :P

See the original article's sources for proper attributions.

[git-history-rewriting]: https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History
