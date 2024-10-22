# Minecraft account authentication

Mcproto has first party support to handle authentication, allowing you to use your own minecraft account. This is
needed if you wish to login to "online mode" (non-warez) servers as a client (player).

## Microsoft (migrated) accounts

This is how authentication works for already migrated minecraft accounts, using Microsoft accounts for authentication.
(This will be most accounts. Any newly created minecraft accounts - after 2021 will always be Microsoft linked
accounts.)

### Creating Azure application

To authenticate with a microsoft account, you will need to go through the entire OAuth2 flow. Mcproto has functions to
hide pretty much all of this away, however you will need to create a new Microsoft Azure application, that mcproto
will use to obtain an access token.

We know this is annoying, but it's a necessary step, as Microsoft only allows these applications to request OAuth2
authentication, and to avoid potential abuse, we can't really just use our registered application (like with say
[MultiMC](https://github.com/MultiMC/Launcher)), as this token would have to be embedded into our source-code, and
since this is python, that would mean just including it here in plain text, and because mcproto is a low level library
that can be used for any kind of interactions, we can't trust that you won't abuse this token.

Instead, everyone using mcproto should register a new application, and get their own MSA token for your application
that uses mcproto in the back.

To create a new application, follow these steps (this is a simplified guide, for a full guide, feel free to check the
[Microsoft documentation](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)):

1. Go to the [Azure portal](https://portal.azure.com/#home) and log in (create an account if you need to).
2. Search for and select **Azure Active Directory**.
3. On the left navbar, under **Manage** section, click on **App registrations**.
4. Click on **New registration** on top navbar.
5. Pick a name for the application. Anyone using your app to authenticate will see this name.
6. Choose **Personal Microsoft accounts only** from the Supported account types.
7. Leave the **Redirect URI (optional)** empty.
8. Click on **Register**.

From there, you will need to enable this application to be used for OAuth2 flows. To do that, follow these steps:

1. On the left navbar, under **Manage** section, click on **Authentication**.
2. Set **Allow public content flows** to **Yes**.
3. Click **Save**.

After that, you can go back to the app (click **Overview** from the left navbar), and you'll want to copy the
**Application (client) ID**. This is the ID you will need to pass to mcproto. (You will also need the **Display name**,
and the **Directory (Tenant) ID** for [Registering the application with Minecraft] - first time only)

If you ever need to access this application again, follow these steps (as Microsoft Azure is pretty unintuitive, we
document this too):

1. Go to the [Azure portal](https://portal.azure.com/#home) and log in.
2. Click on **Azure Active Directory** (if you can't find it on the main page, you can use the search).
3. On the left navbar, under **Manage** section, click on **App registrations**.
4. Click on **View all applications from personal account** (assuming you registered the app from a personal account).
5. Click on your app.

### Registering the application with Minecraft

Previously, this step wasn't required, however due to people maliciously creating these applications to steal
accounts, Mojang have recently started to limit access to the <https://api.minecraftservices.com>, and only allow
explicitly white listed Client IDs to use this API.

This API is absolutely crucial step in getting the final minecraft token, and so you will need to register your Client
ID to be white listed by Mojang. Thankfully, it looks like Mojang is generally pretty lenient and at least for me,
they didn't cause any unnecessary hassles when I asked for my application to be registered, for development purposes
and work on mcproto.

That said, you will need to wait a while (about a week, though it could be more), until Mojang reviews your
application and approves it. There isn't much we can do about this.

To get your Azure application registered, you will need to fill out a simple form, where you accept the EULA, provide
your E-Mail, Application name, Application Client ID and Tennant ID.

More annoyingly you will additionally also need to provide an **associated website or domain** for your project/brand.
(This application is generally designed for more user-facing programs, such as full launchers. When registering
mcproto, I just used the GitHub URL). Lastly, you'll want to describe why you need access to this API in the
**Justification** section.

Visit the [Mojang article](https://help.minecraft.net/hc/en-us/articles/16254801392141) describing this process. There
is also a link to the form to fill out.

### The code

Finally, after you've managed to register your application and get it approved by Mojang, you can use it with mcproto,
go through the Microsoft OAuth2 flow and authorize this application to access your Microsoft account, which mcproto
will then use to get the minecraft token you'll then need to login to online servers.

```python
import httpx
from mcproto.auth.microsoft.oauth import full_microsoft_oauth
from mcproto.auth.microsoft.xbox import xbox_auth
from mcproto.auth.msa import MSAAccount

MY_MSA_CLIENT_ID = "[REDACTED]"  # Paste your own Client ID here

async def authenticate() -> MSAAccount:
    async with httpx.AsyncClient() as client:
        microsoft_token = await full_microsoft_oauth(client, MY_MSA_CLIENT_ID)
        user_hash, xsts_token = xbox_auth(client, microsoft_token)
        return MSAAccount.xbox_auth(cilent, user_hash, xsts_token)
```

Note that the `full_microsoft_oauth` function will print a message containing the URL you should visit in your
browser, and a one time code to type in once you reach this URL. That will then prompt you to log in to your Microsoft
account, and then allow you to authorize the application to use your account.

### Caching

You will very likely want to set up caching here, and store at least the `microsoft_token` somewhere, so you don't have
to log in each time your code will run. Here's some example code that caches every step of the way, always resorting to
the "closest" functional token. Note that this is using `pickle` to store the tokens, you may want to use JSON or other
format instead, as it would be safer. Also, be aware that these are sensitive and if compromised, someone could gain
access to your minecraft account (though only for playing, they shouldn't be able to change your password or anything
like that), so you might want to consider encrypting these cache files before storing:

```python
from __future__ import annotations

import logging
import pickle
from pathlib import Path

import httpx

from mcproto.auth.microsoft.oauth import full_microsoft_oauth
from mcproto.auth.microsoft.xbox import XSTSRequestError, xbox_auth
from mcproto.auth.msa import MSAAccount, ServicesAPIError

log = logging.getLogger(__name__)

MY_MSA_CLIENT_ID = "[REDACTED]"  # Paste your own Client ID here
CACHE_DIR = Path(".cache/")


async def microsoft_login(client: httpx.AsyncClient) -> MSAAccount:  # noqa: PLR0912,PLR0915
    """Obtain minecraft account using Microsoft authentication.

    This function performs full caching of every step along the way, allowing for recovery
    without manual intervention for as long as at least the root token (from Microsoft OAuth2)
    is valid. Any later tokens will be refreshed and re-cached once invalid.

    If all tokens are invalid, or this function was ran for the first time (without any cached
    data), you will be shown a URL and a code. You have to go to this URL with your browser and
    enter the code, completing the OAuth2 flow, obtaining the root token.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    access_token_cache = CACHE_DIR.joinpath("xbox_access_token.pickle")
    if access_token_cache.exists():
        with access_token_cache.open("rb") as f:
            access_token: str = pickle.load(f)  # noqa: S301

        try:
            account = await MSAAccount.from_xbox_access_token(client, access_token)
            log.info("Logged in with cached xbox minecraft access token")
            return account
        except httpx.HTTPStatusError as exc:
            log.warning(f"Cached xbox minecraft access token is invalid: {exc!r}")
    else:
        log.warning("No cached access token available, trying Xbox Secure Token Service (XSTS) token")

    # Access token either doesn't exist, or isn't valid, try XSTS (Xbox) token
    xbox_token_cache = CACHE_DIR.joinpath("xbox_xsts_token.pickle")
    if xbox_token_cache.exists():
        with xbox_token_cache.open("rb") as f:
            user_hash, xsts_token = pickle.load(f)  # noqa: S301

        try:
            access_token = await MSAAccount._get_access_token_from_xbox(client, user_hash, xsts_token)
        except ServicesAPIError as exc:
            log.warning(f"Invalid cached Xbox Secure Token Service (XSTS) token: {exc!r}")
        else:
            log.info("Obtained xbox access token from cached Xbox Secure Token Service (XSTS) token")
            log.info("Storing xbox minecraft access token to cache and restarting auth")
            with access_token_cache.open("wb") as f:
                pickle.dump(access_token, f)
            return await microsoft_login(client)
    else:
        log.warning("No cached Xbox Secure Token Service (XSTS) token available, trying Microsoft OAuth2 token")

    # XSTS token either doesn't exist, or isn't valid, try Microsoft OAuth2 token
    microsoft_token_cache = CACHE_DIR.joinpath("microsoft_token.pickle")
    if microsoft_token_cache.exists():
        with microsoft_token_cache.open("rb") as f:
            microsoft_token = pickle.load(f)  # noqa: S301

        try:
            user_hash, xsts_token = await xbox_auth(client, microsoft_token)
        except (httpx.HTTPStatusError, XSTSRequestError) as exc:
            log.warning(f"Invalid cached Microsoft OAuth2 token {exc!r}")
        else:
            log.info("Obtained Xbox Secure Token Service (XSTS) token from cached Microsoft OAuth2 token")
            log.info("Storing Xbox Secure Token Service (XSTS) token to cache and restarting auth")
            with xbox_token_cache.open("wb") as f:
                pickle.dump((user_hash, xsts_token), f)
            return await microsoft_login(client)
    else:
        log.warning("No cached microsoft token")

    # Microsoft OAuth2 token either doesn't exist, or isn't valid, request user auth
    log.info("Running Microsoft OAuth2 flow, requesting user authentication")
    microsoft_token = await full_microsoft_oauth(client, MY_MSA_CLIENT_ID)
    log.info("Obtained Microsoft OAuth2 token from user authentication")
    log.info("Storing Microsoft OAuth2 token and restarting auth")
    with microsoft_token_cache.open("wb") as f:
        pickle.dump(microsoft_token["access_token"], f)
    return await microsoft_login(client)
```

## Minecraft (non-migrated) accounts

If you haven't migrated your account into a Microsoft account, follow this guide for authentication. (Any newly created
Minecraft accounts will be using Microsoft accounts already.) This method of authentication is called "yggdrasil".

!!! warning

    The account migration process has been concluded in  **September 19, 2023**. See:
    <https://www.minecraft.net/en-us/article/account-migration-last-call>

    That means that it's no longer possible to migrate this old account into a microsoft account and it's only a matter
    of time until the authentication servers handling these accounts are turned off entirely.

    Mcproto will remove support for this old authentication methods once this happens.

This method of authentication doesn't require any special app registrations, however it is significantly less secure,
as you need to enter your login and password directly.

```python
import httpx
from mcproto.auth.yggdrasil import YggdrasilAccount

LOGIN = "mail@example.com"
PASSWORD = "my_password"

async def authenticate() -> YggdrasilAccount:
    async with httpx.AsyncClient() as client:
        return YggdrasilAccount.authenticate(client, login=LOGIN, password=PASSWORD)
```

The Account instance you will obtain here will contain a refresh token, and a shorter lived access token, received from
Mojang APIs from the credentials you entered. Just like with Microsoft accounts, you may want to cache these tokens to
avoid needless calls to request new ones and go through authentication again. That said, since doing so doesn't
necessarily require user interaction, if you make the credentials accessible from your code directly, this is a lot
less annoying.

If you will decide to use caching, or if you plan on using these credentials in a long running program, you may see the
access token expire. You can check whether the token is expired with the `YggdrasilAccount.validate` method, and if it
is (call returned `False`), you can call `YggdrasilAccount.refresh` to use the refresh token to obtain a new access
token. The refresh token is much more long lived than the access token, so this should generally be enough for you,
although if you login from elsewhere, or after a really long time, the refresh token might be invalidated, in that
case, you'll need to go through the full login again.

## Legacy Mojang accounts

If your minecraft account is still using the (really old) Mojang authentication, you can simply follow the non-migrated
guide, as it will work with these legacy accounts too, the only change you will need to make is to use your username,
instead of an email.
