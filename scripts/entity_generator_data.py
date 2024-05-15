from __future__ import annotations

from typing import Dict, List, Union

# Define a type for a single field in the entity data
Field = Dict[str, Union[type, str, int, bool, float, List[Dict[str, Union[type, str, int]]]]]

# Define a type for the entire entity data dictionary
EntityData = Dict[str, Union[str, List[Field]]]

ENTITY_DATA: list[EntityData] = [
    {  # Entity
        "name": "Entity",
        "description": "Base for all Entity classes.",
        "base": "EntityMetadata",
        "fields": [
            {
                "type": "Byte",
                "name": "entity_flags",
                "available": False,
                "default": 0,
                "input": int,
                "proxy": [
                    {
                        "type": "Masked",
                        "name": "is_on_fire",
                        "input": bool,
                        "description": "Whether the entity is on fire.",
                        "mask": 0x01,
                    },
                    {
                        "type": "Masked",
                        "name": "is_crouching",
                        "input": bool,
                        "description": "Whether the entity is crouching.",
                        "mask": 0x02,
                    },
                    {
                        "type": "Masked",
                        "name": "is_riding",
                        "input": bool,
                        "description": "[UNUSED] Whether the entity is riding something.",
                        "mask": 0x04,
                    },
                    {
                        "type": "Masked",
                        "name": "is_sprinting",
                        "input": bool,
                        "description": "Whether the entity is sprinting.",
                        "mask": 0x08,
                    },
                    {
                        "type": "Masked",
                        "name": "is_swimming",
                        "input": bool,
                        "description": "Whether the entity is swimming.",
                        "mask": 0x10,
                    },
                    {
                        "type": "Masked",
                        "name": "is_invisible",
                        "input": bool,
                        "description": "Whether the entity is invisible.",
                        "mask": 0x20,
                    },
                    {
                        "type": "Masked",
                        "name": "is_glowing",
                        "input": bool,
                        "description": "Whether the entity has a glowing effect.",
                        "mask": 0x40,
                    },
                    {
                        "type": "Masked",
                        "name": "is_flying",
                        "input": bool,
                        "description": "Whether the entity is flying.",
                        "mask": 0x80,
                    },
                ],
                "description": "Flags for the entity.",
            },
            {
                "type": "VarInt",
                "name": "air",
                "default": 300,
                "input": int,
                "description": "The amount of air the entity has.",
            },
            {
                "type": "String",
                "name": "custom_name",
                "default": "",
                "input": str,
                "description": "The custom name of the entity.",
            },
            {
                "type": "Boolean",
                "name": "is_custom_name_visible",
                "default": False,
                "input": bool,
                "description": "Whether the custom name is visible.",
            },
            {
                "type": "Boolean",
                "name": "is_silent",
                "default": False,
                "input": bool,
                "description": "Whether the entity is silent.",
            },
            {
                "type": "Boolean",
                "name": "no_gravity",
                "default": False,
                "input": bool,
                "description": "Whether the entity should ignore gravity.",
            },
            {
                "type": "Pose",
                "name": "pose",
                "default": "STANDING",
                "input": "Pose",
                "enum": True,
                "description": "The pose of the entity. Can be one of the following: STANDING, FALL_FLYING,\n"
                "    SLEEPING, SWIMMING, SPIN_ATTACK, SNEAKING, DYING.",
            },
            {
                "type": "VarInt",
                "name": "ticks_frozen",
                "default": 0,
                "input": int,
                "description": "The amount of ticks the entity has been in powdered snow for.",
            },
        ],
    },  # End of Entity
    {  # Interaction
        "name": "Interaction",
        "description": "Entity that can be interacted with.",
        "base": "Entity",
        "fields": [
            {
                "type": "Float",
                "name": "width",
                "default": 1.0,
                "input": float,
                "description": "The width of the entity.",
            },
            {
                "type": "Float",
                "name": "height",
                "default": 1.0,
                "input": float,
                "description": "The height of the entity.",
            },
            {
                "type": "Boolean",
                "name": "responsive",
                "default": False,
                "input": bool,
                "description": "Whether the entity can be interacted with/attached",
            },
        ],
    },  # End of Interaction
    {  # Display
        "name": "Display",
        "description": "Entity that are used to render something on the client.\n\n"
        "    https://minecraft.wiki/w/Display",
        "base": "Entity",
        "fields": [
            {
                "type": "VarInt",
                "name": "interpolation_delay",
                "default": 0,
                "input": int,
                "description": "Delay before starting interpolation.\n    If 0, interpolation starts immediately."
                "(doesn't exist in newest snapshot)",
            },
            {
                "type": "VarInt",
                "name": "interpolation_translation_duration",
                "default": 0,
                "input": int,
                "description": "Transformation interpolation duration.",
            },
            {
                "type": "VarInt",
                "name": "interpolation_rotation_duration",
                "default": 0,
                "input": int,
                "description": "Rotation interpolation duration.",
            },
            {
                "type": "Vector3",
                "name": "translation",
                "default": "(0.0, 0.0, 0.0)",
                "input": "tuple[float, float, float]",
                "description": "Translation vector",
            },
            {
                "type": "Vector3",
                "name": "scale",
                "default": "(1.0, 1.0, 1.0)",
                "input": "tuple[float, float, float]",
                "description": "Scaling vector",
            },
            {
                "type": "Quaternion",
                "name": "rotation_left",
                "default": "(0.0, 0.0, 0.0, 1.0)",
                "input": "tuple[float, float, float, float]",
                "description": "See :attr:`rotation_right`",
            },
            {
                "type": "Quaternion",
                "name": "rotation_right",
                "default": "(0.0, 0.0, 0.0, 1.0)",
                "input": "tuple[float, float, float, float]",
                "description": "Initial rotation. This tag corresponds to the right-singular vector matrix after the\n"
                "    matrix singular value decomposition. ",
            },
            {
                "type": "Byte",
                "name": "billboard_constraint",
                "default": 0,
                "input": int,
                "description": "Billboard Constraints (0 = FIXED, 1 = VERTICAL, 2 = HORIZONTAL, 3 = CENTER)\n"
                "    Controls if this entity should pivot to face player when rendered.",
            },
            {  # Might need a proxy later for the components
                "type": "VarInt",
                "name": "brightness_override",
                "default": -1,
                "input": int,
                "description": "Brightness override (blockLight << 4 | skyLight << 20). By default the brightness\n"
                "    value is calculated from the light level of the block the entity is in.",
            },
            {
                "type": "Float",
                "name": "view_range",
                "default": 1.0,
                "input": float,
                "description": "View range",
            },
            {
                "type": "Float",
                "name": "shadow_radius",
                "default": 0.0,
                "input": float,
                "description": "Shadow radius. Value is treated as 64 when higher than 64.\n"
                "    If less than or equal to 0, the entity has no shadow. Interpolated",
            },
            {
                "type": "Float",
                "name": "shadow_strength",
                "default": 0.0,
                "input": float,
                "description": "Shadow strength. Interpolated",
            },
            {
                "type": "Float",
                "name": "width",
                "default": 0.0,
                "input": float,
                "description": "The maximum width of the entity. Rendering culling bounding box spans horizontally\n"
                "    `width/2` from entity position, and the part beyond will be culled. If set to 0, no culling on\n"
                "    both vertical and horizontal directions.",
            },
            {
                "type": "Float",
                "name": "height",
                "default": 0.0,
                "input": float,
                "description": "The maximum height of the entity. Rendering culling bounding box spans vertically\n"
                "    `y` to `y+height`, and the part beyond will be culled. If set to 0, no culling on both\n"
                "    vertical and horizontal directions.",
            },
            {
                "type": "VarInt",
                "name": "glow_color_override",
                "default": 0,
                "input": int,
                "description": "Overrides the glow border color. If 0, uses the color of the team that the display\n"
                "    entity is in.",
            },
        ],
    },  # End of Display
    {  # Block Display
        "name": "BlockDisplay",
        "description": "Entity that are used to render a block on the client as a Display entity.\n\n"
        "    https://minecraft.wiki/w/Display#Block_Displays",
        "base": "Display",
        "fields": [
            {
                "type": "BlockState",
                "name": "block",
                "default": 0,  # minecraft:air
                "input": int,
                "description": "The block state to display. Default is air.",
            },
        ],
    },  # End of Block Display
    {  # Item Display
        "name": "ItemDisplay",
        "description": "Entity that are used to render an item on the client as a Display entity.\n\n"
        "    https://minecraft.wiki/w/Display#Item_Displays",
        "base": "Display",
        "fields": [
            {
                "type": "Slot",
                "name": "item",
                "default": "Slot(present=False)",  # empty
                "input": "Slot",
                "description": "The item to display. Default is an empty slot.",
            },
            {
                "type": "Byte",
                "name": "display_type",
                "default": 0,
                "input": int,
                "description": "Display type: (NONE, THIRD_PERSON_LEFT_HAND, THIRD_PERSON_RIGHT_HAND,\n"
                "    FIRST_PERSON_LEFT_HAND, FIRST_PERSON_RIGHT_HAND, HEAD, GUI, GROUND, FIXED).",
            },
        ],
    },  # End of Item Display
    {  # Text Display
        "name": "TextDisplay",
        "description": "Entity that are used to render text on the client as a Display entity.\n\n"
        "    https://minecraft.wiki/w/Display#Text_Displays",
        "base": "Display",
        "fields": [
            {
                "type": "TextComponent",
                "name": "text",
                "default": 'TextComponent("")',  # empty
                "input": "TextComponent",
                "description": "The text to display. Default is an empty text component.",
            },
            {
                "type": "VarInt",
                "name": "line_width",
                "default": 200,
                "input": int,
                "description": ": Maximum line width used to split lines (note: new line can also\n"
                "    be added with \\\\n characters).",
            },
            {
                "type": "VarInt",
                "name": "background_color",
                "default": 1073741824,
                "input": int,
                "description": "Background color of the text. Default is 0x40000000.",
            },
            {
                "name": "display_flags",
                "type": "Byte",
                "default": 0,
                "input": int,
                "available": False,
                "proxy": [
                    {
                        "type": "Masked",
                        "name": "has_shadow",
                        "input": bool,
                        "description": "Whether the text is displayed with shadow.",
                        "mask": 0x01,
                    },
                    {
                        "type": "Masked",
                        "name": "is_see_through",
                        "input": bool,
                        "description": "Whether the text is displayed as see-through.",
                        "mask": 0x02,
                    },
                    {
                        "type": "Masked",
                        "name": "use_default_background",
                        "input": bool,
                        "description": "Whether to use the default background color for the text\n    display.",
                        "mask": 0x04,
                    },
                    {
                        "type": "Masked",
                        "name": "align_left",
                        "input": bool,
                        "description": "Whether the text is aligned to the left.\n"
                        "    Has priority over right (see also :attr:`align_right`)",
                        "mask": 0x08,
                    },
                    {
                        "type": "Masked",
                        "name": "align_right",
                        "input": bool,
                        "description": "Whether the text is aligned to the right.\n"
                        "    Set both to false for center alignment.",
                        "mask": 0x10,
                    },
                ],
                "description": "Flags for the text display.",
            },
        ],
    },
    {  # Thrown Item Projectile
        "name": "ThrownItemProjectile",
        "description": "Entity that represents a thrown item projectile.",
        "base": "Entity",
        "fields": [
            {
                "type": "Slot",
                "name": "item",
                "default": "Slot(present=False)",  # empty
                "input": "Slot",
                "description": "The item that the projectile represents",
            }
        ],
    },
    {  # Thrown Egg
        "name": "ThrownEgg",
        "description": "Entity that represents a thrown egg projectile.",
        "base": "ThrownItemProjectile",
        "fields": [
            {
                "type": "Slot",
                "name": "item",
                # Registries not implemented yet
                "default": "Slot(present=True, item_id=NotImplemented, item_count=1)",
                "input": "Slot",
            }
        ],
    },
    {  # Thrown Ender Pearl
        "name": "ThrownEnderPearl",
        "description": "Entity that represents a thrown ender pearl projectile.",
        "base": "ThrownItemProjectile",
        "fields": [
            {
                "type": "Slot",
                "name": "item",
                "default": "Slot(present=True, item_id=NotImplemented, item_count=1)",  # same
                "input": "Slot",
            }
        ],
    },
    {  # Thrown Experience Bottle
        "name": "ThrownExperienceBottle",
        "description": "Entity that represents a thrown experience bottle projectile.",
        "base": "ThrownItemProjectile",
        "fields": [
            {
                "type": "Slot",
                "name": "item",
                "default": "Slot(present=True, item_id=NotImplemented, item_count=1)",  # same
                "input": "Slot",
            }
        ],
    },
    {  # Thrown Potion
        "name": "ThrownPotion",
        "description": "Entity that represents a thrown potion projectile.",
        "base": "ThrownItemProjectile",
        "fields": [
            {
                "type": "Slot",
                "name": "item",
                "default": "Slot(present=True, item_id=NotImplemented, item_count=1)",  # same
                "input": "Slot",
            }
        ],
    },
    {  # Thrown Snowball
        "name": "ThrownSnowball",
        "description": "Entity that represents a thrown snowball projectile.",
        "base": "ThrownItemProjectile",
        "fields": [
            {
                "type": "Slot",
                "name": "item",
                "default": "Slot(present=True, item_id=NotImplemented, item_count=1)",  # same
                "input": "Slot",
            }
        ],
    },
    {  # Eye of Ender
        "name": "EyeOfEnder",
        "description": "Entity that represents an eye of ender.",
        "base": "Entity",
        "fields": [
            {
                "type": "Slot",
                "name": "item",
                "default": "Slot(present=False)",  # behaves like a minecraft:ender_eye
                "input": "Slot",
                "description": "The item that the entity represents (usually an ender eye)",
            }
        ],
    },
    {  # Falling Block
        "name": "FallingBlock",
        "description": "Entity that represents a falling block.",
        "base": "Entity",
        "fields": [
            {
                "type": "Position",
                "name": "position",
                "default": "(0, 0, 0)",
                "input": "tuple[int, int, int]",
                "description": "The spawn position of the falling block",
            },
        ],
    },
    {
        "name": "AreaEffectCloud",
        "description": "Entity that represents an area effect cloud.",
        "base": "Entity",
        "fields": [
            {
                "type": "Float",
                "name": "radius",
                "default": 0.5,
                "input": float,
                "description": "The radius of the area effect cloud.",
            },
            {
                "type": "VarInt",
                "name": "color",
                "default": 0,
                "input": int,
                "description": "Color of the cloud's particle effect. Only applicable for mob spell particles.",
            },
            {
                "type": "Boolean",
                "name": "single_point_effect",
                "default": False,
                "input": bool,
                "description": "Whether to ignore the radius and show the effect as a single point, not an area.",
            },
            {
                "type": "Particle",
                "name": "effect",
                "default": "(0, None)",
                "input": "tuple[int, Any]",
                "description": "The particle effect of the area effect cloud.",
            },
        ],
    },
    {  # Fishing Hook
        "name": "FishingHook",
        "description": "Entity that represents a fishing hook.",
        "base": "Entity",
        "fields": [
            {
                "type": "VarInt",
                "name": "hooked_entity_id",
                "default": 0,
                "input": int,
                "description": "The ID of the hooked entity plus one, or 0 if there is no hooked entity.",
            },
            {
                "type": "Boolean",
                "name": "is_catchable",
                "default": False,
                "input": bool,
                "description": "Whether the fishing hook is catchable.",
            },
        ],
    },
    {  # Abstract Arrow
        "name": "AbstractArrow",
        "description": "Entity that represents an abstract arrow.",
        "base": "Entity",
        "fields": [
            {
                "type": "Byte",
                "name": "arrow_flags",
                "default": 0,
                "input": int,
                "available": False,
                "proxy": [
                    {
                        "type": "Masked",
                        "name": "is_critical",
                        "input": bool,
                        "description": "Whether the arrow is critical.",
                        "mask": 0x01,
                    },
                    {
                        "type": "Masked",
                        "name": "is_noclip",
                        "input": bool,
                        "description": "Whether the arrow is noclip (used by loyalty tridents when\n returning).",
                        "mask": 0x02,
                    },
                ],
                "description": "Flags for the arrow.",
            },
            {
                "type": "Byte",
                "name": "piercing_level",
                "default": 0,
                "input": int,
                "description": "The piercing level of the arrow.",
            },
        ],
    },
    {  # Arrow
        "name": "Arrow",
        "description": "Entity that represents an arrow.",
        "base": "AbstractArrow",
        "fields": [
            {
                "type": "VarInt",
                "name": "color",
                "default": -1,
                "input": int,
                "description": "Color of the arrow's particles. Set to -1 for no particles.",
            }
        ],
    },
    {  # Spectral Arrow
        "name": "SpectralArrow",
        "description": "Entity that represents a spectral arrow.",
        "base": "AbstractArrow",
        "fields": [],
    },
    {  # Thrown Trident
        "name": "ThrownTrident",
        "description": "Entity that represents a thrown trident.",
        "base": "AbstractArrow",
        "fields": [
            {
                "type": "VarInt",
                "name": "loyalty_level",
                "default": 0,
                "input": int,
                "description": "The loyalty level of the thrown trident (enchantment).",
            },
            {
                "type": "Boolean",
                "name": "has_enchantment_glint",
                "default": False,
                "input": bool,
                "description": "Whether the thrown trident has an enchantment glint.",
            },
        ],
    },
    {
        "name": "AbstractVehicle",
        "description": "Entity that represents an abstract vehicle.",
        "base": "Entity",
        "fields": [
            {
                "type": "VarInt",
                "name": "shaking_power",
                "default": 0,
                "input": int,
                "description": "The shaking power of the vehicle.",
            },
            {
                "type": "VarInt",
                "name": "shaking_direction",
                "default": 1,
                "input": int,
                "description": "The shaking direction of the vehicle.",
            },
            {
                "type": "Float",
                "name": "shaking_multiplier",
                "default": 0.0,
                "input": float,
                "description": "The shaking multiplier of the vehicle.",
            },
        ],
    },
    {
        "name": "Boat",
        "description": "Entity that represents a boat.",
        "base": "AbstractVehicle",
        "fields": [
            {
                "type": "VarInt",
                "name": "boat_type",
                "default": 0,
                "input": int,
                "description": "The type of the boat. (0 = oak, 1 = spruce, 2 = birch, 3 = jungle,\n"
                "    4 = acacia, 5 = dark oak)",
            },
            {
                "type": "Boolean",
                "name": "is_left_paddle_turning",
                "default": False,
                "input": bool,
                "description": "Whether the left paddle of the boat is turning.",
            },
            {
                "type": "Boolean",
                "name": "is_right_paddle_turning",
                "default": False,
                "input": bool,
                "description": "Whether the right paddle of the boat is turning.",
            },
            {
                "type": "VarInt",
                "name": "splash_timer",
                "default": 0,
                "input": int,
                "description": "The splash timer of the boat.",
            },
        ],
    },
    {
        "name": "ChestBoat",
        "description": "Entity that represents a chest boat.",
        "base": "Boat",
        "fields": [],
    },
    {
        "name": "AbstractMinecart",
        "description": "Entity that represents an abstract minecart.",
        "base": "AbstractVehicle",
        "fields": [
            {
                "type": "VarInt",
                "name": "custom_block_id_and_damage",
                "default": 0,
                "input": int,
                "description": "The custom block ID and damage of the minecart.",
            },
            {
                "type": "VarInt",
                "name": "custom_block_y_position",
                "default": 6,
                "input": int,
                "description": "The custom block Y position (in 16ths of a block) of the minecart.",
            },
            {
                "type": "Boolean",
                "name": "show_custom_block",
                "default": False,
                "input": bool,
                "description": "Whether to show the custom block of the minecart.",
            },
        ],
    },
    {
        "name": "Minecart",
        "description": "Entity that represents a minecart.",
        "base": "AbstractMinecart",
        "fields": [],
    },
    {
        "name": "AbstractMinecartContainer",
        "description": "Entity that represents an abstract minecart container.",
        "base": "AbstractMinecart",
        "fields": [],
    },
    {
        "name": "MinecartHopper",
        "description": "Entity that represents a minecart hopper.",
        "base": "AbstractMinecartContainer",
        "fields": [],
    },
    {
        "name": "MinecartChest",
        "description": "Entity that represents a minecart chest.",
        "base": "AbstractMinecartContainer",
        "fields": [],
    },
    {
        "name": "MinecartFurnace",
        "description": "Entity that represents a minecart furnace.",
        "base": "AbstractMinecart",
        "fields": [
            {
                "type": "Boolean",
                "name": "has_fuel",
                "default": False,
                "input": bool,
                "description": "Whether the furnace minecart has fuel.",
            }
        ],
    },
    {
        "name": "MinecartTNT",
        "description": "Entity that represents a minecart TNT.",
        "base": "AbstractMinecart",
        "fields": [],
    },
    {
        "name": "MinecartSpawner",
        "description": "Entity that represents a minecart spawner.",
        "base": "AbstractMinecart",
        "fields": [],
    },
    {
        "name": "MinecartCommandBlock",
        "description": "Entity that represents a minecart command block.",
        "base": "AbstractMinecart",
        "fields": [
            {
                "type": "String",
                "name": "command",
                "default": "",
                "input": str,
                "description": "The command stored in the command block.",
            },
            {
                "type": "TextComponent",
                "name": "last_output",
                "default": 'TextComponent("")',
                "input": "TextComponent",
                "description": "The last output from the command block.",
            },
        ],
    },
    {
        "name": "EndCrystal",
        "description": "Entity that represents an end crystal.",
        "base": "Entity",
        "fields": [
            {
                "type": "OptPosition",
                "name": "beam_target",
                "default": "None",
                "input": "tuple[int, int, int]|None",
                "description": "The position of the beam target.",
            },
            {
                "type": "Boolean",
                "name": "show_bottom",
                "default": True,
                "input": bool,
                "description": "Whether the bottom of the end crystal is shown.",
            },
        ],
    },
    {
        "name": "DragonFireball",
        "description": "Entity that represents a dragon fireball.",
        "base": "Entity",
        "fields": [],
    },
    {
        "name": "SmallFireball",
        "description": "Entity that represents a small fireball.",
        "base": "Entity",
        "fields": [
            {
                "type": "Slot",
                "name": "item",
                "default": "Slot(present=False)",
                "input": "Slot",
                "description": "The item representing the small fireball.",
            }
        ],
    },
    {
        "name": "Fireball",
        "description": "Entity that represents a fireball.",
        "base": "Entity",
        "fields": [
            {
                "type": "Slot",
                "name": "item",
                "default": "Slot(present=False)",
                "input": "Slot",
                "description": "The item representing the fireball.",
            }
        ],
    },
    {
        "name": "WitherSkull",
        "description": "Entity that represents a wither skull.",
        "base": "Entity",
        "fields": [
            {
                "type": "Boolean",
                "name": "is_invulnerable",
                "default": False,
                "input": bool,
                "description": "Whether the wither skull is invulnerable.",
            }
        ],
    },
    {
        "name": "FireworkRocket",
        "description": "Entity representing a firework rocket.",
        "base": "Entity",
        "fields": [
            {
                "type": "Slot",
                "name": "firework_info",
                "default": "Slot(present=False)",
                "input": "Slot",
                "description": "The information about the firework.",
            },
            {
                "type": "OptVarInt",
                "name": "shooter_entity_id",
                "default": "None",
                "input": "int|None",
                "description": "The entity ID of the entity that used the firework (for elytra boosting).",
            },
            {
                "type": "Boolean",
                "name": "shot_at_angle",
                "default": False,
                "input": bool,
                "description": "Whether the firework rocket was shot at an angle (from a crossbow).",
            },
        ],
    },
    {
        "name": "ItemFrame",
        "description": "Entity representing an item frame.",
        "base": "Entity",
        "fields": [
            {
                "type": "Slot",
                "name": "item",
                "default": "Slot(present=False)",
                "input": "Slot",
                "description": "The item in the item frame.",
            },
            {
                "type": "VarInt",
                "name": "rotation",
                "default": 0,
                "input": int,
                "description": "The rotation of the item frame.",
            },
        ],
    },
    {
        "name": "GlowingItemFrame",
        "description": "Entity representing a glowing item frame.",
        "base": "ItemFrame",
        "fields": [],
    },
    {
        "name": "Painting",
        "description": "Entity representing a painting.",
        "base": "Entity",
        "fields": [
            {
                "type": "PaintingVariant",
                "name": "painting_type",
                "default": 0,
                "input": "int",
                "description": "The type of painting variant.",
            }
        ],
    },
    {
        "name": "ItemEntity",
        "description": "Entity representing an item.",
        "base": "Entity",
        "fields": [
            {
                "type": "Slot",
                "name": "item",
                "default": "Slot(present=False)",
                "input": "Slot",
                "description": "The item in the item entity.",
            }
        ],
    },
    {
        "name": "LivingEntity",
        "description": "Entity that represents a living entity.",
        "base": "Entity",
        "fields": [
            {
                "type": "Byte",
                "name": "hand_states",
                "default": 0,
                "input": int,
                "available": False,
                "proxy": [
                    {
                        "type": "Masked",
                        "name": "is_hand_active",
                        "input": bool,
                        "description": "Whether the hand is active.",
                        "mask": 0x01,
                    },
                    {
                        "type": "Masked",
                        "name": "active_hand",
                        "input": int,
                        "description": "Which hand is active (0 = main hand, 1 = offhand).",
                        "mask": 0x02,
                    },
                    {
                        "type": "Masked",
                        "name": "is_riptide_spin_attack",
                        "input": bool,
                        "description": "Whether the entity is in riptide spin attack.",
                        "mask": 0x04,
                    },
                ],
                "description": "Bit mask indicating hand states.",
            },
            {
                "type": "Float",
                "name": "health",
                "default": 1.0,
                "input": float,
                "description": "The health of the living entity.",
            },
            {
                "type": "VarInt",
                "name": "potion_effect_color",
                "default": 0,
                "input": int,
                "description": "Color of the potion effect (or 0 if there is no effect).",
            },
            {
                "type": "Boolean",
                "name": "is_potion_effect_ambient",
                "default": False,
                "input": bool,
                "description": "Whether the potion effect is ambient: reduces the number of particles generated by\n"
                "    potions to 1/5 the normal amount.",
            },
            {
                "type": "VarInt",
                "name": "num_arrows",
                "default": 0,
                "input": int,
                "description": "Number of arrows in the entity.",
            },
            {
                "type": "VarInt",
                "name": "num_bee_stingers",
                "default": 0,
                "input": int,
                "description": "Number of bee stingers in the entity.",
            },
            {
                "type": "OptPosition",
                "name": "sleeping_bed_location",
                "default": "None",
                "input": "Position|None",
                "description": "Location of the bed that the entity is currently sleeping\n"
                "    in (Empty if it isn't sleeping).",
            },
        ],
    },
    {
        "name": "Player",
        "description": "Player entity.",
        "base": "LivingEntity",
        "fields": [
            {
                "type": "Float",
                "name": "additional_hearts",
                "default": 0.0,
                "input": float,
                "description": "Additional hearts of the player.",
            },
            {
                "type": "VarInt",
                "name": "score",
                "default": 0,
                "input": int,
                "description": "The score of the player.",
            },
            {
                "type": "Byte",
                "name": "displayed_skin_parts",
                "default": 0,
                "input": int,
                "available": False,
                "proxy": [
                    {
                        "type": "Masked",
                        "name": "cape_enabled",
                        "input": bool,
                        "description": "Whether the cape is enabled.",
                        "mask": 0x01,
                    },
                    {
                        "type": "Masked",
                        "name": "jacket_enabled",
                        "input": bool,
                        "description": "Whether the jacket is enabled.",
                        "mask": 0x02,
                    },
                    {
                        "type": "Masked",
                        "name": "left_sleeve_enabled",
                        "input": bool,
                        "description": "Whether the left sleeve is enabled.",
                        "mask": 0x04,
                    },
                    {
                        "type": "Masked",
                        "name": "right_sleeve_enabled",
                        "input": bool,
                        "description": "Whether the right sleeve is enabled.",
                        "mask": 0x08,
                    },
                    {
                        "type": "Masked",
                        "name": "left_pants_leg_enabled",
                        "input": bool,
                        "description": "Whether the left pants leg is enabled.",
                        "mask": 0x10,
                    },
                    {
                        "type": "Masked",
                        "name": "right_pants_leg_enabled",
                        "input": bool,
                        "description": "Whether the right pants leg is enabled.\n" "  ",
                        "mask": 0x20,
                    },
                    {
                        "type": "Masked",
                        "name": "hat_enabled",
                        "input": bool,
                        "description": "Whether the hat is enabled.",
                        "mask": 0x40,
                    },
                ],
                "description": "Bit mask indicating displayed skin parts.",
            },
            {
                "type": "Byte",
                "name": "main_hand",
                "default": 1,
                "input": int,
                "description": "The main hand of the player (0: Left, 1: Right).",
            },
            {
                "type": "NBTag",
                "name": "left_shoulder_entity_data",
                "default": "EndNBT()",
                "input": "NBTag",
                "description": "Left shoulder entity data (for occupying parrot).",
            },
            {
                "type": "NBTag",
                "name": "right_shoulder_entity_data",
                "default": "EndNBT()",
                "input": "NBTag",
                "description": "Right shoulder entity data (for occupying parrot).",
            },
        ],
    },
    {
        "name": "ArmorStand",
        "description": "Entity representing an armor stand.",
        "base": "LivingEntity",
        "fields": [
            {
                "type": "Byte",
                "name": "armorstand_flags",
                "default": 0,
                "input": int,
                "available": False,
                "proxy": [
                    {
                        "type": "Masked",
                        "name": "is_small",
                        "input": bool,
                        "description": "Whether the armor stand is small.",
                        "mask": 0x01,
                    },
                    {
                        "type": "Masked",
                        "name": "has_arms",
                        "input": bool,
                        "description": "Whether the armor stand has arms.",
                        "mask": 0x04,
                    },
                    {
                        "type": "Masked",
                        "name": "has_no_base_plate",
                        "input": bool,
                        "description": "Whether the armor stand has no base plate.",
                        "mask": 0x08,
                    },
                    {
                        "type": "Masked",
                        "name": "is_marker",
                        "input": bool,
                        "description": "Whether the armor stand is a marker.",
                        "mask": 0x10,
                    },
                ],
                "description": "Bit mask indicating various properties of the armor stand.",
            },
            {
                "type": "Rotation",
                "name": "head_rotation",
                "default": "(0.0, 0.0, 0.0)",
                "input": "tuple[float, float, float]",
                "description": "Rotation of the armor stand's head.",
            },
            {
                "type": "Rotation",
                "name": "body_rotation",
                "default": "(0.0, 0.0, 0.0)",
                "input": "tuple[float, float, float]",
                "description": "Rotation of the armor stand's body.",
            },
            {
                "type": "Rotation",
                "name": "left_arm_rotation",
                "default": "(-10.0, 0.0, -10.0)",
                "input": "tuple[float, float, float]",
                "description": "Rotation of the armor stand's left arm.",
            },
            {
                "type": "Rotation",
                "name": "right_arm_rotation",
                "default": "(-15.0, 0.0, 10.0)",
                "input": "tuple[float, float, float]",
                "description": "Rotation of the armor stand's right arm.",
            },
            {
                "type": "Rotation",
                "name": "left_leg_rotation",
                "default": "(-1.0, 0.0, -1.0)",
                "input": "tuple[float, float, float]",
                "description": "Rotation of the armor stand's left leg.",
            },
            {
                "type": "Rotation",
                "name": "right_leg_rotation",
                "default": "(1.0, 0.0, 1.0)",
                "input": "tuple[float, float, float]",
                "description": "Rotation of the armor stand's right leg.",
            },
        ],
    },
    {
        "name": "Mob",
        "description": "Generic mobile entity.",
        "base": "LivingEntity",
        "fields": [
            {
                "type": "Byte",
                "name": "mob_flags",
                "default": 0,
                "input": int,
                "available": False,
                "proxy": [
                    {
                        "type": "Masked",
                        "name": "no_ai",
                        "input": bool,
                        "description": "Whether the mob has AI.",
                        "mask": 0x01,
                    },
                    {
                        "type": "Masked",
                        "name": "is_left_handed",
                        "input": bool,
                        "description": "Whether the mob is left-handed.",
                        "mask": 0x02,
                    },
                    {
                        "type": "Masked",
                        "name": "is_aggressive",
                        "input": bool,
                        "description": "Whether the mob is aggressive.",
                        "mask": 0x04,
                    },
                ],
                "description": "Bit mask indicating various properties of the mob.",
            }
        ],
    },
    {
        "name": "AmbientCreature",
        "description": "Entity that represents an ambient creature.",
        "base": "Mob",
        "fields": [],
    },
    {
        "name": "Bat",
        "description": "Entity that represents a bat.",
        "base": "AmbientCreature",
        "fields": [
            {
                "type": "Byte",
                "name": "bat_flags",
                "default": 0,
                "input": int,
                "available": False,
                "proxy": [
                    {
                        "type": "Masked",
                        "name": "is_hanging",
                        "input": bool,
                        "description": "Whether the bat is hanging upside down.",
                        "mask": 0x01,
                    }
                ],
                "description": "Flags of the bat.",
            }
        ],
    },
    {
        "name": "PathfinderMob",
        "description": "Entity that represents a pathfinder mob.",
        "base": "Mob",
        "fields": [],
    },
    {
        "name": "WaterAnimal",
        "description": "Entity that represents a water-dwelling animal.",
        "base": "PathfinderMob",
        "fields": [],
    },
    {
        "name": "Squid",
        "description": "Entity that represents a squid.",
        "base": "WaterAnimal",
        "fields": [],
    },
    {
        "name": "Dolphin",
        "description": "Entity that represents a dolphin.",
        "base": "WaterAnimal",
        "fields": [
            {
                "type": "Position",
                "name": "treasure_position",
                "default": "(0, 0, 0)",
                "input": "tuple[int, int, int]",
                "description": "The position of the dolphin's treasure.",
            },
            {
                "type": "Boolean",
                "name": "has_fish",
                "default": False,
                "input": bool,
                "description": "Whether the dolphin has fish.",
            },
            {
                "type": "VarInt",
                "name": "moisture_level",
                "default": 2400,
                "input": int,
                "description": "The moisture level of the dolphin.",
            },
        ],
    },
    {
        "name": "AbstractFish",
        "description": "Entity that represents an abstract fish.",
        "base": "WaterAnimal",
        "fields": [
            {
                "type": "Boolean",
                "name": "from_bucket",
                "default": False,
                "input": bool,
                "description": "Whether the fish is from a bucket.",
            }
        ],
    },
    {
        "name": "Cod",
        "description": "Entity that represents a cod fish.",
        "base": "AbstractFish",
        "fields": [],
    },
    {
        "name": "PufferFish",
        "description": "Entity that represents a puffer fish.",
        "base": "AbstractFish",
        "fields": [
            {
                "type": "VarInt",
                "name": "puff_state",
                "default": 0,
                "input": int,
                "description": "The state of puffing of the puffer fish, varies from 0 to 2.",
            }
        ],
    },
    {"name": "Salmon", "description": "Entity that represents a salmon fish.", "base": "AbstractFish", "fields": []},
    {
        "name": "TropicalFish",
        "description": "Entity that represents a tropical fish.",
        "base": "AbstractFish",
        "fields": [
            {
                "type": "VarInt",
                "name": "variant",
                "default": 0,
                "input": int,
                "description": "The variant of the tropical fish.",
            }
        ],
    },
    {"name": "Tadpole", "description": "Entity that represents a tadpole.", "base": "AbstractFish", "fields": []},
    {
        "name": "AgeableMob",
        "description": "Entity that represents an ageable mob.",
        "base": "PathfinderMob",
        "fields": [
            {
                "type": "Boolean",
                "name": "is_baby",
                "default": False,
                "input": bool,
                "description": "Whether the mob is a baby.",
            }
        ],
    },
    {
        "name": "Animal",
        "description": "Entity that represents an animal.",
        "base": "AgeableMob",
        "fields": [],
    },
    {
        "name": "Sniffer",
        "description": "Entity that represents a sniffer.",
        "base": "Animal",
        "fields": [
            {
                "type": "SnifferState",
                "name": "sniffer_state",
                "default": "IDLING",
                "input": "SnifferState",
                "enum": True,
                "description": "The state of the sniffer.",
            },
            {
                "type": "VarInt",
                "name": "drop_seed_at_tick",
                "default": 0,
                "input": int,
                "description": "The tick at which the sniffer will drop seed.",
            },
        ],
    },
    {
        "name": "AbstractHorse",
        "description": "Entity that represents an abstract horse.",
        "base": "Animal",
        "fields": [
            {
                "type": "Byte",
                "name": "horse_flags",
                "default": 0,
                "input": int,
                "available": False,
                "proxy": [
                    {
                        "type": "Masked",
                        "name": "is_tame",
                        "input": bool,
                        "description": "Whether the horse is tame.",
                        "mask": 0x02,
                    },
                    {
                        "type": "Masked",
                        "name": "is_saddled",
                        "input": bool,
                        "description": "Whether the horse is saddled.",
                        "mask": 0x04,
                    },
                    {
                        "type": "Masked",
                        "name": "has_bred",
                        "input": bool,
                        "description": "Whether the horse has bred.",
                        "mask": 0x08,
                    },
                    {
                        "type": "Masked",
                        "name": "is_eating",
                        "input": bool,
                        "description": "Whether the horse is eating.",
                        "mask": 0x10,
                    },
                    {
                        "type": "Masked",
                        "name": "is_rearing",
                        "input": bool,
                        "description": "Whether the horse is rearing (on hind legs).",
                        "mask": 0x20,
                    },
                    {
                        "type": "Masked",
                        "name": "is_mouth_open",
                        "input": bool,
                        "description": "Whether the horse's mouth is open.",
                        "mask": 0x40,
                    },
                ],
                "description": "Flags for the horse.",
            }
        ],
    },
    {
        "name": "Horse",
        "description": "Entity that represents a horse.",
        "base": "AbstractHorse",
        "fields": [
            {
                "type": "VarInt",
                "name": "variant",
                "default": 0,
                "input": int,
                "description": "The variant of the horse representing its color and style.",
            }
        ],
    },
    {
        "name": "ZombieHorse",
        "description": "Entity that represents a zombie horse.",
        "base": "AbstractHorse",
        "fields": [],
    },
    {
        "name": "SkeletonHorse",
        "description": "Entity that represents a skeleton horse.",
        "base": "AbstractHorse",
        "fields": [],
    },
    {
        "name": "Camel",
        "description": "Entity that represents a camel.",
        "base": "AbstractHorse",
        "fields": [
            {
                "type": "Boolean",
                "name": "is_dashing",
                "default": False,
                "input": bool,
                "description": "Whether the camel is dashing.",
            },
            {
                "type": "VarLong",
                "name": "last_pose_change_tick",
                "default": 0,
                "input": int,
                "description": "The tick at which the camel's pose was last changed.",
            },
        ],
    },
    {
        "name": "ChestedHorse",
        "description": "Entity that represents a horse with a chest.",
        "base": "AbstractHorse",
        "fields": [
            {
                "type": "Boolean",
                "name": "has_chest",
                "default": False,
                "input": bool,
                "description": "Whether the horse has a chest.",
            }
        ],
    },
    {
        "name": "Donkey",
        "description": "Entity that represents a donkey.",
        "base": "ChestedHorse",
        "fields": [],
    },
    {
        "name": "Llama",
        "description": "Entity that represents a llama.",
        "base": "ChestedHorse",
        "fields": [
            {
                "type": "VarInt",
                "name": "strength",
                "default": 0,
                "input": int,
                "description": "The strength of the llama, representing the number of columns of 3 slots in its\n"
                "    inventory once a chest is equipped.",
            },
            {
                "type": "VarInt",
                "name": "carpet_color",
                "default": -1,
                "input": int,
                "description": "The color of the carpet equipped on the llama, represented as a dye color. -1 if no\n"
                "    carpet is equipped.",
            },
            {
                "type": "VarInt",
                "name": "variant",
                "default": 0,
                "input": int,
                "description": "The variant of the llama.",
            },
        ],
    },
    {"name": "TraderLlama", "description": "Entity that represents a trader llama.", "base": "Llama", "fields": []},
    {"name": "Mule", "description": "Entity that represents a mule.", "base": "ChestedHorse", "fields": []},
    {
        "name": "Axolotl",
        "description": "Entity that represents an axolotl.",
        "base": "Animal",
        "fields": [
            {
                "type": "VarInt",
                "name": "variant",
                "default": 0,
                "input": int,
                "description": "The variant of the axolotl.",
            },
            {
                "type": "Boolean",
                "name": "is_playing_dead",
                "default": False,
                "input": bool,
                "description": "Whether the axolotl is currently playing dead.",
            },
            {
                "type": "Boolean",
                "name": "is_spawned_from_bucket",
                "default": False,
                "input": bool,
                "description": "Whether the axolotl was spawned from a bucket.",
            },
        ],
    },
    {
        "name": "Bee",
        "description": "Entity that represents a bee.",
        "base": "Animal",
        "fields": [
            {
                "type": "Byte",
                "name": "bee_flags",
                "default": 0,
                "input": int,
                "available": False,
                "description": "Flags representing various properties of the bee.",
                "proxy": [
                    {
                        "type": "Masked",
                        "name": "is_angry",
                        "input": bool,
                        "description": "Whether the bee is angry.",
                        "mask": 0x02,
                    },
                    {
                        "type": "Masked",
                        "name": "has_stung",
                        "input": bool,
                        "description": "Whether the bee has stung.",
                        "mask": 0x04,
                    },
                    {
                        "type": "Masked",
                        "name": "has_nectar",
                        "input": bool,
                        "description": "Whether the bee has nectar.",
                        "mask": 0x08,
                    },
                ],
            },
            {
                "type": "VarInt",
                "name": "anger_time",
                "default": 0,
                "input": int,
                "description": "The time in ticks for which the bee remains angry.",
            },
        ],
    },
    {
        "name": "Fox",
        "description": "Entity that represents a fox.",
        "base": "Animal",
        "fields": [
            {
                "type": "VarInt",
                "name": "fox_type",
                "default": 0,
                "input": int,
                "description": "The type of the fox.",
            },
            {
                "type": "Byte",
                "name": "fox_flags",
                "default": 0,
                "input": int,
                "available": False,
                "description": "Bit mask representing various states of the fox.",
                "proxy": [
                    {
                        "type": "Masked",
                        "name": "is_sitting",
                        "input": bool,
                        "description": "Whether the fox is sitting.",
                        "mask": 0x01,
                    },
                    {
                        "type": "Masked",
                        "name": "is_fox_crouching",
                        "input": bool,
                        "description": "Whether the fox is crouching.",
                        "mask": 0x04,
                    },
                    {
                        "type": "Masked",
                        "name": "is_interested",
                        "input": bool,
                        "description": "Whether the fox is interested.",
                        "mask": 0x08,
                    },
                    {
                        "type": "Masked",
                        "name": "is_pouncing",
                        "input": bool,
                        "description": "Whether the fox is pouncing.",
                        "mask": 0x10,
                    },
                    {
                        "type": "Masked",
                        "name": "is_sleeping",
                        "input": bool,
                        "description": "Whether the fox is sleeping.",
                        "mask": 0x20,
                    },
                    {
                        "type": "Masked",
                        "name": "is_faceplanted",
                        "input": bool,
                        "description": "Whether the fox is faceplanted.",
                        "mask": 0x40,
                    },
                    {
                        "type": "Masked",
                        "name": "is_defending",
                        "input": bool,
                        "description": "Whether the fox is defending.",
                        "mask": 0x80,
                    },
                ],
            },
            {
                "type": "OptUUID",
                "name": "trusted_uuid",
                "default": "None",
                "input": "UUID|None",
                "description": "The UUID of the player that the fox trusts.",
            },
            {
                "type": "OptUUID",
                "name": "trusted_uuid_2",
                "default": "None",
                "input": "UUID|None",
                "description": "Another player that the fox trusts.",
            },
        ],
    },
    {
        "name": "Frog",
        "description": "Entity that represents a frog.",
        "base": "Animal",
        "fields": [
            {
                "type": "FrogVariant",
                "name": "variant",
                "default": 0,  # No registry yet
                "input": "int",
                "description": "The variant of the frog.",
            },
            {
                "type": "OptVarInt",
                "name": "tongue_target",
                "default": 0,
                "input": int,
                "description": "The target of the frog's tongue.",
            },
        ],
    },
    {
        "name": "Ocelot",
        "description": "Entity that represents an ocelot.",
        "base": "Animal",
        "fields": [
            {
                "type": "Boolean",
                "name": "is_trusting",
                "default": False,
                "input": bool,
                "description": "Whether the ocelot is trusting.",
            }
        ],
    },
    {
        "name": "Panda",
        "description": "Entity that represents a panda.",
        "base": "Animal",
        "fields": [
            {
                "type": "VarInt",
                "name": "breed_timer",
                "default": 0,
                "input": int,
                "description": "The breed timer of the panda.",
            },
            {
                "type": "VarInt",
                "name": "sneeze_timer",
                "default": 0,
                "input": int,
                "description": "The sneeze timer of the panda.",
            },
            {
                "type": "VarInt",
                "name": "eat_timer",
                "default": 0,
                "input": int,
                "description": "The eat timer of the panda.",
            },
            {
                "type": "Byte",
                "name": "main_gene",
                "default": 0,
                "input": int,
                "description": "The main gene of the panda.",
            },
            {
                "type": "Byte",
                "name": "hidden_gene",
                "default": 0,
                "input": int,
                "description": "The hidden gene of the panda.",
            },
            {
                "type": "Byte",
                "name": "panda_flags",
                "default": 0,
                "input": int,
                "available": False,
                "description": "Bit mask representing various states of the panda.",
                "proxy": [
                    {
                        "type": "Masked",
                        "name": "is_sneezing",
                        "input": bool,
                        "description": "Whether the panda is sneezing.",
                        "mask": 0x02,
                    },
                    {
                        "type": "Masked",
                        "name": "is_rolling",
                        "input": bool,
                        "description": "Whether the panda is rolling.",
                        "mask": 0x04,
                    },
                    {
                        "type": "Masked",
                        "name": "is_sitting",
                        "input": bool,
                        "description": "Whether the panda is sitting.",
                        "mask": 0x08,
                    },
                    {
                        "type": "Masked",
                        "name": "is_on_back",
                        "input": bool,
                        "description": "Whether the panda is on its back.",
                        "mask": 0x10,
                    },
                ],
            },
        ],
    },
    {
        "name": "Pig",
        "description": "Entity that represents a pig.",
        "base": "Animal",
        "fields": [
            {
                "type": "Boolean",
                "name": "has_saddle",
                "default": False,
                "input": bool,
                "description": "Whether the pig has a saddle.",
            },
            {
                "type": "VarInt",
                "name": "boost_time",
                "default": 0,
                "input": int,
                "description": "Total time to 'boost' with a carrot on a stick for.",
            },
        ],
    },
    {
        "name": "Rabbit",
        "description": "Entity that represents a rabbit.",
        "base": "Animal",
        "fields": [
            {
                "type": "VarInt",
                "name": "rabbit_type",
                "default": 0,
                "input": int,
                "description": "The type of the rabbit.",
            }
        ],
    },
    {
        "name": "Turtle",
        "description": "Entity that represents a turtle.",
        "base": "Animal",
        "fields": [
            {
                "type": "Position",
                "name": "home_pos",
                "default": "(0, 0, 0)",
                "input": "tuple[int, int, int]",
                "description": "The home position of the turtle.",
            },
            {
                "type": "Boolean",
                "name": "has_egg",
                "default": False,
                "input": bool,
                "description": "Whether the turtle has an egg.",
            },
            {
                "type": "Boolean",
                "name": "is_laying_egg",
                "default": False,
                "input": bool,
                "description": "Whether the turtle is laying an egg.",
            },
            {
                "type": "Position",
                "name": "travel_pos",
                "default": "(0, 0, 0)",
                "input": "tuple[int, int, int]",
                "description": "The travel position of the turtle.",
            },
            {
                "type": "Boolean",
                "name": "is_going_home",
                "default": False,
                "input": bool,
                "description": "Whether the turtle is going home.",
            },
            {
                "type": "Boolean",
                "name": "is_traveling",
                "default": False,
                "input": bool,
                "description": "Whether the turtle is traveling.",
            },
        ],
    },
    {
        "name": "PolarBear",
        "description": "Entity that represents a polar bear.",
        "base": "Animal",
        "fields": [
            {
                "type": "Boolean",
                "name": "is_standing_up",
                "default": False,
                "input": bool,
                "description": "Whether the polar bear is standing up.",
            }
        ],
    },
    {  # Chicken
        "name": "Chicken",
        "description": "Entity representing a chicken.",
        "base": "Animal",
        "fields": [],
    },
    {  # Cow
        "name": "Cow",
        "description": "Entity representing a cow.",
        "base": "Animal",
        "fields": [],
    },
    {  # Mooshroom
        "name": "Mooshroom",
        "description": "Entity representing a mooshroom.",
        "base": "Cow",
        "fields": [
            {
                "type": "String",
                "name": "variant",
                "default": "red",
                "input": str,
                "description": "The variant of the mooshroom: 'red' or 'brown'.",
            }
        ],
    },
    {  # Hoglin
        "name": "Hoglin",
        "description": "Entity representing a hoglin.",
        "base": "Animal",
        "fields": [
            {
                "type": "Boolean",
                "name": "immune_to_zombification",
                "default": False,
                "input": bool,
                "description": "Whether the hoglin is immune to zombification.",
            }
        ],
    },
    {  # Sheep
        "name": "Sheep",
        "description": "Entity representing a sheep.",
        "base": "Animal",
        "fields": [
            {
                "type": "Byte",
                "name": "sheep_data",
                "default": 0,
                "input": int,
                "available": False,
                "proxy": [
                    {
                        "type": "Masked",
                        "name": "color_id",
                        "input": int,
                        "description": "The color of the sheep.",
                        "mask": 0x0F,
                    },
                    {
                        "type": "Masked",
                        "name": "is_sheared",
                        "input": bool,
                        "description": "Whether the sheep is sheared.",
                        "mask": 0x10,
                    },
                ],
                "description": "Data of the sheep.",
            }
        ],
    },
    {  # Strider
        "name": "Strider",
        "description": "Entity representing a strider.",
        "base": "Animal",
        "fields": [
            {
                "type": "VarInt",
                "name": "boost_duration",
                "default": 0,
                "input": int,
                "description": "Total time to 'boost' with warped fungus on a stick.",
            },
            {
                "type": "Boolean",
                "name": "is_shaking",
                "default": False,
                "input": bool,
                "description": "Whether the strider is shaking. (True unless riding a vehicle or on or in a block\n"
                "    tagged with strider_warm_blocks (default: lava))",
            },
            {
                "type": "Boolean",
                "name": "has_saddle",
                "default": False,
                "input": bool,
                "description": "Whether the strider has a saddle.",
            },
        ],
    },
    {  # Goat
        "name": "Goat",
        "description": "Entity representing a goat.",
        "base": "Animal",
        "fields": [
            {
                "type": "Boolean",
                "name": "is_screaming_goat",
                "default": False,
                "input": bool,
                "description": "Whether the goat is a screaming goat.",
            },
            {
                "type": "Boolean",
                "name": "has_left_horn",
                "default": True,
                "input": bool,
                "description": "Whether the goat has a left horn.",
            },
            {
                "type": "Boolean",
                "name": "has_right_horn",
                "default": True,
                "input": bool,
                "description": "Whether the goat has a right horn.",
            },
        ],
    },
    {  # Tameable Animal
        "name": "TameableAnimal",
        "description": "Entity representing a tameable animal.",
        "base": "Animal",
        "fields": [
            {
                "type": "Byte",
                "name": "tameable_data",
                "default": 0,
                "input": int,
                "available": False,
                "proxy": [
                    {
                        "type": "Masked",
                        "name": "is_sitting",
                        "input": bool,
                        "description": "Whether the animal is sitting.",
                        "mask": 0x01,
                    },
                    {
                        "type": "Masked",
                        "name": "is_tamed",
                        "input": bool,
                        "description": "Whether the animal is tamed.",
                        "mask": 0x04,
                    },
                ],
                "description": "Data of the tameable animal.",
            },
            {
                "type": "OptUUID",
                "name": "owner_uuid",
                "default": "None",
                "input": "UUID|None",
                "description": "The UUID of the owner, if the animal is tamed.",
            },
        ],
    },
    {  # Cat
        "name": "Cat",
        "description": "Entity representing a cat.",
        "base": "TameableAnimal",
        "fields": [
            {
                "type": "CatVariant",
                "name": "cat_variant",
                "default": 0,  # No registry yet
                "input": int,
                "description": "The variant of the cat.",
            },
            {
                "type": "Boolean",
                "name": "is_lying",
                "default": False,
                "input": bool,
                "description": "Whether the cat is lying down.",
            },
            {
                "type": "Boolean",
                "name": "is_relaxed",
                "default": False,
                "input": bool,
                "description": "Unknown use. When true, the cat's head goes slightly upwards.",
            },
            {
                "type": "VarInt",
                "name": "collar_color",
                "default": 14,
                "input": int,
                "description": "The color of the cat's collar, using dye values.",
            },
        ],
    },
    {  # Wolf
        "name": "Wolf",
        "description": "Entity representing a wolf.",
        "base": "TameableAnimal",
        "fields": [
            {
                "type": "Boolean",
                "name": "is_begging",
                "default": False,
                "input": bool,
                "description": "Whether the wolf is begging.",
            },
            {
                "type": "VarInt",
                "name": "collar_color",
                "default": 14,
                "input": int,
                "description": "The color of the wolf's collar, using dye values.",
            },
            {
                "type": "VarInt",
                "name": "anger_time",
                "default": 0,
                "input": int,
                "description": "The time for which the wolf remains angry.",
            },
        ],
    },
    {  # Parrot
        "name": "Parrot",
        "description": "Entity representing a parrot.",
        "base": "TameableAnimal",
        "fields": [
            {
                "type": "VarInt",
                "name": "variant",
                "default": 0,
                "input": int,
                "description": "The variant of the parrot.",
            }
        ],
    },
    {  # Abstract Villager
        "name": "AbstractVillager",
        "description": "Entity representing an abstract villager.",
        "base": "AgeableMob",
        "fields": [
            {
                "type": "VarInt",
                "name": "head_shake_timer",
                "default": 0,
                "input": int,
                "description": "The head shake timer of the villager, starting at 40 and decrementing each tick.",
            }
        ],
    },
    {  # Villager
        "name": "Villager",
        "description": "Entity representing a villager.",
        "base": "AbstractVillager",
        "fields": [
            {
                "type": "VillagerData",
                "name": "villager_data",
                "default": "(0, 0, 0)",
                "input": "tuple[int, int, int]",
                "description": "The data associated with the villager.",
            }
        ],
    },
    {  # Wandering Trader
        "name": "WanderingTrader",
        "description": "Entity representing a wandering trader.",
        "base": "AbstractVillager",
        "fields": [],
    },
    {  # Abstract Golem
        "name": "AbstractGolem",
        "description": "Entity representing an abstract golem.",
        "base": "PathfinderMob",
        "fields": [],
    },
    {  # Iron Golem
        "name": "IronGolem",
        "description": "Entity representing an iron golem.",
        "base": "AbstractGolem",
        "fields": [
            {
                "type": "Byte",
                "name": "iron_golem_flags",
                "default": 0,
                "input": int,
                "available": False,
                "proxy": [
                    {
                        "type": "Masked",
                        "name": "is_player_created",
                        "input": bool,
                        "description": "Whether the iron golem was created by a player.",
                        "mask": 0x01,
                    }
                ],
                "description": "Flags of the iron golem.",
            }
        ],
    },
    {  # Snow Golem
        "name": "SnowGolem",
        "description": "Entity representing a snow golem.",
        "base": "AbstractGolem",
        "fields": [
            {
                "type": "Byte",
                "name": "snow_golem_flags",
                "default": 0x10,
                "input": int,
                "available": False,
                "proxy": [
                    {
                        "type": "Masked",
                        "name": "has_pumpkin",
                        "input": bool,
                        "description": "Whether the snow golem has a pumpkin on its head.",
                        "mask": 0x10,
                    },
                ],
                "description": "Flags of the snow golem.",
            }
        ],
    },
    {  # Shulker
        "name": "Shulker",
        "description": "Entity representing a shulker.",
        "base": "AbstractGolem",
        "fields": [
            {
                "type": "Direction",
                "name": "attach_face",
                "default": "DOWN",
                "enum": True,
                "input": "Direction",
                "description": "The face to which the shulker is attached.",
            },
            {
                "type": "Byte",
                "name": "shield_height",
                "default": 0,
                "input": int,
                "description": "The shield height of the shulker.",
            },
            {
                "type": "Byte",
                "name": "color",
                "default": 16,
                "input": int,
                "description": "The color of the shulker, using dye color values.",
            },
        ],
    },
    {  # Monster
        "name": "Monster",
        "description": "Entity representing a monster.",
        "base": "PathfinderMob",
        "fields": [],
    },
    {  # Base Piglin
        "name": "BasePiglin",
        "description": "Entity representing a base piglin.",
        "base": "Monster",
        "fields": [
            {
                "type": "Boolean",
                "name": "is_immune_to_zombification",
                "default": False,
                "input": bool,
                "description": "Indicates if the piglin is immune to zombification.",
            }
        ],
    },
    {  # Piglin
        "name": "Piglin",
        "description": "Entity representing a piglin.",
        "base": "BasePiglin",
        "fields": [
            {
                "type": "Boolean",
                "name": "is_baby",
                "default": False,
                "input": bool,
                "description": "Indicates if the piglin is a baby.",
            },
            {
                "type": "Boolean",
                "name": "is_charging_crossbow",
                "default": False,
                "input": bool,
                "description": "Indicates if the piglin is charging a crossbow.",
            },
            {
                "type": "Boolean",
                "name": "is_dancing",
                "default": False,
                "input": bool,
                "description": "Indicates if the piglin is dancing.",
            },
        ],
    },
    {  # Piglin Brute
        "name": "PiglinBrute",
        "description": "Entity representing a piglin brute.",
        "base": "BasePiglin",
        "fields": [],
    },
    {  # Blaze
        "name": "Blaze",
        "description": "Entity representing a blaze.",
        "base": "Monster",
        "fields": [
            {
                "type": "Byte",
                "name": "blaze_flags",
                "default": 0,
                "input": int,
                "available": False,
                "proxy": [
                    {
                        "type": "Masked",
                        "name": "is_blaze_on_fire",
                        "input": bool,
                        "description": "Whether the blaze is on fire.",
                        "mask": 0x01,
                    },
                ],
                "description": "Flags of the blaze.",
            }
        ],
    },
    {  # Creeper
        "name": "Creeper",
        "description": "Entity representing a creeper.",
        "base": "Monster",
        "fields": [
            {
                "type": "VarInt",
                "name": "state",
                "default": -1,
                "input": int,
                "description": "The state of the creeper (-1 = idle, 1 = fuse).",
            },
            {
                "type": "Boolean",
                "name": "is_charged",
                "default": False,
                "input": bool,
                "description": "Indicates if the creeper is charged.",
            },
            {
                "type": "Boolean",
                "name": "is_ignited",
                "default": False,
                "input": bool,
                "description": "Indicates if the creeper is ignited.",
            },
        ],
    },
    {  # Endermite
        "name": "Endermite",
        "description": "Entity representing an endermite.",
        "base": "Monster",
        "fields": [],
    },
    {  # Giant
        "name": "Giant",
        "description": "Entity representing a giant.",
        "base": "Monster",
        "fields": [],
    },
    {  # Guardian
        "name": "Guardian",
        "description": "Entity representing a guardian.",
        "base": "Monster",
        "fields": [
            {
                "type": "Boolean",
                "name": "is_retracting_spikes",
                "default": False,
                "input": bool,
                "description": "Indicates if the guardian is retracting spikes.",
            },
            {
                "type": "VarInt",
                "name": "target_eid",
                "default": 0,
                "input": int,
                "description": "The Entity ID of the target.",
            },
        ],
    },
    {  # Elder Guardian
        "name": "ElderGuardian",
        "description": "Entity representing an elder guardian.",
        "base": "Guardian",
        "fields": [],
    },
    {  # Silverfish
        "name": "Silverfish",
        "description": "Entity representing a silverfish.",
        "base": "Monster",
        "fields": [],
    },
    {  # Raider
        "name": "Raider",
        "description": "Entity representing a raider.",
        "base": "Monster",
        "fields": [
            {
                "type": "Boolean",
                "name": "is_celebrating",
                "default": False,
                "input": bool,
                "description": "Indicates if the raider is celebrating.",
            }
        ],
    },
    {  # Abstract Illager
        "name": "AbstractIllager",
        "description": "Entity representing an abstract illager.",
        "base": "Raider",
        "fields": [],
    },
    {  # Vindicator
        "name": "Vindicator",
        "description": "Entity representing a vindicator.",
        "base": "AbstractIllager",
        "fields": [],
    },
    {  # Pillager
        "name": "Pillager",
        "description": "Entity representing a pillager.",
        "base": "AbstractIllager",
        "fields": [
            {
                "type": "Boolean",
                "name": "is_charging",
                "default": False,
                "input": bool,
                "description": "Indicates if the pillager is charging.",
            }
        ],
    },
    {  # Spellcaster Illager
        "name": "SpellcasterIllager",
        "description": "Entity representing a spellcaster illager.",
        "base": "AbstractIllager",
        "fields": [
            {
                "type": "Byte",
                "name": "spell",
                "default": 0,
                "input": int,
                "description": "The type of spell the illager is casting. (0: none, 1: summon vex, 2: attack,\n"
                "    3: wololo, 4: disappear, 5: blindness)",
            }
        ],
    },
    {  # Evoker
        "name": "Evoker",
        "description": "Entity representing an evoker.",
        "base": "SpellcasterIllager",
        "fields": [],
    },
    {  # Illusioner
        "name": "Illusioner",
        "description": "Entity representing an illusioner.",
        "base": "SpellcasterIllager",
        "fields": [],
    },
    {  # Ravager
        "name": "Ravager",
        "description": "Entity representing a ravager.",
        "base": "Raider",
        "fields": [],
    },
    {  # Witch
        "name": "Witch",
        "description": "Entity representing a witch.",
        "base": "Raider",
        "fields": [
            {
                "type": "Boolean",
                "name": "is_drinking_potion",
                "default": False,
                "input": bool,
                "description": "Indicates if the witch is drinking a potion.",
            }
        ],
    },
    {  # Evoker Fangs
        "name": "EvokerFangs",
        "description": "Entity representing evoker fangs.",
        "base": "Entity",
        "fields": [],
    },
    {  # Vex
        "name": "Vex",
        "description": "Entity representing a vex.",
        "base": "Monster",
        "fields": [
            {
                "type": "Byte",
                "name": "vex_flags",
                "default": 0,
                "input": int,
                "available": False,
                "proxy": [
                    {
                        "type": "Masked",
                        "name": "is_attacking",
                        "input": bool,
                        "description": "Indicates if the vex is charging.",
                        "mask": 0x01,
                    },
                ],
                "description": "Flags of the vex.",
            }
        ],
    },
    {  # Abstract Skeleton
        "name": "AbstractSkeleton",
        "description": "Entity representing an abstract skeleton.",
        "base": "Monster",
        "fields": [],
    },
    {  # Skeleton
        "name": "Skeleton",
        "description": "Entity representing a skeleton.",
        "base": "AbstractSkeleton",
        "fields": [],
    },
    {  # Wither Skeleton
        "name": "WitherSkeleton",
        "description": "Entity representing a wither skeleton.",
        "base": "AbstractSkeleton",
        "fields": [],
    },
    {  # Stray
        "name": "Stray",
        "description": "Entity representing a stray skeleton.",
        "base": "AbstractSkeleton",
        "fields": [],
    },
    {  # Spider
        "name": "Spider",
        "description": "Entity representing a spider.",
        "base": "Monster",
        "fields": [
            {
                "type": "Byte",
                "name": "spider_flags",
                "default": 0,
                "input": int,
                "available": False,
                "proxy": [
                    {
                        "type": "Masked",
                        "name": "is_climbing",
                        "input": bool,
                        "description": "Whether the spider is climbing.",
                        "mask": 0x01,
                    },
                ],
                "description": "Flags of the spider.",
            }
        ],
    },
    {  # Warden
        "name": "Warden",
        "description": "Entity representing a warden.",
        "base": "Monster",
        "fields": [
            {
                "type": "VarInt",
                "name": "anger_level",
                "default": 0,
                "input": int,
                "description": "The level of anger of the warden.",
            }
        ],
    },
    {  # Wither
        "name": "Wither",
        "description": "Entity representing a wither.",
        "base": "Monster",
        "fields": [
            {
                "type": "VarInt",
                "name": "center_head_target",
                "default": 0,
                "input": int,
                "description": "The entity ID of the target for the center head. (0 if no target)",
            },
            {
                "type": "VarInt",
                "name": "left_head_target",
                "default": 0,
                "input": int,
                "description": "The entity ID of the target for the left head. (0 if no target)",
            },
            {
                "type": "VarInt",
                "name": "right_head_target",
                "default": 0,
                "input": int,
                "description": "The entity ID of the target for the right head. (0 if no target)",
            },
            {
                "type": "VarInt",
                "name": "invulnerable_time",
                "default": 0,
                "input": int,
                "description": "The amount of time the wither is invulnerable.",
            },
        ],
    },
    {  # Zoglin
        "name": "Zoglin",
        "description": "Entity representing a zoglin.",
        "base": "Monster",
        "fields": [
            {
                "type": "Boolean",
                "name": "is_baby",
                "default": False,
                "input": bool,
                "description": "Indicates whether the zoglin is a baby.",
            }
        ],
    },
    {  # Zombie
        "name": "Zombie",
        "description": "Entity representing a zombie.",
        "base": "Monster",
        "fields": [
            {
                "type": "Boolean",
                "name": "is_baby",
                "default": False,
                "input": bool,
                "description": "Indicates whether the zombie is a baby.",
            },
            {
                "type": "VarInt",
                "name": "_zombie_type",
                "default": 0,
                "input": int,
                "description": "Unused metadata. (Previously used for zombie type)",
            },
            {
                "type": "Boolean",
                "name": "is_becoming_drowned",
                "default": False,
                "input": bool,
                "description": "Indicates whether the zombie is in the process of becoming a drowned.",
            },
        ],
    },
    {  # Zombie Villager
        "name": "ZombieVillager",
        "description": "Entity representing a zombie villager.",
        "base": "Zombie",
        "fields": [
            {
                "type": "Boolean",
                "name": "is_converting",
                "default": False,
                "input": bool,
                "description": "Indicates whether the zombie villager is currently converting.",
            },
            {
                "type": "VillagerData",
                "name": "villager_data",
                "default": "(0, 0, 0)",
                "input": "tuple[int, int, int]",
                "description": "The data of the villager associated with the zombie villager.",
            },
        ],
    },
    {  # Husk
        "name": "Husk",
        "description": "Entity representing a husk.",
        "base": "Zombie",
        "fields": [],
    },
    {  # Drowned
        "name": "Drowned",
        "description": "Entity representing a drowned.",
        "base": "Zombie",
        "fields": [],
    },
    {  # Zombified Piglin
        "name": "ZombifiedPiglin",
        "description": "Entity representing a zombified piglin.",
        "base": "Zombie",
        "fields": [],
    },
    {  # Enderman
        "name": "Enderman",
        "description": "Entity representing an enderman.",
        "base": "Monster",
        "fields": [
            {
                "type": "OptBlockState",
                "name": "carried_block",
                "default": "Absent",
                "input": str,
                "description": "The block the enderman is carrying.",
            },
            {
                "type": "Boolean",
                "name": "is_screaming",
                "default": False,
                "input": bool,
                "description": "Indicates if the enderman is screaming.",
            },
            {
                "type": "Boolean",
                "name": "is_staring",
                "default": False,
                "input": bool,
                "description": "Indicates if the enderman is staring.",
            },
        ],
    },
    {  # Ender Dragon
        "name": "EnderDragon",
        "description": "Entity representing an ender dragon.",
        "base": "Mob",
        "fields": [
            {
                "type": "DragonPhase",
                "name": "dragon_phase",
                "default": "HOVERING_NO_AI",
                "enum": True,
                "input": "DragonPhase",
                "description": "The current phase of the ender dragon.",
            }
        ],
    },
    {  # Flying
        "name": "Flying",
        "description": "Base entity for flying mobs.",
        "base": "Mob",
        "fields": [],
    },
    {  # Ghast
        "name": "Ghast",
        "description": "Entity representing a ghast.",
        "base": "Flying",
        "fields": [
            {
                "type": "Boolean",
                "name": "is_attacking",
                "default": False,
                "input": bool,
                "description": "Indicates if the ghast is attacking.",
            }
        ],
    },
    {  # Phantom
        "name": "Phantom",
        "description": "Entity representing a phantom.",
        "base": "Flying",
        "fields": [
            {"type": "VarInt", "name": "size", "default": 0, "input": int, "description": "The size of the phantom."}
        ],
    },
    {  # Slime
        "name": "Slime",
        "description": "Entity representing a slime.",
        "base": "Mob",
        "fields": [
            {"type": "VarInt", "name": "size", "default": 1, "input": int, "description": "The size of the slime."}
        ],
    },
    {  # Llama Spit
        "name": "LlamaSpit",
        "description": "Entity representing spit from a llama.",
        "base": "Entity",
        "fields": [],
    },
    {  # Primed TNT
        "name": "PrimedTnt",
        "description": "Entity representing primed TNT.",
        "base": "Entity",
        "fields": [
            {
                "type": "VarInt",
                "name": "fuse_time",
                "default": 80,
                "input": int,
                "description": "The fuse time for the primed TNT.",
            }
        ],
    },
]
