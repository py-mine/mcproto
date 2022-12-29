# <img src="https://i.imgur.com/nPCcxts.png" height=25> McProto

[![discord chat](https://img.shields.io/discord/936788458939224094.svg?logo=Discord)](https://discord.gg/C2wX7zduxC)
![supported python versions](https://img.shields.io/pypi/pyversions/mcproto.svg)
[![current PyPI version](https://img.shields.io/pypi/v/mcproto.svg)](https://pypi.org/project/mcproto/)
[![Validation](https://github.com/ItsDrike/mcproto/actions/workflows/validation.yml/badge.svg)](https://github.com/ItsDrike/mcproto/actions/workflows/validation.yml)
[![Unit tests](https://github.com/ItsDrike/mcproto/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/ItsDrike/mcproto/actions/workflows/unit-tests.yml)

This is a heavily Work-In-Progress library, which attempts to be a full wrapper around the minecraft protocol, allowing
for simple interactions with minecraft servers, and perhaps even for use as a base to a full minecraft server
implementation in python (though the speed will very likely be quite terrible, making it probably unusable as any
real-world playable server).

Currently, the library is very limited and doesn't yet have any documentation, so while contributions are welcome, fair
warning that there is a lot to comprehend in the code-base and it may be challenging to understand it all.

## Installation

Mcproto is available on [PyPI](https://pypi.org/project/mcproto/), and can be installed trivially with:

```bash
python3 -m pip install mcproto
```

That said, as mcproto is still in development, the PyPI version will likely go out of date quite soon. This means that
it may lack some already implemented features, or contain already fixed bugs. For that reason, you can also consider
installing mcproto through git, to get the most recent version. But know that while this will mean you'll be getting
all of the new features, this version is much more likely to contain bugs than the one on PyPI, so make your decision
wisely. To install the latest version from git, you can use the command below:

```bash
python3 -m pip install 'mcproto @ git+https://github.com/py-mine/mcproto@main'
```

Alternatively, if you want to poke around with mcproto's code, you can always include mcproto as a full [git
submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules) to your project, or just git clone it directly and play
around with it from REPL.

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

#### Obtaining the packet map

The first thing you'll need to understand about packet classes in mcproto is that they're versioned depending on the
protocol version you're using. As we've already seen with minecraft packets, they're following a certain format, and
for given packet direction and game state, the packet numbers are unique.

This is how we can detect what packet is being received, but because of the different versions that the library can
support, we will need to use a packet map, that will contain all of the mappings for given protocol version, from
which, knowing the state and direction, we can get a dictionary with packet IDs as keys, and the individual packet
classes as values.

This dictionary is crucial to receiving packets, as it's the only thing that tells us which packet class should be
used, once we receive a packet and learn about the packet id. Otherwise we wouldn't know what to do with the data we
obtained.

The first game state we'll be in, before doing anything will always be the handshaking state, so let's see how we could
generate this dictionary for this state, for all of the receiving (client bound) packets.

```python
from mcproto.packets import PACKET_MAP
from mcproto.packets.abc import PacketDirection, GameState

handshaking_packet_map = PACKET_MAP.make_id_map(
    protocol_version=757,
    direction=PacketDirection.CLIENTBOUND,
    game_state=GameState.HANDSHAKING
)

print(handshaking_packet_map)  # {}
```

Notice that the packet map is actually empty, and this is simply because there (currently) aren't any client bound
packets a server can send out for the handshaking game state. Let's see the status gamestate instead:

```python
status_packet_map = PACKET_MAP.make_id_map(
    protocol_version=757,
    direction=PacketDirection.CLIENTBOUND,
    game_state=GameState.STATUS,
)

print(status_packet_map)  # Will print:
# {1: mcproto.packets.v757.status.ping.PingPong, 0: mcproto.packets.v757.status.status.StatusResponse}
```

Cool! These are all of the packets, with their IDs that the server can send in STATUS game state.

#### Creating our own packets


Now, we could create a similar packet map for sending out the packets, and just use it to construct our packets,
however this is not the recommended approach, as it's kind of hard to remember all of the packet IDs, and (at least
currently) it means not having any typing information about what packet class will we get. For that reason, it's
recommended to import packets that we want to send out manually, like so:

```python
from mcproto.packets.v757.handshaking.handshake import Handshake, NextState

my_handshake = Handshake(
    # Once again, we use an old protocol version so that even older servers will work
    protocol_version=47,
    server_address="mc.hypixel.net",
    server_port=25565,
    next_state=NextState.STATUS,
)
```

That's it! We've now constructed a full handshake packet with all of the data it should contain. You might remember
from the example above, that we originally had to look at the protocol specification, find the handshake packet and
construct it's data as a Buffer with all of these variables.

With these packet classes, you can simply follow your editor's function hints to see what this packet requires, pass it
in and the data will be constructed for you from these attributes, once we'll be to sending it.

For completion, let's also construct the status request packet that we were sending to instruct the server to send us
back the status response packet.

```python
from mcproto.packets.v757.status.status import StatusRequest

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

How quick was that? Now compare this to the manual version.

#### Receiving packets

Alright, we might now know how to send a packet, but how do we receive one? Let's see:

```python
from mcproto.packets import PACKET_MAP

# Let's prepare the packet map we'll be using, say we're already in the STATUS game state now
STATUS_PACKET_MAP = PACKET_MAP.make_id_map(
    protocol_version=757,
    direction=PacketDirection.CLIENTBOUND,
    game_state=GameState.STATUS
)

# Let's say we already have a connection at this moment, after all, how else would
# we've gotten into the STATUS game state.
# Also, let's do something different, let's say we have a synchronous connection
from mcproto.connection import TCPSyncConnection
conn: TCPSyncConnection

# With a synchronous connection, comes synchronous reader, so instead of using async_read_packet,
# we'll use sync_read_packet here
from mcproto.packets import sync_read_packet

packet = sync_read_packet(conn, STATUS_PACKET_MAP)

# Cool! We've got back a packet, but what packet is it? Let's import the packet classes it could
# be and check against them
from mcproto.packets.v757.status.status import StatusResponse
from mcproto.packets.v757.status.ping import PingPong

if isinstance(packet, StatusResponse):
    ...
elif isinstance(packet, PingPong):
    ...
else:
    raise Exception("Impossible, there aren't other client bound packets in the STATUS game state")
```

#### Requesting status

Now let's actually do something meaningful, and replicate the entire example from the manual version using packets,
let's see just how much simpler it will be:

```python
from mcproto.connection import TCPAsyncConnection
from mcproto.packets import async_write_packet, async_read_packet, PACKET_MAP
from mcproto.packets.abc import PacketDirection, GameState
from mcproto.packets.v757.handshaking.handshake import Handshake, NextState
from mcproto.packets.v757.status.status import StatusRequest, StatusResponse

STATUS_PACKET_MAP = PACKET_MAP.make_id_map(
    protocol_version=757,
    direction=PacketDirection.CLIENTBOUND,
    game_state=GameState.STATUS
)


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
        packet = await async_read_packet(connection, STATUS_PACKET_MAP)

    # Now that we've got back the packet, we no longer need the connection, we won't be sending
    # anything else. Let's just make sure it really is the packet we expected
    if not isinstance(packet, StatusResponse):
        raise ValueError(f"We've got an unexpected packet back: {packet!r}")

    # Now that we know we're dealing with a status response, let's get out it's data, and return in
    return packet.data
```

Well, that wasn't so hard, was it?
