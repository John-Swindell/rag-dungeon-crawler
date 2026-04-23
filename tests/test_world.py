from api.game.world import (
    MAP_AREA,
    MIN_ROOM_SIZE,
    ROOM_NAMES,
    START_ROOM,
    TOTAL_ITEMS,
    WARDEN_ROOM,
    build_rooms,
)


def test_build_rooms_generates_named_rooms_and_items():
    rooms = build_rooms(seed=42)

    assert set(rooms) == set(ROOM_NAMES)
    assert sum(1 for room in rooms.values() if room.item is not None) == TOTAL_ITEMS
    assert rooms[START_ROOM].item is None
    assert rooms[WARDEN_ROOM].item is None


def test_build_rooms_generates_valid_room_rects():
    for seed in range(25):
        rooms = build_rooms(seed=seed)

        for room in rooms.values():
            x, y = room.room_info.position
            width, height = room.room_info.size

            assert width >= MIN_ROOM_SIZE[0]
            assert height >= MIN_ROOM_SIZE[1]
            assert x >= 0
            assert y >= 0
            assert x + width <= MAP_AREA[0]
            assert y + height <= MAP_AREA[1]


def test_build_rooms_generates_connected_graph():
    rooms = build_rooms(seed=123)
    visited = set()
    stack = [START_ROOM]

    while stack:
        room_name = stack.pop()
        if room_name in visited:
            continue
        visited.add(room_name)
        stack.extend(rooms[room_name].connections.values())

    assert visited == set(rooms)


def test_connections_are_reciprocal():
    rooms = build_rooms(seed=987)

    for room in rooms.values():
        for target_name in room.connections.values():
            assert room.name in rooms[target_name].connections.values()


def test_maps_change_by_seed():
    first = build_rooms(seed=1)
    second = build_rooms(seed=2)

    first_layout = {
        name: (tuple(room.room_info.position), tuple(room.room_info.size), tuple(sorted(room.connections.items())))
        for name, room in first.items()
    }
    second_layout = {
        name: (tuple(room.room_info.position), tuple(room.room_info.size), tuple(sorted(room.connections.items())))
        for name, room in second.items()
    }

    assert first_layout != second_layout
