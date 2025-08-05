---
hide:
    - navigation
---

# Frequently Asked Questions

!!! bug "Work In Progress"

    This page is still being worked on, if you have any suggestions for a question, feel free to create an issue on
    GitHub, or let us know on the development discord server.

## Missing synchronous alternatives for some functions

While mcproto does provide synchronous functionalities for the general protocol interactions (reading/writing packets
and lower level structures), any unrelated functionalities (such as HTTP interactions with the Minecraft API) will only
provide asynchronous versions.

This was done to reduce the burden of maintaining 2 versions of the same code. The only reason protocol interaction
even have synchronous support is because it's needed for the [`Buffer`][mcproto.buffer.Buffer]
class. (See [Issue \#128](https://github.com/py-mine/mcproto/issues/128) for more details on this decision.)

Generally, we recommend that you just stick to using the asynchronous alternatives though, both since some functions
only support async, and because async will generally provide you with a more scalable codebase, making it much easier
to handle multiple things concurrently.
