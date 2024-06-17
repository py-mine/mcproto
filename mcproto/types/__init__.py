from __future__ import annotations

from mcproto.types.abc import MCType, Serializable
from mcproto.types.advancement import Advancement, AdvancementProgress, AdvancementDisplay, AdvancementCriterion
from mcproto.types.angle import Angle
from mcproto.types.bitset import Bitset, FixedBitset
from mcproto.types.block_entity import BlockEntity
from mcproto.types.chat import JSONTextComponent, TextComponent
from mcproto.types.entity import EntityMetadata
from mcproto.types.identifier import Identifier
from mcproto.types.map_icon import MapIcon, IconType
from mcproto.types.modifier import ModifierData, ModifierOperation
from mcproto.types.nbt import NBTag, CompoundNBT
from mcproto.types.particle_data import ParticleData
from mcproto.types.quaternion import Quaternion
from mcproto.types.recipe import (
    Recipe,
    ArmorDyeRecipe,
    BannerDuplicateRecipe,
    BlastingRecipe,
    BookCloningRecipe,
    ShulkerBoxColoringRecipe,
    CampfireRecipe,
    ShapedRecipe,
    DecoratedPotRecipe,
    FireworkRocketRecipe,
    MapCloningRecipe,
    MapExtendingRecipe,
    RepairItemRecipe,
    ShapelessRecipe,
    ShieldDecorationRecipe,
    SmokingRecipe,
    FireworkStarRecipe,
    FireworkStarFadeRecipe,
    Ingredient,
    SmeltingRecipe,
    SmithingTransformRecipe,
    SmithingTrimRecipe,
    TippedArrowRecipe,
    StoneCuttingRecipe,
    SuspiciousStewRecipe,
)
from mcproto.types.slot import Slot
from mcproto.types.registry_tag import RegistryTag
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
