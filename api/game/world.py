from __future__ import annotations

import math
import random
from collections.abc import Iterable

from api.models.game_state import BSPNode, Rect, Room

CHARACTERS = ["Weasel", "Sal", "Billy", "Finn"]

ITEMS = [
    "rigging",
    "fuel tank",
    "wiring kit",
    "engine",
    "flight gear",
    "propeller",
    "control valves",
    "navigation tools",
]

TOTAL_ITEMS = len(ITEMS)
START_ROOM = "Cell"
ROOF_ROOM = "Roof"
WARDEN_ROOM = "Wardens Office"
BOSS_ROOM = WARDEN_ROOM

MAP_AREA = [800, 800]
MIN_ROOM_SIZE = [44, 44]
MAX_ROOM_SIZE = [118, 118]
ROOM_PADDING = 10

DIRECTIONS: dict[str, tuple[int, int]] = {
    "North": (0, -1),
    "Northeast": (1, -1),
    "East": (1, 0),
    "Southeast": (1, 1),
    "South": (0, 1),
    "Southwest": (-1, 1),
    "West": (-1, 0),
    "Northwest": (-1, -1),
}

OPPOSITE_DIRECTIONS: dict[str, str] = {
    "North": "South",
    "Northeast": "Southwest",
    "East": "West",
    "Southeast": "Northwest",
    "South": "North",
    "Southwest": "Northeast",
    "West": "East",
    "Northwest": "Southeast",
}

ROOM_NAMES = [
    START_ROOM,
    "Michigan Avenue",
    "Broadway",
    "Times Square",
    "Showers",
    "Laundry Room",
    "Cafeteria",
    "Kitchen",
    "Recreation Yard",
    "Guard Tower",
    "Docks",
    "Building 64",
    "Gondola Station",
    ROOF_ROOM,
    "Spiral Staircase",
    "Citadel Tunnels",
    "Library",
    "Infirmary",
    WARDEN_ROOM,
]

# Kept for compatibility with older docs/tests. Connections are generated per session.
ROOM_DEFINITIONS: dict[str, dict] = {
    name: {"connections": {}, "item": None}
    for name in ROOM_NAMES
}


def _can_split_horizontally(node: BSPNode, min_leaf_height: int) -> bool:
    """Check whether a node can be divided into two valid child heights."""
    return node.height >= min_leaf_height * 2


def _can_split_vertically(node: BSPNode, min_leaf_width: int) -> bool:
    """Check whether a node can be divided into two valid child widths."""
    return node.width >= min_leaf_width * 2


def _split_node(
    node: BSPNode,
    min_leaf_width: int,
    min_leaf_height: int,
    rng: random.Random,
) -> bool:
    """Split one node into two children that can both still hold a room."""
    can_split_horizontally = _can_split_horizontally(node, min_leaf_height)
    can_split_vertically = _can_split_vertically(node, min_leaf_width)

    if not can_split_horizontally and not can_split_vertically:
        return False

    if can_split_horizontally and can_split_vertically:
        split_horizontally = rng.choice([True, False])
        if node.width > node.height * 1.25:
            split_horizontally = False
        elif node.height > node.width * 1.25:
            split_horizontally = True
    else:
        split_horizontally = can_split_horizontally

    if split_horizontally:
        split_point = rng.randint(min_leaf_height, node.height - min_leaf_height)
        node.left = BSPNode(node.x, node.y, node.width, split_point)
        node.right = BSPNode(node.x, node.y + split_point, node.width, node.height - split_point)
    else:
        split_point = rng.randint(min_leaf_width, node.width - min_leaf_width)
        node.left = BSPNode(node.x, node.y, split_point, node.height)
        node.right = BSPNode(node.x + split_point, node.y, node.width - split_point, node.height)

    return True


def get_leaves(node: BSPNode) -> list[BSPNode]:
    """Collect all leaf nodes from the current BSP tree."""
    if node.is_leaf():
        return [node]
    return (get_leaves(node.left) if node.left else []) + (get_leaves(node.right) if node.right else [])


