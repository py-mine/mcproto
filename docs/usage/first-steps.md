# Manual communication with the server

This example demonstrates how to interact with a Minecraft server using mcproto at it's lowest-level interface. It
avoids the built-in packet classes to show how to manually handle data through mcproto's connection and buffer classes.
Although this isn’t the typical use case for mcproto, it provides insight into the underlying Minecraft protocol, which
is crucial to understand before transitioning to using the higher-level packet handling.

In this example, we'll retrieve a server's status — information displayed in the multiplayer server list, such as the
server's MOTD, icon, and player count.

## Step-by-step guide

### Handshake with the server

The first step when doing pretty much any kind of communication with the server is establishing a connection and
sending a "handshake" packet.

??? question "What even is a packet?"

    A packet is a structured piece of data sent across a network to encode an action or message. In games, packets
    allow different kinds of information — such as a player's movement, an item pickup, or a chat message — to be
    communicated in a structured way, with each packet tailored for a specific purpose.

    Every packet has a set structure with fields that identify it and hold its data, making it clear what action or
    event the packet is meant to represent. While packets may carry different types of information, they usually follow
    a similar format, so the game’s client and server can read and respond to them easily.

To do this, we first need to understand Minecraft packets structure in general, then focus on the specific handshake
packet format. To find this out, we recommend using [minecraft.wiki], which is a fantastic resource, detailing all of
the Minecraft protocol logic.

So, according to the [Packet Format][docs-packet-format] page, a Minecraft packet has three fields:

- **Packet length**: the total size of the Packet ID and Data fields (in bytes). Sent in a variable length integer
  format.
- **Packet ID**: uniquely identifies which packet this is. Also sent in the varint format.
- **Data**: the packet's actual content. This will differ depending on the packet type.

Another important information to know is that Minecraft protocol operates in “states,” each with its own set of packets
and IDs. For example, the same packet ID in one state may represent a completely different packet in another state.
Upon establishing a connection with a Minecraft server, you'll begin in the "handshaking" state, with only one packet
available: the handshake packet. This packet tells the server which state to enter next.

In our case, we’ll request to enter the "status" state, used for obtaining server information (in contrast, the "login"
state would be used to join the server).

Next, let’s look at the specifics of the handshake packet on minecraft.wiki [here][docs-handshake].

From here, we can see that the handshake packet has an ID of `0` and should contain the following data (fields):

- **Protocol Version**: The version of minecraft protocol (for compatibility), sent as a varint.
- **Server Address**: The hostname or IP that was used to connect to the server, sent as a string with max length of
  255 characters.
- **Server Port**: The port number (usually 25565), sent as unsigned short.
- **Next State**: The desired state to transition to, sent as a varint. (1 for "status".)

Armed with this information, we can start writing code to send the handshake:

```python
from mcproto.buffer import Buffer
from mcproto.connection import TCPAsyncConnection
from mcproto.protocol.base_io import StructFormat


async def handshake(conn: TCPAsyncConnection, ip: str, port: int = 25565) -> None:
    handshake = Buffer()
    # We use 47 for the protocol version, as which is quite old. We do that to make sure that this code
    # will work with almost any server, including older ones. Using a newer protocol number may result
    # in older servers refusing to respond.
    handshake.write_varint(47)
    handshake.write_utf(ip)
    handshake.write_value(StructFormat.USHORT, port)
    handshake.write_varint(1)  # The next state should be "status"

    # Nice! Now we have the packet data, stored in a buffer object.
    # This is the data field in the packet format specification.

    # Let's prepare another buffer that will contain the last 2 packet format fields (packet id and data).
    # We do this since the first field will require us to know the size of these two combined,
    # so let's put them into 1 buffer first:
    packet = Buffer()
    packet.write_varint(0)  # Handshake packet ID
    packet.write(handshake)  # The entire handshake data, from our previous buffer.

    # And finally, it's time to send it!
    await conn.write_varint(len(packet))  # First field (size of packet id + data)
    await conn.write(packet)  # Second + Third fields (packet id + data)
```

### Running the code

Now, you may be wondering how to actually run this code, what is `TCPAsyncConnection`? Essentially, it's just a wrapper
around a socket connection, designed specifically for communication with Minecraft servers.

To create an instance of this connection, you'll want to use an `async with` statement, like so:

```python
import asyncio

from mcproto.connection import TCPAsyncConnection

async def main():
    ip = "mc.hypixel.net"
    port = 25565

    async with (await TCPAsyncConnection.make_client((ip, port), 2)) as connection:
        await handshake(connection, ip, port)

def start():
    # Just some boilerplate code that we can run our asynchronous main function
    asyncio.run(main())
```

Currently, this code only establishes a connection and requests a state transition to "status", so when running it you
won't see any meaningful result just yet.

!!! tip "Synchronous handling"

    Even though we're using asynchronous connection in this example, mcproto does also provide a synchronous
    version: `TCPSyncConnection`.

    While you can use this synchronous option, we recommend the asynchronous approach as it highlights blocking
    operations with the `await` keyword and allows other tasks to run concurrently, while these blocking operations are
    waiting.

