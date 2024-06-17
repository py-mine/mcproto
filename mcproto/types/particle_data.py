from __future__ import annotations
from attrs import define
from mcproto.types.abc import MCType
from mcproto.types.slot import Slot
from mcproto.types.vec3 import Position
from typing import cast, final
from typing_extensions import override, Self
from mcproto.buffer import Buffer
from mcproto.protocol.base_io import StructFormat


@final
@define
class ParticleData(MCType):
    """Represents the data of a particle.

    .. note:: Only some of the parameters can be used at the same time. They are determined by the particle ID.

    :param particle_id: The ID of the particle (used to determine the actual data to read).
    :type particle_id: int

    :param block_state: The ID of the block state.
    :type block_state: int, optional

    :param red: The red color component of the particle.
    :type red: float, optional
    :param green: The green color component of the particle.
    :type green: float, optional
    :param blue: The blue color component of the particle.
    :type blue: float, optional
    :param scale: The scale of the particle.
    :type scale: float, optional

    :param from_red: The initial red color component of the particle.
    :type from_red: float, optional
    :param from_green: The initial green color component of the particle.
    :type from_green: float, optional
    :param from_blue: The initial blue color component of the particle.
    :type from_blue: float, optional
    :param to_red: The final red color component of the particle.
    :type to_red: float, optional
    :param to_green: The final green color component of the particle.
    :type to_green: float, optional
    :param to_blue: The final blue color component of the particle.
    :type to_blue: float, optional

    :param roll: How much the particle will be rotated when displayed.
    :type roll: float, optional

    :param item: The item that will be displayed as a particle.
    :type item: :class:`mcproto.types.item.Slot`, optional

    :param source_type: The type of the source of the particle. (0 for `minecraft:block`, 1 for `minecraft:entity`)
    :type source_type: int, optional
    :param block_position: The position of the block that is the source of the particle. (used when `source_type` is 0)
    :type block_position: :class:`mcproto.types.vec3.Position`, optional
    :param entity_id: The ID of the entity that is the source of the particle. (used when `source_type` is 1)
    :type entity_id: int, optional
    :param entity_eye_height: The height of the entity's eye relative to the entity. (used when `source_type` is 1)
    :type entity_eye_height: float, optional
    :param tick: The amount of ticks it takes for the vibration to travel from its source to its destination.
    :type tick: int, optional

    :param delay: The delay before the particle is displayed.
    :type delay: int, optional
    """

    # TODO: Use registries for particle IDs

    WITH_BLOCK_STATE = (
        2,  # minecraft:block
        3,  # minecraft:block_marker
        27,  # minecraft:falling_dust
    )

    WITH_RGB_SCALE = (
        14,  # minecraft:dust
    )

    WITH_RGB_TRANSITION = (
        15,  # minecraft:dust_color_transition
    )

    WITH_ROLL = (
        33,  # minecraft:sculk_charge
    )

    WITH_ITEM = (
        42,  # minecraft:item
    )

    WITH_VIBRATION = (
        43,  # minecraft:vibration
    )

    WITH_DELAY = (
        96,  # minecraft:shriek
    )

    particle_id: int
    block_state: int | None = None
    red: float | None = None
    green: float | None = None
    blue: float | None = None
    scale: float | None = None
    from_red: float | None = None
    from_green: float | None = None
    from_blue: float | None = None
    to_red: float | None = None
    to_green: float | None = None
    to_blue: float | None = None
    roll: float | None = None
    item: Slot | None = None
    source_type: int | None = None
    block_position: Position | None = None
    entity_id: int | None = None
    entity_eye_height: float | None = None
    tick: int | None = None
    delay: int | None = None

    @override
    def serialize_to(self, buf: Buffer, with_id: bool = True) -> None:
        if with_id:
            buf.write_varint(self.particle_id)
        if self.particle_id in self.WITH_BLOCK_STATE:
            self.block_state = cast(int, self.block_state)
            buf.write_varint(self.block_state)
        if self.particle_id in self.WITH_RGB_SCALE:
            self.red = cast(float, self.red)
            self.green = cast(float, self.green)
            self.blue = cast(float, self.blue)
            buf.write_value(StructFormat.FLOAT, self.red)
            buf.write_value(StructFormat.FLOAT, self.green)
            buf.write_value(StructFormat.FLOAT, self.blue)
        if self.particle_id in self.WITH_RGB_TRANSITION:
            self.from_red = cast(float, self.from_red)
            self.from_green = cast(float, self.from_green)
            self.from_blue = cast(float, self.from_blue)
            self.scale = cast(float, self.scale)
            self.to_red = cast(float, self.to_red)
            self.to_green = cast(float, self.to_green)
            self.to_blue = cast(float, self.to_blue)
            buf.write_value(StructFormat.FLOAT, self.from_red)
            buf.write_value(StructFormat.FLOAT, self.from_green)
            buf.write_value(StructFormat.FLOAT, self.from_blue)
            buf.write_value(StructFormat.FLOAT, self.scale)
            buf.write_value(StructFormat.FLOAT, self.to_red)
            buf.write_value(StructFormat.FLOAT, self.to_green)
            buf.write_value(StructFormat.FLOAT, self.to_blue)
        if self.particle_id in self.WITH_ROLL:
            self.roll = cast(float, self.roll)
            buf.write_value(StructFormat.FLOAT, self.roll)
        if self.particle_id in self.WITH_ITEM:
            self.item = cast(Slot, self.item)
            self.item.serialize_to(buf)
        if self.particle_id in self.WITH_VIBRATION:
            self.source_type = cast(int, self.source_type)
            self.tick = cast(int, self.tick)
            buf.write_varint(self.source_type)
            if self.source_type == 0:
                self.block_position = cast(Position, self.block_position)
                self.block_position.serialize_to(buf)
            else:
                self.entity_id = cast(int, self.entity_id)
                self.entity_eye_height = cast(float, self.entity_eye_height)
                buf.write_varint(self.entity_id)
                buf.write_value(StructFormat.FLOAT, self.entity_eye_height)
            buf.write_varint(self.tick)
        if self.particle_id in self.WITH_DELAY:
            self.delay = cast(int, self.delay)
            buf.write_varint(self.delay)

    @classmethod
    @override
    def deserialize(cls, buf: Buffer, particle_id: int | None = None) -> Self:
        particle_id = buf.read_varint() if particle_id is None else particle_id
        block_state = None
        red = None
        green = None
        blue = None
        scale = None
        from_red = None
        from_green = None
        from_blue = None
        to_red = None
        to_green = None
        to_blue = None
        roll = None
        item = None
        source_type = None
        block_position = None
        entity_id = None
        entity_eye_height = None
        tick = None
        delay = None

        if particle_id in cls.WITH_BLOCK_STATE:
            block_state = buf.read_varint()
        if particle_id in cls.WITH_RGB_SCALE:
            red = buf.read_value(StructFormat.FLOAT)
            green = buf.read_value(StructFormat.FLOAT)
            blue = buf.read_value(StructFormat.FLOAT)
        if particle_id in cls.WITH_RGB_TRANSITION:
            from_red = buf.read_value(StructFormat.FLOAT)
            from_green = buf.read_value(StructFormat.FLOAT)
            from_blue = buf.read_value(StructFormat.FLOAT)
            scale = buf.read_value(StructFormat.FLOAT)
            to_red = buf.read_value(StructFormat.FLOAT)
            to_green = buf.read_value(StructFormat.FLOAT)
            to_blue = buf.read_value(StructFormat.FLOAT)
        if particle_id in cls.WITH_ROLL:
            roll = buf.read_value(StructFormat.FLOAT)
        if particle_id in cls.WITH_ITEM:
            item = Slot.deserialize(buf)
        if particle_id in cls.WITH_VIBRATION:
            source_type = buf.read_varint()
            if source_type == 0:
                block_position = Position.deserialize(buf)
            else:
                entity_id = buf.read_varint()
                entity_eye_height = buf.read_value(StructFormat.FLOAT)
            tick = buf.read_varint()
        if particle_id in cls.WITH_DELAY:
            delay = buf.read_varint()

        return cls(
            particle_id=particle_id,
            block_state=block_state,
            red=red,
            green=green,
            blue=blue,
            scale=scale,
            from_red=from_red,
            from_green=from_green,
            from_blue=from_blue,
            to_red=to_red,
            to_green=to_green,
            to_blue=to_blue,
            roll=roll,
            item=item,
            source_type=source_type,
            block_position=block_position,
            entity_id=entity_id,
            entity_eye_height=entity_eye_height,
            tick=tick,
            delay=delay,
        )

    @override
    def validate(self) -> None:  # noqa: PLR0912 # I know but what can I do?
        if self.particle_id in self.WITH_BLOCK_STATE:
            if self.block_state is None:
                raise ValueError("block_state is required for this particle ID")
        elif self.particle_id in self.WITH_RGB_SCALE:
            if self.red is None or self.green is None or self.blue is None:
                raise ValueError("red, green, and blue are required for this particle ID")
        elif self.particle_id in self.WITH_RGB_TRANSITION:
            if self.from_red is None or self.from_green is None or self.from_blue is None:
                raise ValueError("from_red, from_green, and from_blue are required for this particle ID")
            if self.scale is None:
                raise ValueError("scale is required for this particle ID")
            if self.to_red is None or self.to_green is None or self.to_blue is None:
                raise ValueError("to_red, to_green, and to_blue are required for this particle ID")
        elif self.particle_id in self.WITH_ROLL:
            if self.roll is None:
                raise ValueError("roll is required for this particle ID")
        elif self.particle_id in self.WITH_ITEM:
            if self.item is None:
                raise ValueError("item is required for this particle ID")
        elif self.particle_id in self.WITH_VIBRATION:
            if self.source_type is None:
                raise ValueError("source_type is required for this particle ID")
            if self.source_type == 0:
                if self.block_position is None:
                    raise ValueError("block_position is required for this particle ID with source_type 0")
            else:
                if self.entity_id is None:
                    raise ValueError("entity_id is required for this particle ID with source_type 1")
                if self.entity_eye_height is None:
                    raise ValueError("entity_eye_height is required for this particle ID with source_type 1")
            if self.tick is None:
                raise ValueError("tick is required for this particle ID")
        elif self.particle_id in self.WITH_DELAY:
            if self.delay is None:
                raise ValueError("delay is required for this particle ID")
