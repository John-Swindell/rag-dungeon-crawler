from api.game.world import MAP_AREA, MIN_ROOM_SIZE, ROOM_DEFINITIONS, build_rooms


def test_build_rooms_preserves_static_graph_and_items():
    rooms = build_rooms()

    assert set(rooms) == set(ROOM_DEFINITIONS)

    for room_name, definition in ROOM_DEFINITIONS.items():
        room = rooms[room_name]
        assert room.connections == definition["connections"]
        assert room.item == definition["item"]


def test_build_rooms_generates_valid_room_rects():
    for _ in range(25):
        rooms = build_rooms()

        for room in rooms.values():
            x, y = room.room_info.position
            width, height = room.room_info.size

            assert width >= MIN_ROOM_SIZE[0]
            assert height >= MIN_ROOM_SIZE[1]
            assert x >= 0
            assert y >= 0
            assert x + width <= MAP_AREA[0]
            assert y + height <= MAP_AREA[1]
