from api.models.game_state import Rect, Room, BSPNode
import random

CHARACTERS = ["Weasel", "Sal", "Billy", "Finn"]

TOTAL_ITEMS = 8
START_ROOM = "Cell"
BOSS_ROOM = "Wardens Office"

MAP_AREA = [800, 800]
MIN_ROOM_SIZE = [20, 20]
MAX_ROOM_SIZE = [40, 40]


def partition_node(node: BSPNode, min_size: int, iterations: int) -> None:
    """Recursively splits the nodes to generate the BSP tree"""
    if iterations == 0:
        return

    split_horiz = random.choice([True, False])
    if node.width > node.height * 1.25:
        split_horiz = False
    elif node.height > node.width * 1.25:
        split_horiz = True

    max_val = (node.height if split_horiz else node.width) - min_size
    if max_val <= min_size:
        return

    # actual split execution here
    split_point = random.randint(min_size, max_val)

    if split_horiz:
        node.left = BSPNode(node.x, node.y, node.width, split_point)
        node.right = BSPNode(node.x, node.y + split_point, node.width, node.height - split_point)
    else:
        node.left = BSPNode(node.x, node.y, split_point, node.height)
        node.right = BSPNode(node.x + split_point, node.y, node.width - split_point, node.height)

    if node.left and node.right:
        partition_node(node.left, min_size, iterations - 1)
        partition_node(node.right, min_size, iterations - 1)


def get_primary_leaf_name(node: BSPNode) -> str | None:
    """Helper function that fetches the name of the first available room in the node's space"""
    if node.is_leaf():
        return getattr(node, 'room_name', None)

    if node.left:
        return get_primary_leaf_name(node.left)
    if node.right:
        return get_primary_leaf_name(node.right)
    return None


def connect_nodes(node: BSPNode, rooms_dict: dict[str, Room]) -> None:
    """Recursively connects sibling nodes and translates into the compass directions"""
    if node.is_leaf():
        return

    # recurse bottom of tree first
    if node.left:
        connect_nodes(node.left, rooms_dict)
    if node.right:
        connect_nodes(node.right, rooms_dict)

    # connects siblings at curr level
    if node.left and node.right:
        cx1, cy1 = get_center(node.left)
        cx2, cy2 = get_center(node.right)

        room1_name = get_primary_leaf_name(node.left)
        room2_name = get_primary_leaf_name(node.right)

        if not room1_name or not room2_name:
            return

        # delta calc
        dx = cx2 - cx1
        dy = cy2 - cy1

        if abs(dx) > abs(dy):
            # horizontal connection
            dir_eswn = "East" if dx > 0 else "West"
            dir_wesn = "West" if dx > 0 else "East"
        else:
            # vertical connection
            dir_eswn = "South" if dy > 0 else "North"
            dir_wesn = "North" if dy > 0 else "South"

        rooms_dict[room1_name].connections[dir_eswn] = room2_name
        rooms_dict[room2_name].connections[dir_wesn] = room1_name


def get_center(node: BSPNode) -> tuple[int, int]:
    """Calculates the center of BSP node"""
    center_x = node.x + (node.width // 2)
    center_y = node.y + (node.height // 2)
    return center_x, center_y


def get_leaves(node: BSPNode) -> list[BSPNode]:
    """Additional helper to get leaf nodes directly during build"""
    if node.is_leaf(): return [node]
    return (get_leaves(node.left) if node.left else []) + (get_leaves(node.right) if node.right else [])


def build_rooms() -> dict[str, Room]:
    """
    Actual pipeline orchestrator for the whole BSP generation. 
    Internal functions use dataclasses, maps back to Pydantic models / boundaries
    See /api/models/game_state.py for relevant defs 
    """
    root = BSPNode(0, 0, MAP_AREA[0], MAP_AREA[1])

    partition_node(root, min_size=MIN_ROOM_SIZE[0], iterations=4)

    static_room_names = list(ROOM_DEFINITIONS.keys())
    generated_rooms_dict: dict[str, Room] = {}

    leaves = get_leaves(root)

    for i, leaf in enumerate(leaves):
        # if there are too many generated rooms, falls back to "Room_X" 
        room_name = static_room_names[i] if i < len(static_room_names) else f"Secret_Room_{i}"

        leaf.room_name = room_name

        item = ROOM_DEFINITIONS.get(room_name, {}).get("item", None)

        # Generates the room according to Pydantic spec - /api/models
        room_x = leaf.x + 20
        room_y = leaf.y + 20
        room_w = leaf.width - 40
        room_h = leaf.height - 40

        generated_rooms_dict[room_name] = Room(
            name=room_name,
            connections={},  # will be filled in from connect_nodes()
            item=item,
            room_info=Rect(position=[room_x, room_y], size=[room_w, room_h])
        )

    connect_nodes(root, generated_rooms_dict)

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
