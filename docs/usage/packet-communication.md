# Packet communication

This guide explains how to communicate with the server using our packet classes. It will go over the same example from
[previous page](./first-steps.md), showing how to obtain the server status, but instead of using the low level
interactions, this guide will simplify a lot of that logic with the use of packet classes.

!!! warning "Packets Target the Latest Minecraft Version"

    Mcproto's packet classes are designed to support the **latest Minecraft release**. While packets in the handshaking
    and status game states usually remain compatible across versions, mcproto does NOT guarantee cross-version packet
    compatibility. Using packets in the play game state, for example, will very likely lead to compatibility issues if
    you're working with older Minecraft versions.

    Only the low level interactions are guaranteed to remain compatible across protocol updates, if you need support
    for and older minecraft version, consider downgrading to an older version of mcproto, or using the low level
    interactions.

## Obtaining the packet map

Every packet has a unique ID based on its direction (client to server or server to client) and game state (such as
status, handshaking, login, or play). This ID lets us recognize packet types in different situations, which is crucial
for correctly receiving packets.

To make this process easier, mcproto provides a packet map—essentially a dictionary mapping packet IDs to packet
classes. Here’s how to generate a packet map:

```python
from mcproto.packets import generate_packet_map, GameState, PacketDirection

STATUS_CLIENTBOUND_MAP = generate_packet_map(PacketDirection.CLIENTBOUND, GameState.STATUS)
```

Printing `STATUS_CLIENTBOUND_MAP` would display something like this:

```
{
    0: <class 'mcproto.packets.status.status.StatusResponse'>
    1: <class 'mcproto.packets.status.ping.PingPong'>,
}
```

Telling us that in the STATUS gamestate, for the clientbound direction, these are the only packet we can receive,
and mapping the actual packet classes for every supported packet ID number.

## Using packets

The first packet we send to the server is always a **Handshake** packet. This is the only packet in the entire
handshaking state, and it's a "gateway", after which we get moved to a different state, in our case, that will be the
STATUS state.

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
from the previous low-level example, that we originally had to look at the protocol specification, find the handshake
packet and construct it's data as a Buffer with all of these variables.

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

## Sending packets

To actually send out a packet to the server, we'll need to create a connection, and use mcproto's `async_write_packet`
function, responsible for sending packets. Let's see it:

```python
from mcproto.packets import async_write_packet
from mcproto.connection import TCPAsyncConnection

async def main():
    ip = "mc.hypixel.net"
    port = 25565

    async with (await TCPAsyncConnection.make_client((ip, port), timeout=2)) as connection:
        # Let's send the handshake packet that we've created in the example before
        await async_write_packet(connection, my_handshake)
        # Followed by the status request
        await async_write_packet(connection, my_status_request)
```

Much easier than the manual version, isn't it?

## Receiving packets

Alright, we might now know how to send a packet, but how do we receive one?

Let's see, but this time, let's also try out using the synchronous connection, just for fun:

```python
from mcproto.connection import TCPSyncConnection

# With a synchronous connection, comes synchronous reader/writer functions
from mcproto.packets import sync_read_packet, sync_write_packet

# We'll also need the packet classes from the status game-state
from mcproto.packets.status.status import StatusResponse
from mcproto.packets.status.ping import PingPong

def main():
    ip = "mc.hypixel.net"
    port = 25565

    with TCPSyncConnection.make_client(("mc.hypixel.net", 25565), 2) as conn:
        # First, send the handshake & status request, just like before, but synchronously
        await sync_write_packet(connection, my_handshake)
        await sync_write_packet(connection, my_status_request)

        # To read a packet, we'll also need to have the packet map, telling us which IDs represent
        # which actual packet types. Let's pass in the map that we've constructed before:
        packet = sync_read_packet(conn, STATUS_CLIENTBOUND_MAP)

    # Now that we've got back the packet, we no longer need the connection, we won't be sending
    # anything else, so let's get out of the context manager.

    # Finally, let's handle the received packet:
    if isinstance(packet, StatusResponse):
        ...
    elif isinstance(packet, PingPong):
        ...
    else:
        raise Exception("Impossible, there are no other client bound packets in the STATUS game state")
```

## Requesting status

Alright, so let's actually try to put all of this knowledge together, and create something meaningful. Let's replicate
the status obtaining logic from the manual example, but with these new packet classes:

```python
from mcproto.connection import TCPAsyncConnection
from mcproto.packets import async_write_packet, async_read_packet, generate_packet_map
from mcproto.packets.packet import PacketDirection, GameState
from mcproto.packets.handshaking.handshake import Handshake, NextState
from mcproto.packets.status.status import StatusRequest, StatusResponse

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

    # Now, we should always first make sure it really is the packet we expected
    if not isinstance(packet, StatusResponse):
        raise ValueError(f"We've got an unexpected packet back: {packet!r}")

    # Since we know we really are dealing with a status response, let's get out it's data, and return it
    # this is the same JSON data that we obtained from the first example with the manual interactions
    return packet.data
```

As you can see, this approach is more convenient and eliminates much of the manual packet handling, letting you focus
on higher-level logic!