def _generate_bsp_tree(target_leaf_count: int, rng: random.Random) -> tuple[BSPNode, list[BSPNode]]:
    """Split the map until there is one BSP leaf per named room."""
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

        leaf_to_split = max(
            splittable_leaves,
            key=lambda leaf: (leaf.width * leaf.height, rng.random()),
        )
        if not _split_node(leaf_to_split, min_leaf_width, min_leaf_height, rng):
            raise RuntimeError("Failed to split a BSP leaf that was marked splittable.")

        leaves = get_leaves(root)

    return root, leaves


def _build_room_rect(leaf: BSPNode, rng: random.Random) -> Rect:
    """Place a smaller randomized room inside its BSP leaf."""
    max_width = max(MIN_ROOM_SIZE[0], min(MAX_ROOM_SIZE[0], leaf.width - (ROOM_PADDING * 2)))
    max_height = max(MIN_ROOM_SIZE[1], min(MAX_ROOM_SIZE[1], leaf.height - (ROOM_PADDING * 2)))
    room_w = rng.randint(MIN_ROOM_SIZE[0], max_width)
    room_h = rng.randint(MIN_ROOM_SIZE[1], max_height)
    room_x = rng.randint(leaf.x + ROOM_PADDING, leaf.x + leaf.width - ROOM_PADDING - room_w)
    room_y = rng.randint(leaf.y + ROOM_PADDING, leaf.y + leaf.height - ROOM_PADDING - room_h)
    return Rect(position=[room_x, room_y], size=[room_w, room_h])


def _center(rect: Rect) -> tuple[float, float]:
    x, y = rect.position
    width, height = rect.size
    return x + (width / 2), y + (height / 2)


def room_center(room: Room) -> tuple[float, float]:
    """Return the center point for pathfinding and map rendering."""
    return _center(room.room_info)


def _distance(a: Rect, b: Rect) -> float:
    ax, ay = _center(a)
    bx, by = _center(b)
    return math.dist((ax, ay), (bx, by))


def _assign_room_names(leaves: list[BSPNode], rects: list[Rect], rng: random.Random) -> dict[str, Rect]:
    """Pin start/roof/warden to sensible areas, then shuffle the rest."""
    start_index = min(range(len(rects)), key=lambda index: sum(_center(rects[index])))
    roof_index = max(range(len(rects)), key=lambda index: _distance(rects[start_index], rects[index]))
    warden_index = max(
        (index for index in range(len(rects)) if index not in {start_index, roof_index}),
        key=lambda index: min(_distance(rects[index], rects[start_index]), _distance(rects[index], rects[roof_index])),
    )

    assignments: dict[int, str] = {
        start_index: START_ROOM,
        roof_index: ROOF_ROOM,
        warden_index: WARDEN_ROOM,
    }

    remaining_names = [name for name in ROOM_NAMES if name not in assignments.values()]
    rng.shuffle(remaining_names)

    for index in range(len(leaves)):
        if index not in assignments:
            assignments[index] = remaining_names.pop()
        leaves[index].room_name = assignments[index]

    return {assignments[index]: rects[index] for index in range(len(leaves))}


def _direction_candidates(source: Rect, target: Rect) -> list[str]:
    sx, sy = _center(source)
    tx, ty = _center(target)
    dx = tx - sx
    dy = ty - sy
    distance = math.hypot(dx, dy) or 1

    def score(direction: str) -> float:
        vx, vy = DIRECTIONS[direction]
        vector_distance = math.hypot(vx, vy)
        return ((dx / distance) * (vx / vector_distance)) + ((dy / distance) * (vy / vector_distance))

    return sorted(DIRECTIONS, key=score, reverse=True)


def _has_edge(connections: dict[str, dict[str, str]], source: str, target: str) -> bool:
    return target in connections[source].values()


