from __future__ import annotations

from mcproto.types.abc import MCType, Serializable
from mcproto.types.advancement import (
    Advancement,
    AdvancementCriterion,
    AdvancementDisplay,
    AdvancementFrame,
    AdvancementProgress,
)
from mcproto.types.angle import Angle
from mcproto.types.bitset import Bitset, FixedBitset
from mcproto.types.block_entity import BlockEntity
from mcproto.types.chat import JSONTextComponent, TextComponent
from mcproto.types.entity import EntityMetadata
from mcproto.types.identifier import Identifier
from mcproto.types.map_icon import IconType, MapIcon
from mcproto.types.modifier import ModifierData, ModifierOperation
from mcproto.types.nbt import CompoundNBT, NBTag
from mcproto.types.particle_data import ParticleData
from mcproto.types.quaternion import Quaternion
from mcproto.types.recipe import (
    ArmorDyeRecipe,
    BannerDuplicateRecipe,
    BlastingRecipe,
    BookCloningRecipe,
    CampfireRecipe,
    DecoratedPotRecipe,
    FireworkRocketRecipe,
    FireworkStarFadeRecipe,
    FireworkStarRecipe,
    Ingredient,
    MapCloningRecipe,
    MapExtendingRecipe,
    Recipe,
    RepairItemRecipe,
    ShapedRecipe,
    ShapelessRecipe,
    ShieldDecorationRecipe,
    ShulkerBoxColoringRecipe,
    SmeltingRecipe,
    SmithingTransformRecipe,
    SmithingTrimRecipe,
    SmokingRecipe,
    StoneCuttingRecipe,
    SuspiciousStewRecipe,
    TippedArrowRecipe,
)
from mcproto.types.registry_tag import RegistryTag
from mcproto.types.slot import Slot, SlotData
from mcproto.types.trade import Trade
from mcproto.types.uuid import UUID
from mcproto.types.vec3 import Position, Vec3

__all__ = [
    "MCType",
    "Serializable",
    "Angle",
    "Bitset",
    "FixedBitset",
    "JSONTextComponent",
    "TextComponent",
    "Identifier",
    "NBTag",
    "CompoundNBT",
    "Quaternion",
    "Slot",
    "SlotData",
    "RegistryTag",
    "UUID",
    "Position",
    "Vec3",
    "ParticleData",
    "BlockEntity",
    "MapIcon",
    "IconType",
    "Trade",
    "EntityMetadata",
    "Advancement",
    "AdvancementProgress",
    "AdvancementDisplay",
    "AdvancementCriterion",
    "AdvancementFrame",
    "ModifierData",
    "ModifierOperation",
    "Recipe",
    "ArmorDyeRecipe",
    "BannerDuplicateRecipe",
    "BlastingRecipe",
    "BookCloningRecipe",
    "ShulkerBoxColoringRecipe",
    "CampfireRecipe",
    "ShapedRecipe",
    "DecoratedPotRecipe",
    "FireworkRocketRecipe",
    "MapCloningRecipe",
    "MapExtendingRecipe",
    "RepairItemRecipe",
    "ShapelessRecipe",
    "ShieldDecorationRecipe",
    "SmokingRecipe",
    "FireworkStarRecipe",
    "FireworkStarFadeRecipe",
    "Ingredient",
    "SmeltingRecipe",
    "SmithingTransformRecipe",
    "SmithingTrimRecipe",
    "TippedArrowRecipe",
    "StoneCuttingRecipe",
    "SuspiciousStewRecipe",
]
