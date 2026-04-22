import random

from api.models.game_state import BSPNode, Rect, Room

CHARACTERS = ["Weasel", "Sal", "Billy", "Finn"]

TOTAL_ITEMS = 8
START_ROOM = "Cell"
BOSS_ROOM = "Wardens Office"

MAP_AREA = [800, 800]
MIN_ROOM_SIZE = [20, 20]
MAX_ROOM_SIZE = [40, 40]
ROOM_PADDING = 10


def _can_split_horizontally(node: BSPNode, min_leaf_height: int) -> bool:
    """Check whether a node can be divided into two valid child heights."""
    return node.height >= min_leaf_height * 2


def _can_split_vertically(node: BSPNode, min_leaf_width: int) -> bool:
    """Check whether a node can be divided into two valid child widths."""
    return node.width >= min_leaf_width * 2


def _split_node(node: BSPNode, min_leaf_width: int, min_leaf_height: int) -> bool:
    """Split one node into two children that can both still hold a room."""
    can_split_horizontally = _can_split_horizontally(node, min_leaf_height)
    can_split_vertically = _can_split_vertically(node, min_leaf_width)

    if not can_split_horizontally and not can_split_vertically:
        return False

    if can_split_horizontally and can_split_vertically:
        split_horizontally = random.choice([True, False])
        if node.width > node.height * 1.25:
            split_horizontally = False
        elif node.height > node.width * 1.25:
            split_horizontally = True
    else:
        split_horizontally = can_split_horizontally

    if split_horizontally:
        split_point = random.randint(min_leaf_height, node.height - min_leaf_height)
        node.left = BSPNode(node.x, node.y, node.width, split_point)
        node.right = BSPNode(node.x, node.y + split_point, node.width, node.height - split_point)
    else:
        split_point = random.randint(min_leaf_width, node.width - min_leaf_width)
        node.left = BSPNode(node.x, node.y, split_point, node.height)
        node.right = BSPNode(node.x + split_point, node.y, node.width - split_point, node.height)

    return True


def get_leaves(node: BSPNode) -> list[BSPNode]:
    """Collect all leaf nodes from the current BSP tree."""
    if node.is_leaf():
        return [node]
    return (get_leaves(node.left) if node.left else []) + (get_leaves(node.right) if node.right else [])


def _generate_leaf_nodes(target_leaf_count: int) -> list[BSPNode]:
    """
    Split the map until there is one BSP leaf per named room.

    This keeps BSP responsible for layout only. Gameplay topology still comes
    from ROOM_DEFINITIONS until the procedural graph layer is built separately.
    """
    min_leaf_width = MIN_ROOM_SIZE[0] + (ROOM_PADDING * 2)
    min_leaf_height = MIN_ROOM_SIZE[1] + (ROOM_PADDING * 2)

    root = BSPNode(0, 0, MAP_AREA[0], MAP_AREA[1])
    leaves = [root]

    while len(leaves) < target_leaf_count:
        splittable_leaves = [
            leaf
            for leaf in leaves
            if _can_split_vertically(leaf, min_leaf_width) or _can_split_horizontally(leaf, min_leaf_height)
        ]
        if not splittable_leaves:
            raise RuntimeError("Map area is too small to place all named rooms.")

        leaf_to_split = max(splittable_leaves, key=lambda leaf: leaf.width * leaf.height)
        if not _split_node(leaf_to_split, min_leaf_width, min_leaf_height):
            raise RuntimeError("Failed to split a BSP leaf that was marked splittable.")

        leaves = get_leaves(root)

    return leaves


def _build_room_rect(leaf: BSPNode) -> Rect:
    """Inset the room within its BSP leaf so adjacent rooms do not touch edges."""
    room_x = leaf.x + ROOM_PADDING
    room_y = leaf.y + ROOM_PADDING
    room_w = leaf.width - (ROOM_PADDING * 2)
    room_h = leaf.height - (ROOM_PADDING * 2)
    return Rect(position=[room_x, room_y], size=[room_w, room_h])