### Obtaining server status

Now comes the interesting part, we'll request a status from the server, and read the response that it sends us. Since
we're already in the status game state by now, we'll want to take a look at the packets that are available in this
state. Once again, minecraft.wiki details all of this for us [here][docs-status].

We can notice that the packets are split into 2 categories: **client-bound** and **server-bound**. We'll first want to
look at the server-bound ones (i.e. packets targeted to the server, sent by the client - us). There are 2 packets
listed here: Ping Request and Status request. Ping is only here to check if the server is online, and allow us to
measure how long the response took, getting the latency, we're not that interested in doing this now, we want to see
some actual useful data from the server, so we'll choose the Status request packet.

Since this packet just tells the server to send us the status, it actually doesn't contain any data fields for us to
add, so the packet itself will be empty:

```python
from mcproto.buffer import Buffer
from mcproto.connection import TCPAsyncConnection

async def status_request(conn: TCPAsyncConnection) -> None:
    # Let's construct a buffer with the packet ID & packet data (like we saw in the handshake example already)
    # However, since the status request packet doesn't contain any data, we just need to set the packet id.
    packet = Buffer()
    packet.write_varint(0)  # Status request packet ID

    await conn.write_varint(len(packet))
    await conn.write(packet)
```

After we send this request, the server should respond back to us. But what will it respond with? Well, let's find out:

```python
from mcproto.buffer import Buffer
from mcproto.connection import TCPAsyncConnection

async def read_status_response(conn: TCPAsyncConnection) -> None:
    # Remember, the packet format states that we first receive a length, then packet id, then data
    _response_len = await conn.read_varint()
    _response = await conn.read(_response_len)  # will give us a bytearray

    # Amazing, we've just received data from the server! But it's just bytes, let's turn it into
    # a Buffer object, which includes helpful methods that allow us to read from it
    response = Buffer(_response)
    packet_id = response.read_varint()  # Remember, 2nd field is the packet ID, encoded as a varint

    print(packet_id)
```

Adjusting our main function to run the new logic:

```python
async def main():
    ip = "mc.hypixel.net"
    port = 25565

    async with (await TCPAsyncConnection.make_client((ip, port), 2)) as connection:
        await handshake(connection, ip, port)
        await status_request(connection)
        await read_status_response(connection)
```

Running the code now, we can see it print `0`. Aha! That's our packet ID, so let's see what the server sent us. So,
looking through the list of **client-bound** packets in the wiki, this is the **Status Response Packet**!

!!! note

    Interesting, this packet has an ID of 0, wasn't that the status request packet?

    Indeed, packets can have the same ID in different directions, so packet ID `0` for a client-bound response is
    distinct from packet ID `0` for a server-bound request.

Alright then, let's see what the status response packet contains: The wiki says it just has a single UTF-8 string
field, which contains JSON data. Let's adjust our function a bit, and read that data:

```python
import json

from mcproto.buffer import Buffer
from mcproto.connection import TCPAsyncConnection

async def read_status_response(conn: TCPAsyncConnection) -> dict:  # We're now returning a dict
    _response_len = await conn.read_varint()
    _response = await conn.read(_response_len)

    response = Buffer(_response)
    packet_id = response.read_varint()

    # Let's always make sure we got the status response packet here.
    assert packet_id == 0

    # Let's now read that single UTF8 string field, it should still be in our buffer:
    received_string = response.read_utf()

    # Now, let's just use the json built-in library, convert the JSON string into a python object
    # (in this case, it will be a dict)
    data = json.loads(received_string)

    # Cool, we now have the actual status data that the server has provided, we should return them
    # from the function now.
    # Before we do that though, let's just do a sanity-check and ensure that the buffer doesn't contain
    # any more data.
    assert response.remaining == 0  # 0 bytes (everything was read)
    return data
```

Finally, we'll adjust the main function to show some of the status data that we obtained:

```python
async def main():
    ip = "mc.hypixel.net"
    port = 25565

    async with (await TCPAsyncConnection.make_client((ip, port), 2)) as connection:
        await handshake(connection, ip, port)
        await status_request(connection)
        data = await read_status_response(connection)

    # Wohoo, we got the status data! Let's see it
    print(data["players"]["max"])  # This is the server's max player amount (slots)
    print(data["players"]["online"])  # This is how many people are currently online
    print(data["description"])  # And here's the motd

    # There's a bunch of other things in this data, try it out, see what you can find!
```

[minecraft.wiki]: https://minecraft.wiki/w/Java_Edition_protocol
[docs-packet-format]: https://minecraft.wiki/w/Java_Edition_protocol/Packets#Packet_format
[docs-handshake]: https://minecraft.wiki/w/Java_Edition_protocol/Packets#Handshake
[docs-status]: https://minecraft.wiki/w/Java_Edition_protocol/Packets#Status
