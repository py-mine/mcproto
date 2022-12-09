# Mcproto

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
    # (this is what you see in the multiplayer server list, i.e. the server's motd, icon, info about how many players
    # are connected, etc.)

    # To do this, we first need to understand how are minecraft packets composed, and take a look at the specific
    # packets that we're interested in. Thankfully, there's an amazing community made wiki that documents all of this!
    # You can find it at https://wiki.vg/

    # Alright then, let's take a look at the (uncompressed) packet format specification:
    # https://wiki.vg/Protocol#Packet_format
    # From the wiki, we can see that a packet is composed of 3 fields:
    # Packet length (in bytes), sent as a variable length integer (combined length of the 2 fields below)
    # Packet ID, also sent as varint (each packet has it's own unique number, that we use to find out which packet it is)
    # Data, specific to the individual packet

    # Ok then, with this knowledge, let's establish a connection with our server by sending it a handhshake, and
    # obtain the status data from it.

    # First, let's take a look at the Handshake packet:
    # https://wiki.vg/Protocol#Handshake
    handshake = Buffer()
    handshake.write_varint(47)  # Protocol version (using something really old so that it works with almost any server)
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
    await conn.write(packet)  # Second + Third fileds (packet id + data)


async def status(conn: TCPAsyncConnection, ip: str, port: int = 25565) -> dict:
    # This function will be called right after a handshake
    # Sending this packet told the server recognize our connection, and since we've specified the intention
    # to query status, it then moved us to STATUS game state.

    # Different game states have different packets that we can send out, for example there is a game state
    # for login, that we're put into while joining the server, and from it, we tell the server our username
    # player UUID, etc.

    # The packet IDs are unique to each game state, so since we're now in status state, a packet with ID of
    # 0 is no longer the handshake packet, but rather the status request packet (precisely what we need).
    # https://wiki.vg/Protocol#Status_Request

    # The status request packet is empty, and doesn't contain any data, it just instructs the server to send
    # us back a status response packet. Let's send it!
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

    # Interesting, this packet has an ID of 0, but wasn't that the status request packet? We wanted a response tho.
    # Well, actually, if we take a look at the status response packet at the wiki, it really has an ID of 0:
    # https://wiki.vg/Protocol#Status_Response
    # Aha, so not only are packet ids unique between game states, they're also unique between the direction
    # a server bound packet (sent by client, with server as the destination) can have an id of 0, while a
    # client bound packet (sent by server, with client as the destination) can have the same id, and mean something
    # else.

    # Alright then, so we know what we got is a status response packet, let's read the wiki a bit further and see what
    # data it actually contains, and see how we can get it out.
    # Hmmm, it contains a UTF-8 encoded string that represents JSON data, ok, so let's get that string, it's still in
    # our buffer.
    received_string = response.read_utf()

    # Now, let's just use the json module, convert the string into some json object (in this case, a dict)
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
