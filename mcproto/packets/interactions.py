from __future__ import annotations

import zlib
from collections.abc import Mapping
from typing import TypeVar

from mcproto.buffer import Buffer
from mcproto.packets.packet import Packet
from mcproto.protocol.base_io import BaseAsyncReader, BaseAsyncWriter, BaseSyncReader, BaseSyncWriter

__all__ = ["async_read_packet", "async_write_packet", "sync_read_packet", "sync_write_packet"]

T_Packet = TypeVar("T_Packet", bound=Packet)

# PACKET FORMAT:
# | Field name  | Field type    | Notes                                 |
# |-------------|---------------|---------------------------------------|
# | Length      | 32-bit varint | Length (in bytes) of PacketID + Data  |
# | Packet ID   | 32-bit varint |                                       |
# | Data        | byte array    | Internal data to packet of given id   |

# COMPRESSED PACKET FORMAT:
# | Compressed? | Field name    | Field type    | Notes                                                             |
# | ------------|---------------|---------------|-------------------------------------------------------------------|
# | No          | Packet Length | 32-bit varint | Length of (Data Length) + Compressed length of (Packet ID + Data) |
# | No          | Data Length   | 32-bit varint | Length of uncompressed (PacketID + Data)                          |
# | Yes         | Packet ID     | 32-bit varint | Zlib compressed packet ID                                         |
# | Yes         | Data          | byte array    | Zlib compressed packet data                                       |
#
# Compression should only be used when LoginSetCompression packet is received.
# In this packet, a compression threshold will be sent by the server. This is
# a number which specifies how large a packet can be at most (it's Data Length),
# before enabling compression. If a packet is smaller, compression will not be
# enabled.
#
# However since compression changes how the packet format looks, we need to inform
# the reader whether or not compression was used, so when disabled, we just set
# Data Length to 0, which will mean compression is disabled, and Packet ID and Data
# fields will be sent uncompressed.


# Since the read functions here require PACKET_MAP, we can't move these functions
# directly into BaseWriter/BaseReader classes, as that would be a circular import


def _serialize_packet(packet: Packet, *, compression_threshold: int = -1) -> Buffer:
    """Serialize the internal packet data, along with it's packet id.

    Args:
        packet: The packet to serialize.
        compression_threshold:
            A threshold for the packet length (in bytes), which if surpassed compression should
            be enabled. To disable compression, set this to -1. Note that when enabled, even if
            the threshold isn't crossed, the packet format will be different than with compression
            disabled.
    """
    packet_data = packet.serialize()

    # Base packet buffer should only contain packet id and internal packet data
    packet_buf = Buffer()
    packet_buf.write_varint(packet.PACKET_ID)
    packet_buf.write(packet_data)

    # Compression is enabled
    if compression_threshold >= 0:
        # Only run the actual compression step if we cross the threshold, otherwise
        # send uncompressed data with an extra 0 for data length
        if len(packet_buf) > compression_threshold:
            data_length = len(packet_buf)
            packet_buf = Buffer(zlib.compress(packet_buf))
        else:
            data_length = 0

        data_buf = Buffer()
        data_buf.write_varint(data_length)
        data_buf.write(packet_buf)
        return data_buf
    return packet_buf


def _deserialize_packet(
    buf: Buffer,
    packet_map: Mapping[int, type[T_Packet]],
    *,
    compressed: bool = False,
) -> T_Packet:
    """Deserialize the packet id and it's internal data.

    Args:
        packet_map:
            A mapping of packet id (int) -> packet. Should hold all possible packets for the
            current gamestate and direction. See [`generate_packet_map`][mcproto.packets.packet_map.]
        compressed:
            Boolean flag, if compression is enabled, it should be set to `True`, `False` otherwise.

            You can get this based on [`LoginSetCompression`][mcproto.packets.login.login.] packet,
            which will contain a compression threshold value. This threshold is only useful when writing
            the packets, for reading, we don't care about the specific threshold, we only need to know
            whether compression is enabled or not. That is, if the threshold is set to a non-negative
            number, this should be `True`.
    """
    if compressed:
        data_length = buf.read_varint()
        packet_data = buf.read(buf.remaining)
        # Only run decompression if the threshold was crosed, otherwise the data_length will be
        # set to 0, indicating no compression was done, read the data normally if that's the case
        buf = Buffer(zlib.decompress(packet_data)) if data_length != 0 else Buffer(packet_data)

    packet_id = buf.read_varint()
    packet_data = buf.read(buf.remaining)

    return packet_map[packet_id].deserialize(Buffer(packet_data))


