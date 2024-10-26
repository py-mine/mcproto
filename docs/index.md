---
hide:
  - navigation
---

# Home

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

    *For more information on versioning and update practices, see our [Versioning Practices](./installation/versioning-model.md).*

!!! warning

    This library is still heavily Work-In-Progress, which means a lot of things can still change and some features may
    be missing or incomplete. Using the library for production applications at it's current state isn't recommended.
