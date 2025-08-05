# Pull Requests

Welcome! If you're interested in contributing to mcproto, you've come to the right place. Mcproto is an open-source
project, and we welcome contributions from anyone eager to help out.

To contribute, you can create a [pull request] on our GitHub repository. Your pull request will then be reviewed by our
maintainers, and once approved, it will be merged into the main repository. Contributions can include bug fixes,
documentation updates, or new features.

!!! important "Code quality requirements"

    While we encourage and appreciate contributions, maintaining high code quality is crucial to us. That means you
    will need to adhere to our code quality standards. Contributions may be rejected if they do not meet these
    guidelines.

## Get assigned to the issue

The very first thing you will need to do is decide what you actually want to work on. In all likelihood, you already
have something in mind if you're reading this, however, if you don't, you're always free to check the opened GitHub
issues, that don't yet have anyone assigned. If you find anything interesting there that you'd wish to work on, leave a
comment on that issue with something like: "I'd like to work on this".

Even if you do have an idea already, we heavily recommend (though not require) that you first make an issue, this can be
a [bug report], but also a feature request, or something else. Once you made the issue, leave a: "I'd like to work on
this" comment on it.

Eventually, a maintainer will get back to you and you will be assigned to the issue. Being assigned is a soft approval
from us, giving you the green light to start coding. By getting assigned, you also reserve the right to work on that
given issue, hence preventing us (or someone else) from potentially working on the same thing, wasting ours or your
time. This prevention of duplicate efforts is also the primary reason why we recommend creating an issue first.

Of course, you are welcome to start working on the issue even before being officially assigned. However, please be
aware that sometimes, we may choose not to pursue a certain feature / bugfix. In such cases, your work might not end up
being used, which would be a shame.

!!! note "Minor tasks don't need an issue"

    While we generally do encourage contributors to first create an issue and get assigned to it first. If you're
    just fixing a typo, improving the wording, or making some minor optimizations to the code, you can safely skip
    this step.

    The point of encouraging issues is to prevent needlessly wasting people's time. However, with these minor tasks,
    it might actually take you longer to create a full issue about the problem than it would to just submit a fix.

    There's therefore no point in cluttering the issue tracker with a bunch of small issues that can often be
    changed in just a few minutes.

## Pull Request Body

A well-written PR description is one of the most helpful things you can provide as a contributor. It gives reviewers the
context they need to understand what you're doing and why. It also serves as a long-form explanation for future readers,
including users checking the changelog and digging deeper into a change.

We don’t require any strict format here. You’re free to write your PR description however you like, but good
descriptions usually do the following:

- **Link to related issues.** Use GitHub's [closing keywords][gh pr issue linking] if your PR addresses a specific
  issue, or if it just touches it, mention it (e.g. `See also: #29, #65`).
- **Describe the change in a self-contained way.** Your PR body should explain the change well enough that someone
  doesn’t need to read the diff to understand the big picture.
- **Don't repeat what's in the issue.** If you're implementing something that was already well discussed within an
  issue, you don't need to write much, just refer the reader to the issue.
- **Note anything that affects usage, behavior, or compatibility.** This includes breaking changes, deprecations, or
  changes that might not be obvious to downstream users. These should be well described within the PR body to make it
  clear exactly what changes were made when it comes to these areas. (Even if you'll repeat yourself a little in the PR
  body and the changelog fragment, this should be noted down.)
- **Be concise but complete.** You don’t need to write paragraphs and paragraphs. Just aim for enough clarity that a
  reasonably informed reader understands what this PR is about and what it changes just from the PR body.
- **Explain _why_ the change was made**, not just what changed. This helps the reviewer and future readers understand
  the motivation.
- **Mention non-obvious implementation choices.** Sometimes, we end up implementing a feature in a slightly odd way, to
  address a specific problem. This problem might be obvious when trying to implement it in the more obvious way, but it
  might not be so obvious to a reviewer. Mention these choices and your reasoning when this happens.
