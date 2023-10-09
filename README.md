# <img src="https://i.imgur.com/nPCcxts.png" style="height: 25px"> mcproto

[![discord chat](https://img.shields.io/discord/936788458939224094.svg?logo=Discord)](https://discord.gg/C2wX7zduxC)
![supported python versions](https://img.shields.io/pypi/pyversions/mcproto.svg)
[![current PyPI version](https://img.shields.io/pypi/v/mcproto.svg)](https://pypi.org/project/mcproto/)
[![Test Coverage](https://api.codeclimate.com/v1/badges/9464f1037f07a795de35/test_coverage)](https://codeclimate.com/github/py-mine/mcproto/test_coverage)
[![Validation](https://github.com/ItsDrike/mcproto/actions/workflows/validation.yml/badge.svg)](https://github.com/ItsDrike/mcproto/actions/workflows/validation.yml)
[![Unit tests](https://github.com/ItsDrike/mcproto/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/ItsDrike/mcproto/actions/workflows/unit-tests.yml)
[![Docs](https://img.shields.io/readthedocs/mcproto?label=Docs)](https://mcproto.readthedocs.io/)

This is a heavily Work-In-Progress library, which attempts to be a full wrapper around the minecraft protocol, allowing
for simple interactions with minecraft servers, and perhaps even for use as a base to a full minecraft server
implementation in python (though the speed will very likely be quite terrible, making it probably unusable as any
real-world playable server).

Currently, the library is very limited and doesn't yet have any documentation, so while contributions are welcome, fair
warning that there is a lot to comprehend in the code-base and it may be challenging to understand it all.

## Examples

Since there is no documentation, to satisfy some curious minds that really want to use this library even in this
heavily unfinished state, here's a few simple snippets of it in practice:

### Manual communication with the server

As sending entire packets is still being worked on, the best solution to communicate with a server is to send the data
manually, using our connection reader/writer, and buffers (being readers/writers, but only from bytearrays as opposed
to using an actual connection).

Fair warning: This example is pretty long, but that's because it aims to explain the minecraft protocol to people that
see it for the first time, and so a lot of explanation comments are included. But the code itself is actually quite
simple, due to a bunch of helpful read/write methods the library already provides.

```python
import json
import asyncio

from mcproto.buffer import Buffer
from mcproto.connection import TCPAsyncConnection
from mcproto.protocol.base_io import StructFormat


async def handshake(conn: TCPAsyncConnection, ip: str, port: int = 25565) -> None:
    # As a simple example, let's request status info from a server.
    # (this is what you see in the multiplayer server list, i.e. the server's motd, icon, info
    # about how many players are connected, etc.)

    # To do this, we first need to understand how are minecraft packets composed, and take a look
    # at the specific packets that we're interested in. Thankfully, there's an amazing community
    # made wiki that documents all of this! You can find it at https://wiki.vg/

    # Alright then, let's take a look at the (uncompressed) packet format specification:
    # https://wiki.vg/Protocol#Packet_format
    # From the wiki, we can see that a packet is composed of 3 fields:
    # - Packet length (in bytes), sent as a variable length integer
    #       combined length of the 2 fields below
    # - Packet ID, also sent as varint
    #       each packet has a unique number, that we use to find out which packet it is
    # - Data, specific to the individual packet
    #       every packet can hold different kind of data, this will be shown in the packet's
    #       specification (you can find these in wiki.vg)

    # Ok then, with this knowledge, let's establish a connection with our server, and request
    # status. To do this, we fist need to send a handshake packet. Let's do it:

    # Let's take a look at what data the Handshake packet should contain:
    # https://wiki.vg/Protocol#Handshake
    handshake = Buffer()
    # We use 47 for the protocol version, as it's quite old, and will work with almost any server
    handshake.write_varint(47)
    handshake.write_utf(ip)
    handshake.write_value(StructFormat.USHORT, port)
    handshake.write_varint(1)  # Intention to query status

    # Nice! Now that we have the packet data, let's follow the packet format and send it.
    # Let's prepare another buffer that will contain the last 2 fields (packet id and data)
    # combined. We do this since the first field will require us to know the size of these
    # two combined, so let's just put them into 1 buffer.
    packet = Buffer()
    packet.write_varint(0)  # Handshake packet has packet ID of 0
    packet.write(handshake)  # Full data from our handshake packet

    # And now, it's time to send it!
    await conn.write_varint(len(packet))  # First field (size of packet id + data)
    await conn.write(packet)  # Second + Third fields (packet id + data)


async def status(conn: TCPAsyncConnection, ip: str, port: int = 25565) -> dict:
    # This function will be called right after a handshake
    # Sending this packet told the server recognize our connection, and since we've specified
    # the intention to query status, it then moved us to STATUS game state.

    # Different game states have different packets that we can send out, for example there is a
    # game state for login, that we're put into while joining the server, and from it, we tell
    # the server our username player UUID, etc.

    # The packet IDs are unique to each game state, so since we're now in status state, a packet
    # with ID of 0 is no longer the handshake packet, but rather the status request packet
    # (precisely what we need).
    # https://wiki.vg/Protocol#Status_Request

    # The status request packet is empty, and doesn't contain any data, it just instructs the
    # server to send us back a status response packet. Let's send it!
    packet = Buffer()
    packet.write_varint(0)  # Status request packet ID

    await conn.write_varint(len(packet))
    await conn.write(packet)

    # Now, let's receive the response packet from the server
    # Remember, the packet format states that we first receive a length, then packet id, then data
    _response_len = await conn.read_varint()
    _response = await conn.read(_response_len)  # will give us a bytearray

    # Amazing, we've just received data from the server! But it's just bytes, let's turn it into
    # a Buffer object, which includes helpful methods that allow us to read from it
    response = Buffer(_response)
    packet_id = response.read_varint()  # Remember, 2nd field is the packet ID

    # Let's see it then, what packet did we get?
    print(packet_id)  # 0

    # Interesting, this packet has an ID of 0, but wasn't that the status request packet? We wanted
    # a response tho. Well, actually, if we take a look at the status response packet at the wiki,
    # it really has an ID of 0:
    # https://wiki.vg/Protocol#Status_Response
    # Aha, so not only are packet ids unique between game states, they're also unique between the
    # direction a server bound packet (sent by client, with server as the destination) can have an
    # id of 0, while a client bound packet (sent by server, with client as the destination) can
    # have the same id, and mean something else.

    # Alright then, so we know what we got is a status response packet, let's read the wiki a bit
    # further and see what data it actually contains, and see how we can get it out. Hmmm, it
    # contains a UTF-8 encoded string that represents JSON data, ok, so let's get that string, it's
    # still in our buffer.
    received_string = response.read_utf()

    # Now, let's just use the json module, convert the string into some json object (in this case,
    # a dict)
    data = json.loads(received_string)
    return data

async def main():
    # That's it, all that's left is actually calling our functions now

    ip = "mc.hypixel.net"
    port = 25565

    async with (await TCPAsyncConnection.make_client((ip, port), 2)) as connection:
        await handshake(connection, ip, port)
        data = await status(connection, ip, port)

    # Wohoo, we got the status data! Let's see it
    print(data["players"]["max"])  # This is the server's max player amount (slots)
    print(data["players"]["online"])  # This is how many people are currently online
    print(data["description"])  # And here's the motd

    # There's a bunch of other things in this data, try it out, see what you can find!

def start():
    # Just some boilerplate code that can run our asynchronous main function
    asyncio.run(main())
```

### Using packet classes for communication

The first thing you'll need to understand about packet classes in mcproto is that they're generally going to support
the latest minecraft version, and while any the versions are usually mostly compatible, mcproto does NOT guarantee
support for any older protocol versions.

#### Obtaining the packet map

As we've already seen in the example before, packets follow certain format, and every packet has it's associated ID
number, direction (client->server or server->client), and game state (status/handshaking/login/play). The packet IDs
are unique to given direction and game state combination.

For example in clientbound direction (packets sent from server to the client), when in the status game state, there
will always be unique ID numbers for the different packets. In this case, there would actually only be 2 packets here:
The Ping response packet, which has an ID of 1, and the Status response packet, with an ID of 0.

To receive a packet, we therefore need to know both the game state, and the direction, as only then are we able to
figure out what the type of packet it is. In mcproto, packet receiving therefore requires a "packet map", which is a
mapping (dictionary) of packet id -> packet class. Here's an example of obtaining a packet map:

```python
from mcproto.packets import generate_packet_map, GameState, PacketDirection

STATUS_CLIENTBOUND_MAP = generate_packet_map(PacketDirection.CLIENTBOUND, GameState.STATUS)
```

Which, if you were to print it, would look like this:

```
{
    0: <class 'mcproto.packets.status.status.StatusResponse'>
    1: <class 'mcproto.packets.status.ping.PingPong'>,
}
```

Telling us that in the status gamestate, for the clientbound direction, these are the only packet we can receive,
and showing us the actual packet classes for every possible ID number.

#### Building our own packets

Our first packet will always have to be a Handshake, this is the only packet in the entire handshaking state, and it's
a "gateway", after which we get moved to a different state, specifically, either to STATUS (to obtain information about
the server, such as motd, amount of players, or other details you'd see in the multiplayer screen in your MC client).

```python
from mcproto.packets.handshaking.handshake import Handshake, NextState

my_handshake = Handshake(
    # Once again, we use an old protocol version so that even older servers will respond
    protocol_version=47,
    server_address="mc.hypixel.net",
    server_port=25565,
    next_state=NextState.STATUS,
)
```

That's it! We've now constructed a full handshake packet with all of the data it should contain. You might remember
from the example above, that we originally had to look at the protocol specification, find the handshake packet and
construct it's data as a Buffer with all of these variables.

With these packet classes, you can simply follow your editor's autocompletion to see what this packet requires, pass it
in and the data will be constructed for you from these attributes, without constantly cross-checking with the wiki.

For completion, let's also construct the status request packet that we were sending to instruct the server to send us
back the status response packet.

```python
from mcproto.packets.status.status import StatusRequest

my_status_request = StatusRequest()
```

This one was even easier, as the status request packet alone doesn't contain any special data, it's just a request to
the server to send us some data back.

#### Sending packets

To actually send out a packet to the server, we'll need to create a connection, and use the custom functions
responsible for sending packets out. Let's see it:

```python
from mcproto.packets import async_write_packet
from mcproto.connection import TCPAsyncConnection

async def main():
    ip = "mc.hypixel.net"
    port = 25565

    async with (await TCPAsyncConnection.make_client((ip, port), 2)) as connection:
        await async_write_packet(connection, my_handshake)
        # my_handshake is a packet we've created in the example before
```

Much easier than the manual version, isn't it?

#### Receiving packets

Alright, we might now know how to send a packet, but how do we receive one? Let's see:

```python
# Let's say we already have a connection at this moment, after all, how else would
# we've gotten into the STATUS game state.
# Also, let's do something different, let's say we have a synchronous connection, just for fun
from mcproto.connection import TCPSyncConnection
conn: TCPSyncConnection

# With a synchronous connection, comes synchronous reader, so instead of using async_read_packet,
# we'll use sync_read_packet here
from mcproto.packets import sync_read_packet

# But remember? To read a packet, we'll need to have that packet map, telling us which IDs represent
# which actual packet types. Let's pass in the one we've constructed before
packet = sync_read_packet(conn, STATUS_CLIENTBOUND_MAP)

# Cool! We've got back a packet, let's see what kind of packet we got back
from mcproto.packets.status.status import StatusResponse
from mcproto.packets.status.ping import PingPong

if isinstance(packet, StatusResponse):
    ...
elif isinstance(packet, PingPong):
    ...
else:
    raise Exception("Impossible, there aren't other client bound packets in the STATUS game state")
```

#### Requesting status

Alright, so let's actually try to put all of this knowledge together, and create something meaningful. Let's replicate
the status obtaining logic from the manual example, but with these new packet classes:

```python
from mcproto.connection import TCPAsyncConnection
from mcproto.packets import async_write_packet, async_read_packet, generate_packet_map
from mcproto.packets.packet import PacketDirection, GameState
from mcproto.packets.handshaking.handshake import Handshake, NextState
from mcproto.packets.status.status import StatusRequest, StatusResponse
from mcproto.packets.status.ping import PingPong

STATUS_CLIENTBOUND_MAP = generate_packet_map(PacketDirection.CLIENTBOUND, GameState.STATUS)


async def get_status(ip: str, port: int) -> dict:
    handshake_packet = Handshake(
        protocol_version=47,
        server_address=ip,
        server_port=port,
        next_state=NextState.STATUS,
    )
    status_req_packet = StatusRequest()

    async with (await TCPAsyncConnection.make_client((ip, port), 2)) as connection:
        # We start out at HANDSHAKING game state
        await async_write_packet(connection, handshake_packet)
        # After sending the handshake, we told the server to now move us into the STATUS game state
        await async_write_packet(connection, status_req_packet)
        # Since we're still in STATUS game state, we use the status packet map when reading
        packet = await async_read_packet(connection, STATUS_CLIENTBOUND_MAP)

    # Now that we've got back the packet, we no longer need the connection, we won't be sending
    # anything else, so let's get out of the context manager.

    # Now, we should always first make sure it really is the packet we expected
    if not isinstance(packet, StatusResponse):
        raise ValueError(f"We've got an unexpected packet back: {packet!r}")

    # Since we know we really are dealing with a status response, let's get out it's data, and return it
    return packet.data
```

Well, that wasn't so hard, was it?

### Using Client class for communication

Now that you understand how packets work, let's take a look at a much nicer and easier way to do this. Note that it's
still very important that you understand the basics shown above, as even though this is the best way of using mcproto,
and by far the easiest, as a lot of the flows are already implemented for you, if you intent on writing any more
complex bot accounts or doing similar things, you will still need to understand how to work with packets on their own,
and where to learn what to send and when.

```python

import httpx

from mcproto.client import Client
from mcproto.connection import TCPAsyncConnection
from mcproto.auth.account import Account
from mcproto.types.uuid import UUID

HOST = "localhost"
PORT = 25565

MINECRAFT_USERNAME = "YourMinecraftUsername"

# To get your UUID, go to:  # https://api.mojang.com/users/profiles/minecraft/YourMinecraftUsername
MINECRAFT_UUID = UUID("YourMinecraftUUID")

# This can be left empty for warez accounts, but if you want to connect to online mode servers,
# you will need to set this. See: https://mcproto.readthedocs.io/en/stable/usage/authentication/
MINECRAFT_ACCESS_TOKEN = ""


account = Account(MINECRAFT_USERNAME, MINECRAFT_UUID, MINECRAFT_ACCESS_TOKEN)


async def main():
    async with httpx.AsyncClient() as client:
        async with (await TCPAsyncConnection.make_client((HOST, PORT), 2)) as connection:
            client = Client(
                host="localhost",
                port=25565,
                httpx_client=client,
                account=account,
                conn=connection,
                protocol_version=763,  # 1.20.1
            )

            # To request status, you can now simply do:
            status_response = client.status()

            # `status_response` will now contain an instance of StatusResponse packet,
            # so you can access the data just like in the above example, with `status_response.data`

            # In the back, the `status` function has performed a handshake to transition us from
            # the initial (None) game state, to the STATUS game state, and then sent a status
            # request, getting back a response.

            # The Client instance also includes a `login` function, which is capable to go through
            # the entire login flow, leaving you in PLAY game state. Note that unless you've
            # set MINECRAFT_ACCESS_TOKEN, you will only be able to do this for warez servers.

            # But since we just called `status`, it left us in the STATUS game state, but we need
            # to be in LOGIN game state. The `login` function will work if called from an initial
            # game state (None), as it's smart enough to perform a handshake getting us to LOGIN,
            # however it doesn't know what to do from STATUS game state.

            # What we can do, is simply set game_state back to None (this is what happens during
            # initialization of the Client class), making the login function send out another
            # handshake, this time transitioning to LOGIN instead of STATUS. We could also create
            # a completely new client instance.
            client.game_state = None

            client.login()

            # Play state, yay!
```
