from __future__ import annotations

from abc import abstractmethod
from typing import ClassVar, final

from attrs import Attribute, define, field, validators
from typing_extensions import Self, override

from mcproto.buffer import Buffer
from mcproto.protocol import StructFormat
from mcproto.types.abc import MCType
from mcproto.types.identifier import Identifier
from mcproto.types.slot import Slot
from mcproto.utils.abc import RequiredParamsABCMixin


@final
@define
class Ingredient(MCType):
    """Represents an item in a :class:`Recipe`.

    :param count: The count of the item.
    :type count: int
    :param items: The items that can be used to craft the item.
    :type items: list[:class:`~mcproto.types.slot.Slot`]

    .. note:: Each item in the list has to have a count of 1.
    """

    @staticmethod
    def check_quantity(instance: Ingredient, attribute: Attribute[set[Slot]], value: set[Slot]) -> None:
        """Check that each ingredient is valid."""
        if any(item.data is None or item.data.num != 1 for item in value):
            raise ValueError("Each item in the list has to have a count of 1.")

    count: int = field(validator=validators.ge(1))
    items: set[Slot] = field(validator=check_quantity.__get__(object))

    @override
    def serialize_to(self, buf: Buffer) -> None:
        buf.write_varint(self.count)
        buf.write_varint(len(self.items))
        for item in self.items:
            item.serialize_to(buf)

    @override
    @classmethod
    def deserialize(cls, buf: Buffer) -> Self:
        count = buf.read_varint()
        items = {Slot.deserialize(buf) for _ in range(buf.read_varint())}
        return cls(count=count, items=items)


@define
class Recipe(MCType, RequiredParamsABCMixin):
    """Represents a recipe in the :class:`~mcproto.packets.play.UpdateRecipes` packet.

    <https://wiki.vg/Protocol#Update_Recipes>

    :param recipe_id: The ID of the recipe.
    :type recipe_id: :class:`~mcproto.types.identifier.Identifier`
    """

    _REQUIRED_CLASS_VARS = ("recipe_type",)

    recipe_id: Identifier
    recipe_type: ClassVar[int] = NotImplemented
    recipe_type_identifier: ClassVar[Identifier] = NotImplemented  # unused

    @override
    @abstractmethod
    def serialize_to(self, buf: Buffer) -> None:
        self.recipe_id.serialize_to(buf)
        buf.write_varint(self.recipe_type)

    @classmethod
    @abstractmethod
    def _deserialize(cls, buf: Buffer, recipe_id: Identifier) -> Self: ...

    @override
    @classmethod
    def deserialize(cls, buf: Buffer) -> Recipe:
        recipe_id = Identifier.deserialize(buf)
        recipe_type = buf.read_varint()
        return ID_ASSOCIATION[recipe_type]._deserialize(buf, recipe_id)


@final
@define
class ShapedRecipe(Recipe):
    """Represents a shaped recipe in the :class:`~mcproto.packets.play.UpdateRecipes` packet.

    Shaped crafting recipe. All items must be present in the same pattern (which may be flipped horizontally or
    translated).

    :param group: Used to group similar recipes together in the recipe book. Tag is present in recipe JSON.
    :type group: str
    :param category: The category of the recipe. Building = 0, Redstone = 1, Equipment = 2, Misc = 3
    :type category: int
    :param width: The width of the recipe.
    :type width: int
    :param height: The height of the recipe.
    :type height: int
    :param ingredients: The ingredients of the recipe.
    :type ingredients: list[:class:`Ingredient`]
    :param result: The result of the recipe.
    :type result: :class:`~mcproto.types.slot.Slot`
    :param show_toast: Whether to show a toast notification when the recipe is unlocked.
    :type show_toast: bool
    """

    recipe_type: ClassVar[int] = 0
    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "crafting_shaped")

    group: str
    category: int
    width: int
    height: int
    ingredients: list[Ingredient]
    result: Slot
    show_toast: bool

    @override
    def serialize_to(self, buf: Buffer) -> None:
        super().serialize_to(buf)
        buf.write_utf(self.group)
        buf.write_varint(self.category)
        buf.write_varint(self.width)
        buf.write_varint(self.height)
        buf.write_varint(len(self.ingredients))
        for ingredient in self.ingredients:
            ingredient.serialize_to(buf)
        self.result.serialize_to(buf)
        buf.write_value(StructFormat.BOOL, self.show_toast)

    @override
    @classmethod
    def _deserialize(cls, buf: Buffer, recipe_id: Identifier) -> Self:
        group = buf.read_utf()
        category = buf.read_varint()
        width = buf.read_varint()
        height = buf.read_varint()
        ingredients = [Ingredient.deserialize(buf) for _ in range(buf.read_varint())]
        result = Slot.deserialize(buf)
        show_toast = buf.read_value(StructFormat.BOOL)
        return cls(
            recipe_id=recipe_id,
            group=group,
            category=category,
            width=width,
            height=height,
            ingredients=ingredients,
            result=result,
            show_toast=show_toast,
        )