- **Include a summary if your body is long.** Sometimes, you will end up needing more space to explain your thought
  process and various nuances of the implementation you went with, that's okay, but in these cases, it's helpful to add
  a TL;DR / summary section.

Some helpful tips:

- It's usually better to write a few short paragraphs than a giant bullet list.
- Use markdown formatting if it helps readability (e.g., block quotes for warnings or compatibility notes, headings for
  splitting things up, bullet points, etc.).
- If relevant, add links to documentation or specs.
- Try to avoid using code blocks unless really needed.
- If your PR is exploratory, experimental, or needs discussion before merge, say so.

??? example "Example PR bodies"

    === "PR 1"

        **Title:** Fix moving desync when crossing chunk boundary

        **Body:**

        ```markdown
        Fixes: #123

        Corrects a critical desync issue occurring when players move across chunk boundaries.

        This adjusts the `ClientboundPlayerPosition` packet encoding and adding a velocity compensation threshold. It
        also includes new tests to cover edge cases at various movement speeds.
        ```

    === "PR 2"

        **Title:** Introduce support for encryption handling.

        **Body:**

        ```markdown
        Resolves #456
        See: <https://minecraft.wiki/w/Java_Edition_protocol/Encryption>

        This adds `enable_encryption` method to our connection classes, which once called, will automatically
        encrypt/decrypt any incoming/outgoing data.

        **Breaking change:** `LoginEncryptionRequest` public key attribute is now an instance of an RSA public key (from
        the `cryptography` library), instead of just holding the received bytes.

        ## Reasoning

        Most servers (even offline ones) usually send an `EncryptionRequest` packet during the LOGIN state, with a
        public (RSA) key that the client is expected to use to encrypt a randomly generated shared secret, to send back
        to the server in `EncryptionResponse` packet. After that, all further communication is encrypted with this
        shared secret.

        The encryption used is a `AES/CFB8` stream cipher. That means the encrypted ciphertext will have the same amount
        of bytes as the original plaintext, allowing us to still trust our reader/writer methods that rely on reading
        specific amounts of bytes, even if their content don't make sense.
        ```

    === "PR 3"

        **Title:** Restructure the project for new versioning approach

        **Body:**

        ```markdown
        This PR resolves #45, and restructures the entire project to no longer support multiple minecraft protocol
        versions, moving to a single (latest) version model.

        Note that **this is a completely breaking change, and there will NOT be a deprecation period**. This is because
        of how this change impacts the rest of the project development. As this project is still in pre-release stage,
        deprecation here would greatly slow down any further development here, forcing contributors to maintain both the
        temporary deprecation layer, and the new single-version one.

        For more details on how this change will affect the project going forward, and why it is necessary, I'd suggest
        checking out #45, containing a detailed explanation.

        I have updated the README examples which now use this new version, so I'd suggest checking that out before
        moving forward with trying out this version, or reviewing the code, as it demonstrates how this new approach
        will work. Note that when testing this version out, it will almost certainly break any existing code-bases using
        mcproto, checking the README changes and looking at the changelog fragment message should make it clear on how
        to update.

        ---

        Some decisions I made here, which I find potentially worth considering during a review. I'm open to doing these
        differently:

        - The `generate_packet_map` function is dynamic - imports the appropriate libraries on function run, depending
          on the requested packets. The alternative here would be to simply hard-code packet maps dictionaries as
          constants. This could be done either in the new `packet_map.py` file, but also in the individual game state
          folders for the packets, such as `mcproto.packets.login import CLIENTBOUND_MAP`.
        - The `generate_packet_map` uses caching, to avoid needlessly re-importing the modules and walking over all of
          the packets again. The clear downside of this is the fact that it uses more memory, though that's almost
          irrelevant as packet maps are relatively small.
        - Because of how caching works, since we're returning a mutable dictionary from `generate_packet_map`, the cache
          would hold the same reference as the returned dict, potentially causing issues if the user modifies that
          returned dict. ~~For this reason, I decided to also add another decorator, responsible for copying the result
          afterwards, making sure that the cache holds a different instance of the dictionary, and what users see is
          simply a copy of this instance, which they can modify or do whatever they wish with, without risking breaking
          future calls to this function.~~ For this reason, the function will now only return a mapping proxy, which is
          immutable, and holds a strong reference to the dict internally (as suggested by @Martysh12).
        ```

