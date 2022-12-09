from __future__ import annotations

import gzip
from collections.abc import Mapping
from typing import TypeVar

from mcproto.buffer import Buffer
from mcproto.packets.abc import Packet
from mcproto.packets.map import PacketMap
from mcproto.protocol.base_io import BaseAsyncReader, BaseAsyncWriter, BaseSyncReader, BaseSyncWriter

T_Packet = TypeVar("T_Packet", bound=Packet)

__all__ = [
    "async_read_packet",
    "async_write_packet",
    "sync_read_packet",
    "sync_write_packet",
]

# PACKET FORMAT:
# | Field name  | Field type    | Notes                                 |
# |-------------|---------------|---------------------------------------|
# | Length      | 32-bit varint | Length (in bytes) of PacketID + Data  |
# | Packet ID   | 32-bit varint |                                       |
# | Data        | byte array    | Internal data to packet of given id   |


# Since the read functions here require PACKET_MAP, we can't move these functions
# directly into BaseWriter/BaseReader classes, as that would be a circular import

PACKET_MAP = PacketMap()


def _serialize_packet(packet: Packet, *, compressed: bool = False) -> Buffer:
    """Serialize the internal packet data, along with it's packet id."""
    packet_data = packet.serialize()

    # Base packet buffer should only contain packet id and internal packet data
    packet_buf = Buffer()
    packet_buf.write_varint(packet.PACKET_ID)
    packet_buf.write(packet_data)

    # If we're serializing a packet as compressed, we compress the packet buffer data
    # and prepend a varint with the size of uncompressed pacekt buffer
    if compressed:
        data_length = len(packet_buf)
        packet_buf = Buffer(gzip.compress(packet_buf))

        data_buf = Buffer()
        data_buf.write_varint(data_length)
        data_buf.write(packet_buf)
        return data_buf
    else:
        return packet_buf


def _deserialize_packet(
    buf: Buffer, *, packet_map: Mapping[int, type[T_Packet]], compressed: bool = False
) -> T_Packet:
    """Deserialize the packet id and it's internal data."""
    if compressed:
        buf.read_varint()  # We don't need this uncompressed length
        compressd_packet_data = buf.read(buf.remaining)
        buf = Buffer(gzip.decompress(compressd_packet_data))

    packet_id = buf.read_varint()
    packet_data = buf.read(buf.remaining)

    return packet_map[packet_id].deserialize(Buffer(packet_data))


def sync_write_packet(writer: BaseSyncWriter, packet: Packet, *, compressed: bool = False) -> None:
    """Write given packet."""
    data_buf = _serialize_packet(packet, compressed=compressed)
    writer.write_bytearray(data_buf)


async def async_write_packet(writer: BaseAsyncWriter, packet: Packet, *, compressed: bool = False) -> None:
    """Write given packet."""
    data_buf = _serialize_packet(packet, compressed=compressed)
    await writer.write_bytearray(data_buf)


def sync_read_packet(
    reader: BaseSyncReader,
    *,
    packet_map: Mapping[int, type[T_Packet]],
    compressed: bool = False,
) -> T_Packet:
    """Read a packet."""
    data_buf = Buffer(reader.read_bytearray())
    return _deserialize_packet(data_buf, packet_map=packet_map, compressed=compressed)


async def async_read_packet(
    reader: BaseAsyncReader,
    *,
    packet_map: Mapping[int, type[T_Packet]],
    compressed: bool = False,
) -> T_Packet:
    """Read a packet."""
    data_buf = Buffer(await reader.read_bytearray())
    return _deserialize_packet(data_buf, packet_map=packet_map, compressed=compressed)
