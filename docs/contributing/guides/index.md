# Contributing guides & guidelines

Welcome to the contributing guides & guidelines for mcproto. This documentation is intended for our contributors,
interested in writing or modifying mcproto itself. If you just wish to use mcproto in your project, you can safely skip
this section.

Mcproto is a relatively large project and maintaining it is no easy task. With a project like that, consistency and
good code quality becomes very important to keep the code-base readable and bug-free. To achieve this, we have put
together these guidelines that will explain the code style and coding practices that we expect our contributors to
follow.

This documentation will also include various guides that tell you how to set up our project for development and explain
the automated tools that we use to improve our coding experience and enforce a bunch of the code style rules quickly
and without the need for human review.

## The Golden Rules of Contributing

These are the general rules which you should follow when contributing. You can glance over these and then go over the
individual guides one by one, or use the references in these rules to get to the specific guide page explaining the
rule.

!!! note

    This list serves as a quick-reference rather than a full guide. Some of our guidelines aren't directly linked in
    these references at all and we heavily encourage you to go over each of the guide pages in the order they're listed
    in the docs.

1. **Lint before you push.** We have multiple code linting rules, which define our general style of the code-base.
   These are often enforced through certain tools, which you are expected to run before every push and ideally even
   before every commit. The specifics of our linting rules are mentioned in our [style guide](./style-guide.md).
   Running all of these tools manually before every commit would however be quite annoying, so we use
   [pre-commit](./precommit.md).
2. **Make great commits.** Great commits should be atomic (do one thing only and do it well), with a commit message
   that explaining what was done, and why. More on this [here](./great-commits.md).
3. **Make an issue before the PR.** Before you start working on your PR, open an issue and let us know what you're
   planning. We described this further in our [making a PR guide](../making-a-pr.md#get-assigned-to-the-issue).
4. **Use assets licensed for public use.** Whenever you're adding a static asset (e.g. images/video files/audio or
   even code) that isn't owned/written by you, make sure it has a compatible license with our projects.
5. **Follow our [Code of Conduct](../../community/code-of-conduct.md)**

## Changes to these guidelines

While we're confident and happy with the current code style and tooling, we acknowledge that change is inevitable. New
tools are constantly being developed, and we have already made significant updates to our code style in the past.

Every project evolves over time, and these guidelines are no exception. This documentation is open to pull requests and
changes from contributors. Just ensure that any updates to this document are in sync with the codebase. If you propose
a code style change, you must apply that change throughout the codebase to maintain internal consistency.

If you believe you have something valuable to add or change, please submit a pull request. For major style changes, we
strongly encourage you to open an issue first, as we may not always agree with significant alterations. For minor
clarity improvements or typo fixes, opening an issue isn't necessary.

We tried to design our specifications to be straightforward and comprehensive, but we might not always succeed, as
we're doing so from our perspective of already having extensive background knowledge. Therefore, we welcome any clarity
improvements to the documentation. If you think you can explain something better, please contribute.

## Footnotes

We understand that going through all of these guidelines can be time-consuming and a lot to remember. However, we
strongly encourage you to review them, especially if you haven't worked with these tools or followed such best
practices before.

Every page in this contributing guides category has an abstract at the top, summarizing its content. This allows you to
quickly determine if you are already familiar with the topic or, if you're re-reading, to quickly recall what the page
covers. Feel free to skip any guide pages if you're already familiar with what they cover.

We believe these guides will be beneficial to you beyond our codebase, as they promote good coding practices and help
make your code cleaner. You will likely be able to apply much of the knowledge you gain here to your own projects.

## Disclaimer

These documents were inspired by [Python Discord's CONTRIBUTING agreement.][pydis-contributing]

[pydis-contributing]: https://github.com/python-discord/bot/blob/master/CONTRIBUTING.md
