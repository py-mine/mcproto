import struct

from mcproto.buffer import Buffer
from mcproto.types import ParticleData, Position, Slot, SlotData
from tests.mcproto.utils.test_serializable import gen_serializable_test

# WITH_BLOCK_STATE
gen_serializable_test(
    context=globals(),
    cls=ParticleData,
    fields=[
        ("particle_id", int),
        ("block_state", int),
    ],
    serialize_deserialize=[
        ((2, 2), b"\x02\x02"),  # minecraft:block
        ((3, 3), b"\x03\x03"),  # minecraft:block_marker
        ((27, 4), b"\x1b\x04"),  # minecraft:falling_dust
    ],
    validation_fail=[
        ((2, None), ValueError),  # Missing block state
    ],
    test_suffix="BlockState",
)

# WITH_RGB_SCALE
gen_serializable_test(
    context=globals(),
    cls=ParticleData,
    fields=[
        ("particle_id", int),
        ("red", float),
        ("green", float),
        ("blue", float),
    ],
    serialize_deserialize=[
        ((14, 0.5, 0.5, 0.625), b"\x0e" + struct.pack("!fff", 0.5, 0.5, 0.625)),  # minecraft:dust
    ],
    validation_fail=[
        ((14, None, 0.5, 0.75), ValueError),  # Missing red
        ((14, 1.0, None, 0.75), ValueError),  # Missing green
        ((14, 1.0, 0.5, None), ValueError),  # Missing blue
    ],
    test_suffix="RGBScale",
)

# WITH_RGB_TRANSITION
gen_serializable_test(
    context=globals(),
    cls=ParticleData,
    fields=[
        ("particle_id", int),
        ("from_red", float),
        ("from_green", float),
        ("from_blue", float),
        ("scale", float),
        ("to_red", float),
        ("to_green", float),
        ("to_blue", float),
    ],
    serialize_deserialize=[
        (
            (15, 1.0, 0.5, 0.75, 2.0, 0.5, 0.0, 0.625),
            b"\x0f" + struct.pack("!fffffff", 1.0, 0.5, 0.75, 2.0, 0.5, 0.0, 0.625),
        ),  # minecraft:dust_color_transition
    ],
    validation_fail=[
        ((15, None, 0.5, 0.75, 2.0, 0.5, 0.0, 0.625), ValueError),  # Missing from_red
        ((15, 1.0, None, 0.75, 2.0, 0.5, 0.0, 0.625), ValueError),  # Missing from_green
        ((15, 1.0, 0.5, None, 2.0, 0.5, 0.0, 0.625), ValueError),  # Missing from_blue
        ((15, 1.0, 0.5, 0.75, None, 0.5, 0.0, 0.625), ValueError),  # Missing scale
        ((15, 1.0, 0.5, 0.75, 2.0, None, 0.0, 0.625), ValueError),  # Missing to_red
        ((15, 1.0, 0.5, 0.75, 2.0, 0.5, None, 0.625), ValueError),  # Missing to_green
        ((15, 1.0, 0.5, 0.75, 2.0, 0.5, 0.0, None), ValueError),  # Missing to_blue
    ],
    test_suffix="RGBTransition",
)

# WITH_ROLL
gen_serializable_test(
    context=globals(),
    cls=ParticleData,
    fields=[
        ("particle_id", int),
        ("roll", float),
    ],
    serialize_deserialize=[
        ((33, 1.0), b"\x21" + struct.pack("!f", 1.0)),  # minecraft:sculk_charge
    ],
    validation_fail=[
        ((33, None), ValueError),  # Missing roll
    ],
    test_suffix="Roll",
)

# WITH_ITEM
gen_serializable_test(
    context=globals(),
    cls=ParticleData,
    fields=[
        ("particle_id", int),
        ("item", Slot),
    ],
    serialize_deserialize=[
        (
            (42, Slot(SlotData(23, 13))),
            b"\x2a" + Slot(SlotData(23, 13)).serialize(),
        ),
    ],
    validation_fail=[
        ((42, None), ValueError),  # Missing item
    ],
    test_suffix="Item",
)

# WITH_VIBRATION
gen_serializable_test(
    context=globals(),
    cls=ParticleData,
    fields=[
        ("particle_id", int),
        ("source_type", int),
        ("block_position", Position),
        ("entity_id", int),
        ("entity_eye_height", float),
        ("tick", int),
    ],
    serialize_deserialize=[
        (
            (43, 0, Position(0, 0, 0), None, None, 10),
            b"\x2b\x00" + Position(0, 0, 0).serialize() + b"\x0a",
        ),  # minecraft:vibration with block_position
        (
            (43, 1, None, 3, 1.0625, 10),
            b"\x2b\x01\x03" + struct.pack("!f", 1.0625) + b"\x0a",
        ),  # minecraft:vibration with entity_id and entity_eye_height
    ],
    validation_fail=[
        ((43, None, Position(0, 0, 0), None, None, 1), ValueError),  # Missing source_type
        ((43, 0, None, None, None, 1), ValueError),  # Missing block_position
        ((43, 1, None, None, None, 1), ValueError),  # Missing entity_id
        ((43, 1, None, 1, None, 1), ValueError),  # Missing entity_eye_height
        ((43, 1, None, 1, 1.8, None), ValueError),  # Missing tick
    ],
    test_suffix="Vibration",
)

# WITH_DELAY
gen_serializable_test(
    context=globals(),
    cls=ParticleData,
    fields=[
        ("particle_id", int),
        ("delay", int),
    ],
    serialize_deserialize=[
        ((96, 1), b"\x60\x01"),  # minecraft:shriek
    ],
    validation_fail=[
        ((96, None), ValueError),  # Missing delay
    ],
    test_suffix="Delay",
)


def test_particle_data_without_id():
    """Test ParticleData without particle_id during serialization."""
    particle_data = ParticleData(particle_id=4)
    assert particle_data.particle_id == 4
    buf = Buffer()
    particle_data.serialize_to(buf, with_id=False)
    assert bytes(buf) == b""