def _add_connection(
    connections: dict[str, dict[str, str]],
    rects_by_name: dict[str, Rect],
    source: str,
    target: str,
) -> bool:
    """Add a reciprocal exit pair using the closest available compass labels."""
    if source == target or _has_edge(connections, source, target):
        return False

    for direction in _direction_candidates(rects_by_name[source], rects_by_name[target]):
        reverse_direction = OPPOSITE_DIRECTIONS[direction]
        if direction in connections[source] or reverse_direction in connections[target]:
            continue
        connections[source][direction] = target
        connections[target][reverse_direction] = source
        return True

    return False


def _nearest_room_pair(
    room_names: Iterable[str],
    connected_names: set[str],
    rects_by_name: dict[str, Rect],
) -> tuple[str, str]:
    best_pair: tuple[str, str] | None = None
    best_distance = math.inf

    for source in connected_names:
        for target in room_names:
            if target in connected_names:
                continue
            distance = _distance(rects_by_name[source], rects_by_name[target])
            if distance < best_distance:
                best_pair = (source, target)
                best_distance = distance

    if best_pair is None:
        raise RuntimeError("No room pair found while connecting generated map.")
    return best_pair


def _build_connections(rects_by_name: dict[str, Rect], rng: random.Random) -> dict[str, dict[str, str]]:
    """Build a connected map and keep the warden office as an avoidable side room."""
    connections = {name: {} for name in rects_by_name}
    playable_rooms = [name for name in rects_by_name if name != WARDEN_ROOM]
    connected_names = {START_ROOM}

    while len(connected_names) < len(playable_rooms):
        source, target = _nearest_room_pair(playable_rooms, connected_names, rects_by_name)
        if not _add_connection(connections, rects_by_name, source, target):
            raise RuntimeError(f"Failed to connect {source} to {target}.")
        connected_names.add(target)

    warden_neighbor = min(playable_rooms, key=lambda name: _distance(rects_by_name[WARDEN_ROOM], rects_by_name[name]))
    if not _add_connection(connections, rects_by_name, WARDEN_ROOM, warden_neighbor):
        raise RuntimeError("Failed to attach the Warden's Office to the map.")

    candidate_pairs = [
        (source, target)
        for index, source in enumerate(playable_rooms)
        for target in playable_rooms[index + 1 :]
        if not _has_edge(connections, source, target)
    ]
    rng.shuffle(candidate_pairs)
    candidate_pairs.sort(key=lambda pair: _distance(rects_by_name[pair[0]], rects_by_name[pair[1]]))

    extra_connection_count = max(4, len(playable_rooms) // 4)
    for source, target in candidate_pairs:
        if extra_connection_count <= 0:
            break
        if _add_connection(connections, rects_by_name, source, target):
            extra_connection_count -= 1

    return connections


def _assign_items(room_names: list[str], rng: random.Random) -> dict[str, str | None]:
    item_by_room = {room_name: None for room_name in room_names}
    eligible_rooms = [name for name in room_names if name not in {START_ROOM, WARDEN_ROOM}]
    item_rooms = rng.sample(eligible_rooms, TOTAL_ITEMS)
    items = [*ITEMS]
    rng.shuffle(items)

    for room_name, item in zip(item_rooms, items, strict=True):
        item_by_room[room_name] = item

    return item_by_room


def build_rooms(seed: int | None = None) -> dict[str, Room]:
    """Create a session-unique BSP map with generated exits and item placement."""
    rng = random.Random(seed)
    _, leaves = _generate_bsp_tree(len(ROOM_NAMES), rng)
    rects = [_build_room_rect(leaf, rng) for leaf in leaves]
    rects_by_name = _assign_room_names(leaves, rects, rng)
    connections = _build_connections(rects_by_name, rng)
    item_by_room = _assign_items(list(rects_by_name), rng)

    return {
        room_name: Room(
            name=room_name,
            connections=connections[room_name],
            item=item_by_room[room_name],
            room_info=rect,
        )
        for room_name, rect in rects_by_name.items()
    }