## Work in Progress PRs

Whenever you open a pull request that isn't yet ready to be reviewed and merged, you can mark it as a **draft**. This
provides both visual and functional indicator that the PR isn't yet ready to be merged.

Methods of marking PR as a draft:

| **When creating it**                      | **After creation**                          |
| ----------------------------------------- | ------------------------------------------- |
| ![image](../assets/draft-pr-creation.png) | ![image](../assets/draft-pr-conversion.png) |

Once your work is done and you think the PR is ready to be merged, mark it as **Ready for review**

![image](../assets/draft-pr-unmark.png){ width="600" }

## Contributing guidelines

In order to make a successful contribution, it is **required** that you get familiar with our [contributing guidelines].

## Automated checks

The project includes various CI workflows that will run automatically for your pull request after every push and check
your changes with various tools. These tools are here to ensure that our contributing guidelines are met and ensure
good code quality of your PR.

That said, you shouldn't rely on these CI workflows to let you know if you made a mistake, instead, you should run
these tools on your own machine during the development. Many of these tools can fix the violations for you
automatically and it will generally be a better experience for you. Running these tools locally will also prevent a
bunch of "Fix the CI" commits, which just clutter the git history.

Make sure to read our [contributing guidelines] thoroughly, as they describe how to use these tools and even how to have
them run automatically before each commit, so you won't forget.

Passing the CI workflows is a requirement in order to get your pull request merged. If a maintainer sees a PR that's
marked as ready for review, but isn't passing the CI, we'll often refrain from even reviewing it, as we consider it
incomplete. If you have a technical reason why your PR can't pass the CI, let us know in the PR description or a
comment.

## Code Review

All pull requests will need to be reviewed by at least one team member before merging. The reviewer will provide
feedback and suggestions for improvement.

Once a reviewer approves your pull request, it can be merged into the `main` branch.

??? question "How do I request a review?"

    Request a review from a team member by [assigning them as a reviewer][assigning pr reviewer] to your pull request.

    However, you can also just wait until we get to your PR, you don't need to assign a reviewer unless you want
    someone specific to review. Just make sure that your PR is marked as ready for review and not draft.

### Giving Feedback

If you wish, you can also provide some feedback on other PRs. Doing so is a great way to fill the time while you're
waiting for your PR to be reviewed by us and you're also speeding up the process, as it reduces the amount of time
we'd have to spend reviewing those other PRs before getting to yours.

When reviewing a pull request, aim to be constructive and specific. Highlight areas that need improvement and suggest
potential solutions. If you have any questions or concerns about something in the code, don't hesitate to ask the author
for clarification.

Focus on the following aspects during a code review:

- Correctness and functionality
- Code quality and readability
- Adherence to the project guidelines

??? example "Good Code Review Feedback"

    Here are some examples of a good code review feedback:

    ```
    - Great work on the new function! The implementation looks good overall.
    - The tests cover most of the functionality, but it's are missing a test case for edge case X. Could you add a test for that?
    - The logic in the new function is somewhat complex. Consider breaking it into smaller functions for better clarity.
    - The new feature is well-implemented, but it would be great to add more inline comments to explain the logic, as
      it isn't trivial to understand.
    - There's a small typo in the docstring. Could you correct it?
    - The configuration settings are hard-coded. Can you move them to a configuration file to make it easier to manage?
    ```

Always be respectful and considerate when giving feedback. Remember that the goal is to improve the code and help the
author grow as a developer.

!!! success "Be Positive"

    Don't forget to acknowledge the positive aspects of the contribution as well!

[pull request]: https://docs.github.com/en/pull-requests
[bug report]: ./issue-guide.md
[contributing guidelines]: ./guides/index.md
[assigning pr reviewer]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/requesting-a-pull-request-review
[gh pr issue linking]: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword
