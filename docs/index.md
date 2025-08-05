---
hide:
    - navigation
    - toc
---

# Home

<style>
    /*
     * Use a smaller max-width (since we don't have toc nor navigation sidebars, the content expands a lot, beyond
     * certain point, this starts to look kinda bad, set a smaller max width to handle this)
     */
    .md-grid {
        max-width: 1300px;
    }

    /* Hide the h1 title */
    .md-content .md-typeset h1 { display: none; }

    /*
     * By hiding the h1 title, mkdocs will see it as active (scrolled at it)
     * which affects the header. This isn't what we want, as it makes the mike
     * version selector disappear, and it also just isn't what we'd want anyways.
     * Force the main header to be visible and hide the active one.
     *
     * See: https://github.com/squidfunk/mkdocs-material/issues/2163#issuecomment-3156700587
     */
    .md-header__title--active .md-header__topic {
        opacity: unset;
        pointer-events: unset;
        transform: unset;
        z-index: unset;
    }
    .md-header__title--active .md-header__topic + .md-header__topic {
        opacity: 0;
        pointer-events: unset;
        transform: unset;
        z-index: unset;
    }
</style>

<div style="display: flex; align-items: center; font-size: 75px; font-weight: bold; color: lightgray;">
    <img src="./assets/py-mine_logo.png" width=100 alt="Logo">
    MCPROTO
</div>

## What is Mcproto

Mcproto is a python library that provides various low level interactions with the Minecraft protocol. It attempts to be
a full wrapper around the Minecraft protocol, which means it could be used as a basis for Minecraft bots written in
python, or even full python server implementations.

!!! important

    Mcproto only covers the **latest minecraft protocol implementation**, updating with each full minecraft release
    (not including snapshots!). Using mcproto for older versions of minecraft is not officially supported, if you need
    to do so, you will want to use an older version of mcproto, but note that **no bug fixes or features will be
    backported** to these older versions.

    *For more information on versioning and update practices, see our [Versioning Practices][versioning].*

!!! warning

    This library is still heavily Work-In-Progress, which means a lot of things can still change and some features may
    be missing or incomplete. Using the library for production applications at it's current state isn't recommended.

[versioning]: meta/versioning.md
