from enum import IntEnum


class Direction(IntEnum):
    """Represents a direction in the world."""

    DOWN = 0
    """Towards the negative y-axis. (-y)"""
    UP = 1
    """Towards the positive y-axis. (+y)"""
    NORTH = 2
    """Towards the negative z-axis. (-z)"""
    SOUTH = 3
    """Towards the positive z-axis. (+z)"""
    WEST = 4
    """Towards the negative x-axis. (-x)"""
    EAST = 5
    """Towards the positive x-axis. (+x)"""


class Pose(IntEnum):
    """Represents a pose of an entity."""

    STANDING = 0
    """The entity is standing. (default)"""
    FALL_FLYING = 1
    """The entity is falling or flying."""
    SLEEPING = 2
    """The entity is sleeping. (e.g. in a bed)"""
    SWIMMING = 3
    """The entity is swimming."""
    SPIN_ATTACK = 4
    """The entity is performing a spin attack (with a riptide trident)."""
    SNEAKING = 5
    """The entity is sneaking."""
    LONG_JUMPING = 6
    """The entity is long jumping."""
    DYING = 7
    """The entity is dying"""
    CROAKING = 8
    """The entity is croaking. (a frog)"""
    USING_TONGUE = 9
    """The entity is using its tongue. (a frog)"""
    SITTING = 10
    """The entity is sitting. (e.g. a pet)"""
    ROARING = 11
    """The entity is roaring. (a warden)"""
    SNIFFING = 12
    """The entity is sniffing."""
    EMERGING = 13
    """The entity is emerging from the ground. (a warden)"""
    DIGGING = 14
    """The entity is digging."""


class SnifferState(IntEnum):
    """Represents the state of a sniffer."""

    IDLING = 0
    FEELING_HAPPY = 1
    SCENTING = 2
    SNIFFING = 3
    SEARCHING = 4
    DIGGING = 5
    RISING = 6


class DragonPhase(IntEnum):
    """Represents the state the ender dragon is in."""

    CIRCLING = 0
    """The dragon is circling around the portal."""
    STRAFING = 1
    """The dragon is strafing the player."""
    FLYING_TO_PORTAL = 2
    """The dragon is flying to the portal."""
    LANDING_ON_PORTAL = 3
    """The dragon is landing on the portal. (perching)"""
    TAKING_OFF_FROM_PORTAL = 4
    """The dragon is taking off from the portal."""
    LANDED_BREATH_ATTACK = 5
    """The dragon has landed and is performing a breath attack."""
    LANDED_LOOKING_FOR_PLAYER = 6
    """The dragon has landed and is looking for the player."""
    LANDED_ROAR = 7
    """The dragon has landed and is roaring."""
    CHARGING_PLAYER = 8
    """The dragon is charging at the player."""
    FLYING_TO_PORTAL_TO_DIE = 9
    """The dragon is flying to the portal to die."""
    HOVERING_NO_AI = 10
    """The dragon is hovering in place with no AI. (default)"""