def build_rooms() -> dict[str, Room]:
    """
    Actual pipeline orchestrator for the whole BSP generation.

    This version uses BSP for geometry only. The room graph is still copied
    from ROOM_DEFINITIONS so movement and win conditions remain stable while
    the procedural connection layer is still under development.

    Internal functions use dataclasses, maps back to Pydantic models / boundaries
    See /api/models/game_state.py for relevant defs
    """
    static_room_names = list(ROOM_DEFINITIONS.keys())
    leaves = _generate_leaf_nodes(len(static_room_names))
    generated_rooms_dict: dict[str, Room] = {}

    for room_name, leaf in zip(static_room_names, leaves, strict=True):
        leaf.room_name = room_name
        room_definition = ROOM_DEFINITIONS[room_name]

        generated_rooms_dict[room_name] = Room(
            name=room_name,
            connections=dict(room_definition["connections"]),
            item=room_definition["item"],
            room_info=_build_room_rect(leaf),
        )

    return generated_rooms_dict


# Hardcoded but included at the bottom to prevent the file from becoming chaotic 
ROOM_DEFINITIONS: dict[str, dict] = {
    "Cell": {
        "connections": {"East": "Michigan Avenue"},
        "item": None,
    },
    "Michigan Avenue": {
        "connections": {
            "West": "Cell",
            "North": "Times Square",
            "South": "Broadway",
            "East": "Showers",
        },
        "item": None,
    },
    "Broadway": {
        "connections": {
            "North": "Michigan Avenue",
            "East": "Laundry Room",
            "South": "Cafeteria",
        },
        "item": None,
    },
    "Times Square": {
        "connections": {
            "South": "Michigan Avenue",
            "East": "Library",
            "North": "Citadel Tunnels",
            "West": "Infirmary",
        },
        "item": None,
    },
    "Showers": {
        "connections": {
            "West": "Michigan Avenue",
            "South": "Laundry Room",
        },
        "item": None,
    },
    "Laundry Room": {
        "connections": {
            "West": "Broadway",
            "North": "Showers",
        },
        "item": "rigging",
    },
    "Cafeteria": {
        "connections": {
            "North": "Broadway",
            "East": "Kitchen",
            "South": "Recreation Yard",
        },
        "item": None,
    },
    "Kitchen": {
        "connections": {"West": "Cafeteria"},
        "item": "fuel tank",
    },
    "Recreation Yard": {
        "connections": {
            "North": "Cafeteria",
            "East": "Guard Tower",
            "South": "Docks",
        },
        "item": None,
    },
    "Guard Tower": {
        "connections": {"West": "Recreation Yard"},
        "item": "wiring kit",
    },
    "Docks": {
        "connections": {
            "North": "Recreation Yard",
            "East": "Building 64",
        },
        "item": "engine",
    },
    "Building 64": {
        "connections": {
            "West": "Docks",
            "North": "Gondola Station",
        },
        "item": "flight gear",
    },
    "Gondola Station": {
        "connections": {
            "South": "Building 64",
            "North": "Roof",
        },
        "item": None,
    },
    "Roof": {
        "connections": {
            "South": "Gondola Station",
            "West": "Spiral Staircase",
        },
        "item": "propeller",
    },
    "Spiral Staircase": {
        "connections": {
            "East": "Roof",
            "South": "Citadel Tunnels",
        },
        "item": None,
    },
    "Citadel Tunnels": {
        "connections": {
            "North": "Spiral Staircase",
            "South": "Times Square",
            "East": "Wardens Office",
        },
        "item": None,
    },
    "Library": {
        "connections": {"West": "Times Square"},
        "item": "control valves",
    },
    "Infirmary": {
        "connections": {
            "East": "Times Square",
            "North": "Wardens Office",
        },
        "item": "navigation tools",
    },
    "Wardens Office": {
        "connections": {
            "South": "Infirmary",
            "West": "Citadel Tunnels",
        },
        "item": None,
    },
}
