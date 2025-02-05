# Writing documentation

???+ abstract

    This guide describes how to write the documentation for this project (like the docs for the page you're reading
    right now). It contains several useful links for `mkdocs` documentation and for the various extensions that we use.

Our documentation page is generated from markdown files in the `docs/` directory, using
[`mkdocs`](https://www.mkdocs.org/) with [`mkdocs-material`](https://squidfunk.github.io/mkdocs-material/).

This gives us an amazing framework for building great-looking, modern docs. For the most part, the documentation is
written in classical markdown syntax, just with some additions. If you're familiar with markdown, you should be able to
make a simple change easily, without having to look at any docs.

That said, for more complex changes, you will want to familiarize yourself with [mkdocs-material
documentation](https://squidfunk.github.io/mkdocs-material/getting-started/). Don't worry, these docs are fairly easy
to read and while they do cover a lot, they're nicely segmented, so you should be able to find what you're looking for
quickly. On top of just that, you may want to simply look through the existing pages, as a lot of what you'd probably
want to do was already done on one of our pages, so you can just copy that.

Other than just mkdocs-material, we also use
[pymdown-extensions](https://facelessuser.github.io/pymdown-extensions/extensions/arithmatex/), which add various neat
extensions that are often useful when writing the docs. These are mostly small quality-of-life extensions that bring
some more life to the docs, but aren't something that you'd need to work with all the time. We do suggest that you check
it out though, so that you know what's available.

Finally, for generating our API reference page, we're using [mkdocstrings](https://mkdocstrings.github.io/). More on
that in the [docstrings and reference](./docstrings-and-reference.md) guide though.