def sync_write_packet(
    writer: BaseSyncWriter,
    packet: Packet,
    *,
    compression_threshold: int = -1,
) -> None:
    """Write given `packet`.

    Args:
        writer: The connection/writer to send this packet to.
        packet: The packet to be sent.
        compression_threshold:
            A threshold packet length, which if crossed compression should be enabled.

            You can get this number from [`LoginSetCompression`][mcproto.packets.login.login.] packet.
            If this packet wasn't sent by the server, set this to -1 (default).
    """
    data_buf = _serialize_packet(packet, compression_threshold=compression_threshold)
    writer.write_bytearray(data_buf)


async def async_write_packet(
    writer: BaseAsyncWriter,
    packet: Packet,
    *,
    compression_threshold: int = -1,
) -> None:
    """Write given `packet`.

    Args:
        writer: The connection/writer to send this packet to.
        packet: The packet to be sent.
        compression_threshold:
            A threshold packet length, which if crossed compression should be enabled.

            You can get this number from [`LoginSetCompression`][mcproto.packets.login.login.] packet.
            If this packet wasn't sent by the server, set this to -1 (default).
    """
    data_buf = _serialize_packet(packet, compression_threshold=compression_threshold)
    await writer.write_bytearray(data_buf)


def sync_read_packet(
    reader: BaseSyncReader,
    packet_map: Mapping[int, type[T_Packet]],
    *,
    compression_threshold: int = -1,
) -> T_Packet:
    """Read a packet.

    Args:
        reader: The connection/reader to receive this packet from.
        packet_map:
            A mapping of packet id (number) -> Packet (class).

            This mapping should contain all of the packets for the current gamestate and direction.
            See [`generate_packet_map`][mcproto.packets.packet_map.]
        compression_threshold:
            A threshold packet length, which if crossed compression should be enabled.

            You can get this number from [`LoginSetCompression`][mcproto.packets.login.login.] packet.
            If this packet wasn't sent by the server, set this to -1 (default).

            Note that during reading, we don't actually need to know the specific threshold, just
            whether or not is is non-negative (whether compression is enabled), as the packet format
            fundamentally changes when it is. That means you can pass any positive number here to
            enable compression, regardless of what it actually is.
    """
    # The packet format fundamentally changes when compression_threshold is non-negative (enabeld)
    # We only care about the sepcific threshold when writing though, for reading (deserialization),
    # we just need to know whether or not compression is enabled
    compressed = compression_threshold >= 0

    data_buf = Buffer(reader.read_bytearray())
    return _deserialize_packet(data_buf, packet_map, compressed=compressed)


async def async_read_packet(
    reader: BaseAsyncReader,
    packet_map: Mapping[int, type[T_Packet]],
    *,
    compression_threshold: int = -1,
) -> T_Packet:
    """Read a packet.

    Args:
        reader: The connection/reader to receive this packet from.
        packet_map:
            A mapping of packet id (number) -> Packet (class).

            This mapping should contain all of the packets for the current gamestate and direction.
            See [`generate_packet_map`][mcproto.packets.packet_map.]
        compression_threshold:
            A threshold packet length, which if crossed compression should be enabled.

            You can get this number from [`LoginSetCompression`][mcproto.packets.login.login.] packet.
            If this packet wasn't sent by the server, set this to -1 (default).

            Note that during reading, we don't actually need to know the specific threshold, just
            whether or not is is non-negative (whether compression is enabled), as the packet format
            fundamentally changes when it is. That means you can pass any positive number here to
            enable compression, regardless of what it actually is.
    """
    # The packet format fundamentally changes when compression_threshold is non-negative (enabeld)
    # We only care about the sepcific threshold when writing though, for reading (deserialization),
    # we just need to know whether or not compression is enabled
    compressed = compression_threshold >= 0

    data_buf = Buffer(await reader.read_bytearray())
    return _deserialize_packet(data_buf, packet_map, compressed=compressed)