@final
@define
class ShapelessRecipe(Recipe):
    """Represents a shapeless recipe in the :class:`~mcproto.packets.play.UpdateRecipes` packet.

    Shapeless crafting recipe. Items can be anywhere in the grid.

    :param group: Used to group similar recipes together in the recipe book. Tag is present in recipe JSON.
    :type group: str
    :param category: The category of the recipe. Building = 0, Redstone = 1, Equipment = 2, Misc = 3
    :type category: int
    :param ingredients: The ingredients of the recipe.
    :type ingredients: list[:class:`Ingredient`]
    :param result: The result of the recipe.
    :type result: :class:`~mcproto.types.slot.Slot`
    """

    recipe_type: ClassVar[int] = 1
    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "crafting_shapeless")

    group: str
    category: int
    ingredients: list[Ingredient]
    result: Slot

    @override
    def serialize_to(self, buf: Buffer) -> None:
        super().serialize_to(buf)
        buf.write_utf(self.group)
        buf.write_varint(self.category)
        buf.write_varint(len(self.ingredients))
        for ingredient in self.ingredients:
            ingredient.serialize_to(buf)
        self.result.serialize_to(buf)

    @override
    @classmethod
    def _deserialize(cls, buf: Buffer, recipe_id: Identifier) -> Self:
        group = buf.read_utf()
        category = buf.read_varint()
        ingredients = [Ingredient.deserialize(buf) for _ in range(buf.read_varint())]
        result = Slot.deserialize(buf)
        return cls(
            recipe_id=recipe_id,
            group=group,
            category=category,
            ingredients=ingredients,
            result=result,
        )


@define
class _SpecialRecipe(Recipe):
    """Represents a recipe containing only the category.

    :param category: The category of the recipe. Building = 0, Redstone = 1, Equipment = 2, Misc = 3
    :type category: int
    """

    category: int

    @override
    def serialize_to(self, buf: Buffer) -> None:
        super().serialize_to(buf)
        buf.write_varint(self.category)

    @override
    @classmethod
    def _deserialize(cls, buf: Buffer, recipe_id: Identifier) -> Self:
        category = buf.read_varint()
        return cls(recipe_id=recipe_id, category=category)


@final
class ArmorDyeRecipe(_SpecialRecipe):
    """Recipe for dying leather armor."""

    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "crafting_special_armordye")
    recipe_type: ClassVar[int] = 2

    __slots__ = ()


@final
class BookCloningRecipe(_SpecialRecipe):
    """Recipe for copying contents of written books."""

    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "crafting_special_bookcloning")
    recipe_type: ClassVar[int] = 3

    __slots__ = ()


@final
class MapCloningRecipe(_SpecialRecipe):
    """Recipe for copying maps."""

    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "crafting_special_mapcloning")
    recipe_type: ClassVar[int] = 4

    __slots__ = ()


@final
class MapExtendingRecipe(_SpecialRecipe):
    """Recipe for adding paper to maps."""

    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "crafting_special_mapextending")
    recipe_type: ClassVar[int] = 5

    __slots__ = ()


@final
class FireworkRocketRecipe(_SpecialRecipe):
    """Recipe for making firework rockets."""

    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "crafting_special_firework_rocket")
    recipe_type: ClassVar[int] = 6

    __slots__ = ()


@final
class FireworkStarRecipe(_SpecialRecipe):
    """Recipe for making firework stars."""

    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "crafting_special_firework_star")
    recipe_type: ClassVar[int] = 7

    __slots__ = ()


@final
class FireworkStarFadeRecipe(_SpecialRecipe):
    """Recipe for making firework stars fade between multiple colors."""

    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "crafting_special_firework_star_fade")
    recipe_type: ClassVar[int] = 8

    __slots__ = ()


@final
class TippedArrowRecipe(_SpecialRecipe):
    """Recipe for crafting tipped arrows."""

    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "crafting_special_tippedarrow")
    recipe_type: ClassVar[int] = 9

    __slots__ = ()


@final
class BannerDuplicateRecipe(_SpecialRecipe):
    """Recipe for copying banner patterns."""

    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "crafting_special_bannerduplicate")
    recipe_type: ClassVar[int] = 10

    __slots__ = ()


@final
class ShieldDecorationRecipe(_SpecialRecipe):
    """Recipe for applying a banner's pattern to a shield."""

    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "crafting_special_shielddecoration")
    recipe_type: ClassVar[int] = 11

    __slots__ = ()


@final
class ShulkerBoxColoringRecipe(_SpecialRecipe):
    """Recipe for recoloring a shulker box."""

    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "crafting_special_shulkerboxcoloring")
    recipe_type: ClassVar[int] = 12

    __slots__ = ()


@final
class SuspiciousStewRecipe(_SpecialRecipe):
    """Recipe for crafting suspicious stews."""

    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "crafting_special_suspiciousstew")
    recipe_type: ClassVar[int] = 13

    __slots__ = ()


@final
class RepairItemRecipe(_SpecialRecipe):
    """Recipe for repairing items via crafting."""

    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "crafting_special_repairitem")
    recipe_type: ClassVar[int] = 14

    __slots__ = ()


@final
class DecoratedPotRecipe(_SpecialRecipe):
    """Recipe for crafting decorated pots."""

    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "crafting_decorated_pot")
    recipe_type: ClassVar[int] = 22

    __slots__ = ()


@define
class SmeltingRecipe(Recipe):
    """Smelting recipe.

    :param group: Used to group similar recipes together in the recipe book. Tag is present in recipe JSON.
    :type group: str
    :param category: The category of the recipe. Building = 0, Redstone = 1, Equipment = 2, Misc = 3
    :type category: int
    :param ingredient: The ingredient of the recipe.
    :type ingredient: :class:`Ingredient`
    :param result: The result of the recipe.
    :type result: :class:`~mcproto.types.slot.Slot`
    :param experience: The experience given when the recipe is completed.
    :type experience: float
    :param cooking_time: The time it takes to complete the recipe.
    :type cooking_time: int
    """

    recipe_type: ClassVar[int] = 15
    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "smelting")

    group: str
    category: int
    ingredient: Ingredient
    result: Slot
    experience: float
    cooking_time: int

    @override
    def serialize_to(self, buf: Buffer) -> None:
        super().serialize_to(buf)
        buf.write_utf(self.group)
        buf.write_varint(self.category)
        self.ingredient.serialize_to(buf)
        self.result.serialize_to(buf)
        buf.write_value(StructFormat.FLOAT, self.experience)
        buf.write_varint(self.cooking_time)

    @override
    @classmethod
    def _deserialize(cls, buf: Buffer, recipe_id: Identifier) -> Self:
        group = buf.read_utf()
        category = buf.read_varint()
        ingredient = Ingredient.deserialize(buf)
        result = Slot.deserialize(buf)
        experience = buf.read_value(StructFormat.FLOAT)
        cooking_time = buf.read_varint()
        return cls(
            recipe_id=recipe_id,
            group=group,
            category=category,
            ingredient=ingredient,
            result=result,
            experience=experience,
            cooking_time=cooking_time,
        )


@final
class BlastingRecipe(SmeltingRecipe):
    """Blast furnace recipe."""

    recipe_type: ClassVar[int] = 16
    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "blasting")

    __slots__ = ()


@final
class SmokingRecipe(SmeltingRecipe):
    """Smoker recipe."""

    recipe_type: ClassVar[int] = 17
    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "smoking")

    __slots__ = ()


@final
class CampfireRecipe(SmeltingRecipe):
    """Campfire recipe."""

    recipe_type: ClassVar[int] = 18
    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "campfire_cooking")

    __slots__ = ()


@final
@define
class StoneCuttingRecipe(Recipe):
    """Stone cutting recipe.

    :param group: Used to group similar recipes together in the recipe book. Tag is present in recipe JSON.
    :type group: str
    :param ingredient: The ingredient of the recipe.
    :type ingredient: :class:`Ingredient`
    :param result: The result of the recipe.
    :type result: :class:`~mcproto.types.slot.Slot`
    """

    recipe_type: ClassVar[int] = 19
    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "stonecutting")

    group: str
    ingredient: Ingredient
    result: Slot

    @override
    def serialize_to(self, buf: Buffer) -> None:
        super().serialize_to(buf)
        buf.write_utf(self.group)
        self.ingredient.serialize_to(buf)
        self.result.serialize_to(buf)

    @override
    @classmethod
    def _deserialize(cls, buf: Buffer, recipe_id: Identifier) -> Self:
        group = buf.read_utf()
        ingredient = Ingredient.deserialize(buf)
        result = Slot.deserialize(buf)
        return cls(
            recipe_id=recipe_id,
            group=group,
            ingredient=ingredient,
            result=result,
        )


@define
class SmithingTrimRecipe(Recipe):
    """Smithing transform recipe.

    :param template: The smithing template.
    :type template: :class:`Ingredient`
    :param base: The base item of the recipe.
    :type base: :class:`Ingredient`
    :param addition: The additional ingredient of the recipe.
    :type addition: :class:`Ingredient`
    """

    recipe_type: ClassVar[int] = 21
    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "smithing_trim")

    template: Ingredient
    base: Ingredient
    addition: Ingredient

    @override
    def serialize_to(self, buf: Buffer) -> None:
        super().serialize_to(buf)
        self.template.serialize_to(buf)
        self.base.serialize_to(buf)
        self.addition.serialize_to(buf)

    @override
    @classmethod
    def _deserialize(cls, buf: Buffer, recipe_id: Identifier) -> Self:
        template = Ingredient.deserialize(buf)
        base = Ingredient.deserialize(buf)
        addition = Ingredient.deserialize(buf)
        return cls(
            recipe_id=recipe_id,
            template=template,
            base=base,
            addition=addition,
        )


@final
@define
class SmithingTransformRecipe(SmithingTrimRecipe):
    """Recipe for smithing netherite gear.

    :param template: The smithing template.
    :type template: :class:`Ingredient`
    :param base: The base item of the recipe.
    :type base: :class:`Ingredient`
    :param addition: The additional ingredient of the recipe.
    :type addition: :class:`Ingredient`
    :param result: The result of the recipe.
    :type result: :class:`~mcproto.types.slot.Slot`
    """

    recipe_type: ClassVar[int] = 20
    recipe_type_identifier: ClassVar[Identifier] = Identifier("minecraft", "smithing_transform")

    result: Slot

    @override
    def serialize_to(self, buf: Buffer) -> None:
        super().serialize_to(buf)
        self.result.serialize_to(buf)

    @override
    @classmethod
    def _deserialize(cls, buf: Buffer, recipe_id: Identifier) -> Self:
        template = Ingredient.deserialize(buf)
        base = Ingredient.deserialize(buf)
        addition = Ingredient.deserialize(buf)
        result = Slot.deserialize(buf)
        return cls(
            recipe_id=recipe_id,
            template=template,
            base=base,
            addition=addition,
            result=result,
        )


ID_ASSOCIATION: dict[int, type[Recipe]] = {
    0: ShapedRecipe,
    1: ShapelessRecipe,
    2: ArmorDyeRecipe,
    3: BookCloningRecipe,
    4: MapCloningRecipe,
    5: MapExtendingRecipe,
    6: FireworkRocketRecipe,
    7: FireworkStarRecipe,
    8: FireworkStarFadeRecipe,
    9: TippedArrowRecipe,
    10: BannerDuplicateRecipe,
    11: ShieldDecorationRecipe,
    12: ShulkerBoxColoringRecipe,
    13: SuspiciousStewRecipe,
    14: RepairItemRecipe,
    15: SmeltingRecipe,
    16: BlastingRecipe,
    17: SmokingRecipe,
    18: CampfireRecipe,
    19: StoneCuttingRecipe,
    20: SmithingTransformRecipe,
    21: SmithingTrimRecipe,
    22: DecoratedPotRecipe,
}
